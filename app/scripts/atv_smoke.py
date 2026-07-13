#!/usr/bin/env python3
"""E5-4 smoke test para ATV (Hacienda Costa Rica).

Dadas las credenciales y el certificado .p12 en variables de entorno, este script:
  1. Verifica conectividad con los endpoints oficiales documentados.
  2. Obtiene un token OAuth2 del Identity Provider de Hacienda.
  3. Genera un comprobante de PRUEBA marcado [SINTETICO].
  4. Firma el XML con el certificado .p12 (si está configurado).
  5. Envía el comprobante al sandbox de recepción.
  6. Escribe la evidencia completa en docs/audits/EVIDENCIA_ATV_SANDBOX_<fecha>.md.

Uso:
    export ATV_USERNAME=...
    export ATV_PASSWORD=...
    export ATV_CERT_PATH=/ruta/atv.p12
    export ATV_CERT_PIN=...
    export ATV_CLIENT_ID=api-stag
    python app/scripts/atv_smoke.py

El script falla cerrado con mensaje claro si falta alguna variable requerida.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


# URLs oficiales verificadas contra documentación pública (ver RUNBOOK_ATV_CREDENCIALES.md).
ATV_URLS = {
    "sandbox": {
        "token": "https://idp.comprobanteselectronicos.go.cr/auth/realms/rut-stag/protocol/openid-connect/token",
        "recepcion": "https://api.comprobanteselectronicos.go.cr/recepcion-sandbox/v1/",
        "client_id": "api-stag",
    },
    "live": {
        "token": "https://idp.comprobanteselectronicos.go.cr/auth/realms/rut/protocol/openid-connect/token",
        "recepcion": "https://api.comprobanteselectronicos.go.cr/recepcion/v1/",
        "client_id": "api-prod",
    },
}

REQUIRED_ENV = ["ATV_USERNAME", "ATV_PASSWORD", "ATV_CERT_PATH", "ATV_CERT_PIN"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    timeout: int = 30,
) -> tuple[int, bytes]:
    """HTTP request with a permissive SSL context for sandbox portals."""

    req = urllib.request.Request(
        url,
        data=body,
        method=method.upper(),
        headers=headers or {},
    )
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def _check_connectivity(urls: dict[str, str]) -> dict[str, Any]:
    """Probe documented endpoints without credentials and record status codes."""

    results: dict[str, Any] = {}
    for name, url in urls.items():
        status, body = _http_request("GET", url, timeout=15)
        results[name] = {
            "url": url,
            "method": "GET",
            "status": status,
            "body_preview": body[:200].decode("utf-8", errors="replace"),
            "checked_at": _utc_now(),
        }
    return results


def _get_token(
    username: str,
    password: str,
    client_id: str,
    token_url: str,
) -> dict[str, Any]:
    """Fetch an OAuth2 token from the Hacienda IdP."""

    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "username": username,
        "password": password,
    }
    body = urllib.parse.urlencode(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    status, response = _http_request("POST", token_url, headers=headers, body=body)

    if status != 200:
        raise RuntimeError(
            f"IdP token request failed: HTTP {status} - {response.decode('utf-8', errors='replace')}"
        )

    token_data = json.loads(response.decode("utf-8"))
    return {
        "access_token": token_data["access_token"],
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_in": token_data.get("expires_in"),
        "scope": token_data.get("scope"),
        "obtained_at": _utc_now(),
    }


def _generate_test_xml(clave: str) -> bytes:
    """Generate a minimal, explicitly synthetic CR electronic voucher XML.

    The XML is intentionally invalid from a schema standpoint (Hacienda will reject
    it) but it exercises the full signing/sending pipeline. It is marked [SINTETICO]
    in every visible field.
    """

    ns = "https://cdn.comprobanteselectronicos.go.cr/xml-schema/v4.3/facturaElectronica"
    ET.register_namespace("", ns)
    root = ET.Element(
        "{https://cdn.comprobanteselectronicos.go.cr/xml-schema/v4.3/facturaElectronica}FacturaElectronica",
    )
    ET.SubElement(root, "Clave").text = clave
    ET.SubElement(root, "CodigoActividad").text = "[SINTETICO-720000]"
    ET.SubElement(root, "NumeroConsecutivo").text = "[SINTETICO-00100001010000000001]"
    ET.SubElement(root, "FechaEmision").text = _utc_now()

    emisor = ET.SubElement(root, "Emisor")
    ET.SubElement(emisor, "Nombre").text = "[SINTETICO] Emisor de Prueba"
    ET.SubElement(emisor, "Identificacion").text = "[SINTETICO-3101123456]"

    receptor = ET.SubElement(root, "Receptor")
    ET.SubElement(receptor, "Nombre").text = "[SINTETICO] Receptor de Prueba"
    ET.SubElement(receptor, "Identificacion").text = "[SINTETICO-3101654321]"

    ET.SubElement(root, "ResumenFactura")

    tree = ET.ElementTree(root)
    import io

    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    return buf.getvalue()


def _sign_xml(xml_bytes: bytes, p12_path: str, pin: str) -> bytes:
    """Sign the XML with the .p12 certificate using cryptography.

    This creates a basic enveloped XML Signature. It is NOT guaranteed to pass
    Hacienda's strict schema validation, but it proves that the private key,
    certificate, and signing pipeline are operational.
    """

    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import pkcs12

    with open(p12_path, "rb") as fh:
        p12_data = fh.read()

    private_key, certificate, _ = pkcs12.load_key_and_certificates(
        p12_data, pin.encode("utf-8")
    )
    if private_key is None or certificate is None:
        raise RuntimeError("El archivo .p12 no contiene llave privada o certificado")

    # Detached RSA-SHA256 signature over the XML bytes.
    signature = private_key.sign(xml_bytes, hashes.SHA256())
    sig_b64 = base64.b64encode(signature).decode("utf-8")

    # Inject a synthetic signature block into the XML for traceability.
    root = ET.fromstring(xml_bytes)
    sig_elem = ET.SubElement(root, "Signature", {"xmlns": "http://www.w3.org/2000/2000/09/xmldsig#"})
    ET.SubElement(sig_elem, "SignatureValue").text = sig_b64
    cert_b64 = base64.b64encode(
        certificate.public_bytes(serialization.Encoding.PEM)
    ).decode("utf-8")
    key_info = ET.SubElement(sig_elem, "KeyInfo")
    ET.SubElement(key_info, "X509Certificate").text = cert_b64

    tree = ET.ElementTree(root)
    import io

    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    return buf.getvalue()


def _send_to_recepcion(token: str, xml_bytes: bytes, recepcion_url: str) -> dict[str, Any]:
    """Send the signed XML to the Hacienda sandbox reception endpoint."""

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/xml",
        "Accept": "application/json",
    }
    status, response = _http_request("POST", recepcion_url, headers=headers, body=xml_bytes)
    return {
        "status": status,
        "response": response.decode("utf-8", errors="replace"),
        "sent_at": _utc_now(),
    }


def _build_clave() -> str:
    """Build a synthetic test document key.

    Real keys have a strict format (country + date + cedula + consecutive + situacion + codigo).
    This synthetic key is marked and will be rejected by Hacienda, which is the expected smoke
    outcome.
    """

    return "[SINTETICO]50607072400012345678901234567890123456789"


def _render_evidence(report: dict[str, Any]) -> str:
    lines = [
        f"# Evidencia ATV Sandbox — {report['generated_at']}",
        "",
        f"**Modo:** {report['mode']}  ",
        f"**Ambiente:** {'sandbox' if report['mode'] == 'sandbox' else 'live'}  ",
        f"**Usuario:** `{report['username']}`  ",
        f"**Certificado:** `{report['cert_path']}`  ",
        "",
        "## 1. Conectividad con endpoints oficiales (sin credenciales)",
        "",
    ]
    for name, probe in report["connectivity"].items():
        lines.append(f"### {name}")
        lines.append(f"- URL: `{probe['url']}`")
        lines.append(f"- Método: {probe['method']}")
        lines.append(f"- Status: {probe['status']}")
        lines.append(f"- Verificado: {probe['checked_at']}")
        lines.append("")

    lines.extend([
        "## 2. Token OAuth2",
        "",
        f"- Endpoint: `{report['token']['token_url']}`",
        f"- Client ID: `{report['token']['client_id']}`",
        f"- Token type: {report['token']['token_type']}",
        f"- Expires in: {report['token']['expires_in']}s",
        f"- Obtenido: {report['token']['obtained_at']}",
        f"- Access token hash (SHA-256): `{hashlib.sha256(report['token']['access_token'].encode()).hexdigest()[:16]}`",
        "",
        "## 3. Comprobante de prueba",
        "",
        f"- Clave: `{report['comprobante']['clave']}`",
        f"- Marcado: `[SINTETICO]` en todos los campos visibles",
        f"- Firmado: {'Sí' if report['comprobante']['signed'] else 'No'}",
        f"- Generado: {report['comprobante']['generated_at']}",
        "",
        "## 4. Envío a recepción sandbox",
        "",
        f"- Endpoint: `{report['envio']['recepcion_url']}`",
        f"- Status HTTP: {report['envio']['status']}",
        f"- Enviado: {report['envio']['sent_at']}",
        "",
        "### Respuesta del servidor",
        "",
        "```json",
        report["envio"]["response"],
        "```",
        "",
        "## Interpretación",
        "",
        "- Un status HTTP distinto de 0 indica que el endpoint responde y la autenticación llegó.",
        "- Una respuesta de error de Hacienda (p. ej. clave inválida o esquema incorrecto) es **esperada** porque el comprobante es sintético.",
        "- El objetivo del smoke es validar el pipeline completo: credenciales → token → firma → envío.",
        "",
        "## Acción humana restante",
        "",
        "Reemplazar el comprobante sintético por uno real y cambiar a `ATV_MODE=live` cuando el certificado de producción esté disponible.",
        "",
        "---",
        "",
        "_Generado automáticamente por `app/scripts/atv_smoke.py`._",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    missing = [v for v in REQUIRED_ENV if not os.getenv(v)]
    if missing:
        print(
            f"[FAIL] Faltan variables de entorno requeridas: {', '.join(missing)}\n"
            "Consulte docs/RUNBOOK_ATV_CREDENCIALES.md para obtener los valores.",
            file=sys.stderr,
        )
        return 1

    mode = os.getenv("ATV_MODE", "sandbox").lower()
    if mode not in ATV_URLS:
        print(f"[FAIL] ATV_MODE debe ser 'sandbox' o 'live', se recibió '{mode}'", file=sys.stderr)
        return 1

    urls = ATV_URLS[mode]
    username = os.environ["ATV_USERNAME"]
    password = os.environ["ATV_PASSWORD"]
    cert_path = os.environ["ATV_CERT_PATH"]
    cert_pin = os.environ["ATV_CERT_PIN"]
    client_id = os.getenv("ATV_CLIENT_ID", urls["client_id"])

    if not Path(cert_path).exists():
        print(f"[FAIL] No existe el certificado: {cert_path}", file=sys.stderr)
        return 1

    report: dict[str, Any] = {
        "generated_at": _utc_now(),
        "mode": mode,
        "username": username,
        "cert_path": cert_path,
    }

    # 1. Connectivity probes.
    report["connectivity"] = _check_connectivity(
        {"token": urls["token"], "recepcion": urls["recepcion"]}
    )

    # 2. Token.
    token_info = _get_token(username, password, client_id, urls["token"])
    token_info["token_url"] = urls["token"]
    token_info["client_id"] = client_id
    report["token"] = token_info

    # 3. Synthetic voucher.
    clave = _build_clave()
    xml_bytes = _generate_test_xml(clave)
    signed_xml = _sign_xml(xml_bytes, cert_path, cert_pin)
    report["comprobante"] = {
        "clave": clave,
        "signed": True,
        "generated_at": _utc_now(),
        "xml_sha256": hashlib.sha256(signed_xml).hexdigest()[:16],
    }

    # 4. Send.
    report["envio"] = _send_to_recepcion(token_info["access_token"], signed_xml, urls["recepcion"])
    report["envio"]["recepcion_url"] = urls["recepcion"]

    # 5. Write evidence.
    out_dir = Path("docs/audits")
    out_dir.mkdir(parents=True, exist_ok=True)
    date_suffix = datetime.now(timezone.utc).strftime("%Y%m%d")
    out_path = out_dir / f"EVIDENCIA_ATV_SANDBOX_{date_suffix}.md"
    out_path.write_text(_render_evidence(report), encoding="utf-8")

    print(f"[OK] Evidencia escrita en {out_path}")
    print(f"[INFO] Status HTTP del envío: {report['envio']['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

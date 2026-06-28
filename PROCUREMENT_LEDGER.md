Id
PROCUREMENT_LEDGER

Version
1

Status
VIGENTE

Visibility
CEO-ONLY

Domain
GOBERNANZA

Stamp
VIGENTE — 2026-06-27

PROCUREMENT_LEDGER — SpaceLoom Etapa 1
Registro único de dependencias del mundo real (datos, certificados, cuentas, credenciales) que no se pueden generar en código. Regla del CLOSER LOOP §9: ninguna de estas frena el cierre interno. Cada hito code-cierra con su fallback; el ítem PROCURE es una compra/gestión puntual posterior. Costos = estimados a confirmar ([CONFIRMAR PRECIO]). No inventar cifras finales. Distinción clave: cierre dogfood interno (D4) NO depende de ningún PROCURE. Los PROCURE solo desbloquean distribución externa y completar datos reales.

Resumen
ID	Hito	Qué se necesita	Bloquea	Fallback en código	Prioridad
PRC-01	SL1b	Datos comerciales reales (precios, márgenes, MOQ, tallas, SKUs) en ENT_COMERCIAL_*	Drafts fully_sourced	Draft corre con [PENDIENTE — NO INVENTAR]	Alta
PRC-02	SL2a/b/c	Corpus real de documentos fuente (MD/TXT/CSV/XLSX/PDF) con procedencia verificable	Test de cita end-to-end con dato real	Fixtures sintéticos con fuente conocida	Media
PRC-03	SL3b/c	Sesiones de uso real (dogfood) para evidenciar que edit_pct baja	Gold loop "real" (vs mecánico)	Sesiones sembradas/simuladas para el test del mecanismo	Media
PRC-04	SL3.5	Dataset confidencial real para test de fuga cross-workspace = 0	Validación de fuga con datos reales	Canaries sintéticos marcados confidential=true	Media
PRC-05	SL4	Certificado de firma de código Windows (Authenticode OV/EV)	.exe firmado / SmartScreen limpio	Self-signed fallback: `app/src/packaging.py::sign_executable_windows`, `app/src/installer.py::SELF_SIGNED_WARNING`, `app/build.py --sign`	Alta (solo distribución)
PRC-06	SL4	Apple Developer Program + Developer ID + notarización Mac	Build Mac distribuible sin warning	Mac no notarizado/diferido: `app/src/packaging.py::generate_dmg_script_macos`; Mac fuera del scope D4 de Etapa 1	Media (solo distribución)
PRC-07	SL4	Llave de firma para auto-update (cadena de confianza publicable)	Auto-update firmado verificado externamente	Self-signed fallback: `app/src/update.py` Ed25519 + pinned-key + rollback + `app/tests/test_sl1b_kb_drafts.py::test_auto_update_sign_verify_and_rollback`	Alta (solo distribución)
PRC-08	D2	Registro de marca "SpaceLoom" / "FaberLoom"	Uso de ® / defensa legal	Uso de ™ (sin registro)	Baja
PRC-09	SL5 (DIFERIDO)	Credenciales IMAP/SMTP rotadas + registro OAuth app (Google/Microsoft)	Connector de correo real	Connector tras email_connector_enabled=false	Diferida
Detalle por ítem
PRC-01 — Datos comerciales reales (SL1b) · Prioridad ALTA
Qué: valores reales para poblar ENT_COMERCIAL_*: precios PARTNER_B2B, márgenes, MOQ, condiciones de pago/entrega/devolución, tallas y SKUs vigentes de Rana Walk.
Por qué bloquea: sin esto, los 10 drafts de SL1b salen con [PENDIENTE]; el harness cierra igual pero los drafts no son fully_sourced.
Fallback activo: el draft marca [PENDIENTE — NO INVENTAR] y source_to_field_check lo refleja como unsourced. SL1b cierra igual (gate = harness + 10 logueados, no completitud).
Owner: CEO / Comercial. Costo: $0 (gestión interna, no compra).
Estado: ABIERTO. Entregable: un batch para ENT_COMERCIAL_* vía sync_*_indexa.ps1.
PRC-02 — Corpus real de documentos fuente (SL2a/b/c) · Prioridad MEDIA
Qué: un set pequeño de documentos reales (MD/TXT/CSV/XLSX/PDF) con procedencia conocida, para el test de cita con fuente real end-to-end.
Por qué bloquea: el test end-to-end de cita necesita una fuente real trazable (campo → documento → sección).
Fallback activo: fixtures sintéticos con fuente conocida; valida el mecanismo de cita y stale_data_block sin datos reales. SL2 cierra con fixtures.
Owner: CEO / Ops. Costo: $0.
Estado: ABIERTO.
PRC-03 — Sesiones de uso real (SL3b/c) · Prioridad MEDIA
Qué: uso real repetido (dogfood) suficiente para mostrar tendencia descendente de edit_pct.
Por qué bloquea: el "gold loop real" requiere datos de uso a lo largo del tiempo; no se fabrica.
Fallback activo: sesiones sembradas/simuladas que prueben que el feedback re-alimenta el loop (mecanismo conectado). SL3b/c cierra probando el mecanismo, no la madurez subjetiva.
Owner: CEO (uso) + ejecutor (instrumentación). Costo: $0 (tiempo de uso).
Estado: ABIERTO.
PRC-04 — Dataset confidencial real (SL3.5) · Prioridad MEDIA
Qué: datos reales marcados confidential=true para el test de fuga cross-workspace = 0 bajo SQLCipher.
Nota: SQLCipher Community Edition es libre/gratuito → no es compra. El PROCURE es el dato real, no la librería. (Solo si se exige FIPS/SEE habría licencia comercial → [CONFIRMAR si se requiere].)
Fallback activo: canaries sintéticos confidential=true; test de fuga = 0 corre en modo normal y cifrado sin datos reales. SL3.5 cierra con canaries.
Owner: CEO. Costo: $0 (Community Edition).
Estado: ABIERTO.
PRC-05 — Certificado de firma de código Windows (SL4) · Prioridad ALTA (solo distribución)
Qué: certificado Authenticode (OV o EV) para firmar SpaceLoom.exe y el instalador; evita warnings de SmartScreen.
Por qué bloquea: solo bloquea distribución externa a no técnicos. No bloquea dogfood interno (D4).
Fallback activo: build con firma self-signed + aviso documentado en el instalador. SL4 code-cierra con fallback.
Trazabilidad fallback SL4:
  - Certificado self-signed: `app/src/packaging.py::generate_self_signed_code_signing_cert`
  - Firma del ejecutable: `app/src/packaging.py::sign_executable_windows`
  - Verificación de firma: `app/src/packaging.py::verify_executable_signature`
  - Orquestación build: `app/build.py --sign`
  - Aviso en instalador: `app/src/installer.py::SELF_SIGNED_WARNING`
  - Test de contrato: `app/tests/test_sl4_packaging.py::test_smoke_signed_executable`
Vendors: DigiCert / Sectigo / SSL.com. Costo: [CONFIRMAR PRECIO] (orden de cientos de USD/año; EV más caro que OV).
Owner: CEO. Estado: ABIERTO (trazado — fallback SL4 verificado; gatillar solo al pasar a distribuible).
PRC-06 — Apple Developer + notarización Mac (SL4) · Prioridad MEDIA (solo distribución)
Qué: Apple Developer Program + certificado Developer ID Application + flujo de notarización para build Mac.
Por qué bloquea: solo distribución Mac sin warning de Gatekeeper.
Fallback activo: empaque Mac sin notarizar para uso interno; o diferir target Mac en Etapa 1.
Trazabilidad fallback SL4:
  - Generador de script DMG no notarizado: `app/src/packaging.py::generate_dmg_script_macos`
  - Decisión de alcance: Mac se difería en Etapa 1; el cierre D4 se hace sobre Windows.
Costo: Apple Developer [CONFIRMAR PRECIO] (~tarifa anual estándar). Owner: CEO.
Estado: ABIERTO (trazado — Mac no es obligatorio para D4; gatillar solo si Mac entra en distribución).
PRC-07 — Llave de firma para auto-update (SL4) · Prioridad ALTA (solo distribución)
Qué: par de llaves + cadena de confianza publicable para firmar y verificar paquetes de auto-update.
Fallback activo: auto-update verificado contra llave self-signed local; el mecanismo de verificación de firma queda probado. SL4 cierra con fallback.
Trazabilidad fallback SL4:
  - Generación de llaves Ed25519: `app/src/update.py::generate_keypair`
  - Firma/verificación de manifest: `app/src/update.py::create_update_manifest` / `verify_update_manifest`
  - Verificación con pinned public key: `app/src/update.py::_TRUSTED_PUBLIC_KEYS` / `set_trusted_public_keys`
  - Rollback de binario: `app/src/update.py::install_update` / `rollback` / `.spaceloom_rollback`
  - Tests de contrato: `app/tests/test_sl1b_kb_drafts.py::test_auto_update_sign_verify_and_rollback`, `app/tests/test_sl4_packaging.py::test_signed_update_manifest_roundtrip`, `app/tests/test_sl4_packaging.py::test_check_for_update_smoke`
Costo: $0 si self-managed; ligado a PRC-05 si se usa la cadena del cert comercial.
Owner: CEO + ejecutor. Estado: ABIERTO (trazado — fallback SL4 verificado).
PRC-08 — Registro de marca (D2) · Prioridad BAJA
Qué: registro de "SpaceLoom" / "FaberLoom" ante la oficina de marcas correspondiente.
Fallback activo: uso de ™ (no ®) en producto y LICENSE.md/NOTICE. No bloquea ningún cierre técnico.
Costo: [CONFIRMAR PRECIO] (tasa de registro por jurisdicción). Owner: CEO / legal.
Estado: ABIERTO (no urgente).
PRC-09 — Credenciales y OAuth de correo (SL5 — DIFERIDO) · Prioridad DIFERIDA
Qué: credenciales IMAP/SMTP rotadas + registro de OAuth app (Google Cloud / Microsoft Azure) para el connector de correo.
Estado por D3: SL5 DIFERIDO de Etapa 1. El connector queda tras email_connector_enabled=false, soportado en backend, fuera del surface.
Fallback activo: flag apagado; no se ejecuta envío real. No cuenta para el cierre de Etapa 1.
Costo: $0 (las plataformas OAuth son gratuitas; el costo es gestión de credenciales). Owner: CEO.
Estado: DIFERIDO (no gatillar salvo override de D3).
Reglas del ledger
Un ítem por dependencia. No duplicar; no acumular efímeros (CLOSER LOOP §9.3).
Cada ítem tiene fallback activo que permite code-cerrar su hito. Si no lo tiene, no es PROCURE: es un blocker real y se escala al CEO.
El cierre dogfood interno (D4) no depende de este ledger. Solo PRC-05/06/07 (distribución) y PRC-01 (datos) afectan calidad/alcance externo.
Al resolver un ítem: cambiar estado a RESUELTO, anotar fecha y entregable, y reflejarlo en ENT_GOB_PENDIENTES.

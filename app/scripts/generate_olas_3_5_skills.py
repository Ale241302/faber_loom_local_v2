#!/usr/bin/env python3
"""Genera los SKILL_*.md de olas 3-5 sin inventar datos.

Fuente: ENT_FB_SKILL_CATALOG_v1.md (Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md).
Regla de 3 niveles:
  - NIVEL A -> SHADOW   (ya existen PACK 1/3 y skills legacy; no se regeneran aquí).
  - NIVEL B -> DRAFT    (template robable, falta localización LATAM + golden cases).
  - NIVEL C -> DEFINITION_PENDING (GAP; ni siquiera se define alcance).

Este script no contiene dominio inventado: solo IDs, nombres derivados del catálogo
y marcadores [PENDIENTE — NO INVENTAR].
"""

from __future__ import annotations

from pathlib import Path

DRAFT_MARKER = "[PENDIENTE — NO INVENTAR]"


def _id_to_name(skill_id: str) -> str:
    """Nombre legible derivado del ID; sin inventar dominio."""

    names: dict[str, str] = {
        # Ola 3 - comex (GAP -> DEFINITION_PENDING)
        "SKILL_CX_DOC_COMPLETENESS": "Verificación de documentación de embarque",
        "SKILL_CX_PEDIMENTO_CROSSCHECK": "Cruce de pedimento aduanero",
        "SKILL_CX_LANDED_COST": "Cálculo de landed cost",
        "SKILL_CX_HS_CLASSIFY": "Clasificación HS de productos",
        "SKILL_CX_DUTY_CALC": "Cálculo de aranceles e impuestos de importación",
        "SKILL_CX_ORIGIN_CHECK": "Verificación de origen y tratados",
        "SKILL_CX_REQUISITOS_PREVIOS": "Requisitos previos de importación",
        "SKILL_CX_REG_WATCH": "Vigilancia regulatoria de comercio exterior",
        "SKILL_CX_DISPUTE_PACK": "Paquete de disputas aduaneras",
        "SKILL_CX_EMBARQUE_TRACK": "Seguimiento de embarque en tránsito",
        # Ola 4 - planilla (GAP)
        "SKILL_PL_PREP": "Preparación de planilla",
        "SKILL_PL_RECTIFICACION": "Rectificación de planilla",
        "SKILL_PL_CARGAS_VALIDATE": "Validación de cargas sociales",
        # Ola 4 - tributario (mixto)
        "SKILL_TR_DECLARACION_INFO": "Preparación informativa de declaraciones tributarias",
        "SKILL_TR_RETENCION_CERT": "Certificado de retenciones",
        "SKILL_TR_TRAMITE_TRACK": "Seguimiento de trámites tributarios",
        "SKILL_TR_PERMISOS_CAL": "Calendario de permisos y patentes",
        "SKILL_TR_TIPO_CAMBIO_ADJ": "Ajuste por tipo de cambio",
        # Ola 4 - whatsapp formal (mixto)
        "SKILL_WA_CLASSIFY_ROUTE": "Clasificación y ruteo de mensajes WhatsApp",
        "SKILL_WA_ORDER_CAPTURE": "Captura de pedidos por WhatsApp",
        "SKILL_WA_AGREEMENT_CAPTURE": "Captura de acuerdos por WhatsApp",
        # Ola 4 - bodega importación (GAP)
        "SKILL_BO_RECEPCION_MATCH": "Reconciliación de recepción de mercancía",
        "SKILL_BO_DEVOLUCION_NC": "Devoluciones y notas de crédito de inventario",
        "SKILL_BO_STOCK_DISPONIBLE": "Consulta de stock disponible",
        # Ola 5 - comercial (mixto)
        "SKILL_CM_ACCOUNT_BRIEF": "Resumen de cuenta comercial",
        "SKILL_CM_CALL_CAPTURE": "Captura de llamadas comerciales",
        "SKILL_CM_CARTERA_PRIORITIZE": "Priorización de cartera comercial",
        "SKILL_CM_REORDER_PREDICT": "Predicción de recompra",
        # Ola 5 - servicio (TEMPLATE)
        "SKILL_SV_TRIAGE": "Triage de tickets de servicio",
        "SKILL_SV_RESPUESTA": "Respuesta a tickets de servicio",
        "SKILL_SV_ESCALACION": "Escalación de servicio",
        "SKILL_SV_TEMAS": "Temas y pulso de servicio",
        "SKILL_SV_GARANTIA_DEVOLUCION": "Garantías y devoluciones",
        # Ola 5 - finanzas cierre (TEMPLATE)
        "SKILL_FI_CIERRE_NARRADO": "Cierre narrado",
        "SKILL_FI_ASIENTOS": "Asientos contables",
        "SKILL_FI_VARIACIONES": "Análisis de variaciones",
        "SKILL_FI_EEFF": "Estados financieros",
        # Ola 5 - legal (mixto)
        "SKILL_LG_NDA_TRIAGE": "Triage de NDAs",
        "SKILL_LG_CONTRATO_REVIEW": "Revisión de contratos",
        "SKILL_LG_VENCIMIENTOS": "Vencimientos contractuales",
        "SKILL_LG_PREFIRMA": "Pre-firma de contratos",
        "SKILL_LG_VIGENCIA_NORMA": "Vigencia normativa",
        # Ola 5 - gerencia (TEMPLATE)
        "SKILL_GE_PULSO": "Pulso gerencial",
        "SKILL_GE_BRIEF_RECURRENTE": "Brief recurrente",
        "SKILL_GE_QBR": "Quarterly business review",
        "SKILL_GE_RIESGOS": "Riesgos gerenciales",
        # Ola 5 - operaciones / marketing / rrhh (TEMPLATE)
        "SKILL_OP_SOP": "Procedimientos operativos",
        "SKILL_OP_STATUS": "Reporte de estado operativo",
        "SKILL_OP_PROVEEDOR_EVAL": "Evaluación de proveedores",
        "SKILL_MK_CAMPANA": "Planificación de campañas",
        "SKILL_MK_CONTENIDO_VOZ": "Contenido con voz de marca",
        "SKILL_MK_BRAND_AUDIT": "Auditoría de marca",
        "SKILL_HR_CONTRATACION": "Contratación y código de trabajo",
    }
    return names.get(skill_id, skill_id.replace("_", " ").title())


def _domain_for_pack(pack_id: str) -> str:
    return {
        "wtp_comex": "COMEX",
        "wtp_planilla": "PLANILLA",
        "wtp_tributario": "TRIBUTARIO",
        "wtp_whatsapp_formal": "WHATSAPP",
        "wtp_bodega_importacion": "BODEGA",
        "wtp_comercial": "COMERCIAL",
        "wtp_servicio": "SERVICIO",
        "wtp_finanzas_cierre": "FINANZAS",
        "wtp_legal": "LEGAL",
        "wtp_gerencia": "GERENCIA",
        "wtp_operaciones": "OPERACIONES",
        "wtp_marketing": "MARKETING",
        "wtp_rrhh": "RRHH",
    }.get(pack_id, "GENERAL")


def _description(status: str) -> str:
    if status == "DRAFT":
        return (
            f"Skill en estado DRAFT. Estructura de template disponible; requiere "
            f"localización LATAM, conectores reales y golden cases validados antes de promover. "
            f"{DRAFT_MARKER}"
        )
    return (
        f"Skill en estado DEFINITION_PENDING. El alcance, entradas, conectores y "
        f"golden cases aún no han sido definidos. {DRAFT_MARKER}"
    )


def _outcome(status: str) -> str:
    return (
        "ready_when_golden_cases_verified"
        if status == "DRAFT"
        else "definition_pending"
    )


def _body(skill_id: str, status: str, name: str) -> str:
    if status == "DRAFT":
        pendientes = (
            "- Localizar template a contexto LATAM (NIIF, derecho civil, Código de Trabajo).\n"
            "- Definir tool allowlist y conectores reales.\n"
            "- Reemplazar placeholders por golden cases reales validados."
        )
    else:
        pendientes = (
            "- Definir alcance, entradas y salidas del skill.\n"
            "- Identificar conectores y fuentes de evidencia.\n"
            "- Diseñar golden cases con datos reales del tenant."
        )
    return (
        f"# {name}\n\n"
        f"**ID:** `{skill_id}`\n\n"
        f"**Estado:** {status}\n\n"
        f"{('Estructura de template disponible; requiere localización LATAM y golden cases reales.' if status == 'DRAFT' else 'GAP sin definición de alcance; no se ejecuta hasta que se especifique.')}\n\n"
        f"## Pendientes explícitos\n\n"
        f"{pendientes}\n\n"
        f"*{DRAFT_MARKER}*\n"
    )


def _skill_md(skill_id: str, status: str, pack_id: str) -> str:
    name = _id_to_name(skill_id)
    domain = _domain_for_pack(pack_id)
    description = _description(status)
    outcome = _outcome(status)
    body = _body(skill_id, status, name)
    return f"""---
name: "{name}"
description: "{description}"
version: "0.1.0"
metadata:
  fbl:
    id: "{skill_id}"
    type: "agent"
    architectural_archetype: "generator"
    archetype: "generator"
    domain: "{domain}"
    visibility: "INTERNAL"
    status: "{status}"
    pack_id: "{pack_id}"
    contract:
      outputs:
        - id: "primary_decision"
          kind: "decision"
          required: true
    outcome:
      primary: "{outcome}"
    tenant_scope:
      mode: "single"
---

{body}"""


SKILLS: list[tuple[str, str, str]] = [
    # (skill_id, status, pack_id)
    # Ola 3
    ("SKILL_CX_DOC_COMPLETENESS", "DEFINITION_PENDING", "wtp_comex"),
    ("SKILL_CX_PEDIMENTO_CROSSCHECK", "DEFINITION_PENDING", "wtp_comex"),
    ("SKILL_CX_LANDED_COST", "DEFINITION_PENDING", "wtp_comex"),
    ("SKILL_CX_HS_CLASSIFY", "DEFINITION_PENDING", "wtp_comex"),
    ("SKILL_CX_DUTY_CALC", "DEFINITION_PENDING", "wtp_comex"),
    ("SKILL_CX_ORIGIN_CHECK", "DEFINITION_PENDING", "wtp_comex"),
    ("SKILL_CX_REQUISITOS_PREVIOS", "DEFINITION_PENDING", "wtp_comex"),
    ("SKILL_CX_REG_WATCH", "DEFINITION_PENDING", "wtp_comex"),
    ("SKILL_CX_DISPUTE_PACK", "DEFINITION_PENDING", "wtp_comex"),
    ("SKILL_CX_EMBARQUE_TRACK", "DEFINITION_PENDING", "wtp_comex"),
    # Ola 4
    ("SKILL_PL_PREP", "DEFINITION_PENDING", "wtp_planilla"),
    ("SKILL_PL_RECTIFICACION", "DEFINITION_PENDING", "wtp_planilla"),
    ("SKILL_PL_CARGAS_VALIDATE", "DEFINITION_PENDING", "wtp_planilla"),
    ("SKILL_TR_DECLARACION_INFO", "DRAFT", "wtp_tributario"),
    ("SKILL_TR_RETENCION_CERT", "DEFINITION_PENDING", "wtp_tributario"),
    ("SKILL_TR_TRAMITE_TRACK", "DEFINITION_PENDING", "wtp_tributario"),
    ("SKILL_TR_PERMISOS_CAL", "DRAFT", "wtp_tributario"),
    ("SKILL_TR_TIPO_CAMBIO_ADJ", "DEFINITION_PENDING", "wtp_tributario"),
    ("SKILL_WA_CLASSIFY_ROUTE", "DRAFT", "wtp_whatsapp_formal"),
    ("SKILL_WA_ORDER_CAPTURE", "DEFINITION_PENDING", "wtp_whatsapp_formal"),
    ("SKILL_WA_AGREEMENT_CAPTURE", "DEFINITION_PENDING", "wtp_whatsapp_formal"),
    ("SKILL_BO_RECEPCION_MATCH", "DEFINITION_PENDING", "wtp_bodega_importacion"),
    ("SKILL_BO_DEVOLUCION_NC", "DEFINITION_PENDING", "wtp_bodega_importacion"),
    ("SKILL_BO_STOCK_DISPONIBLE", "DEFINITION_PENDING", "wtp_bodega_importacion"),
    # Ola 5
    ("SKILL_CM_ACCOUNT_BRIEF", "DRAFT", "wtp_comercial"),
    ("SKILL_CM_CALL_CAPTURE", "DRAFT", "wtp_comercial"),
    ("SKILL_CM_CARTERA_PRIORITIZE", "DRAFT", "wtp_comercial"),
    ("SKILL_CM_REORDER_PREDICT", "DEFINITION_PENDING", "wtp_comercial"),
    ("SKILL_SV_TRIAGE", "DRAFT", "wtp_servicio"),
    ("SKILL_SV_RESPUESTA", "DRAFT", "wtp_servicio"),
    ("SKILL_SV_ESCALACION", "DRAFT", "wtp_servicio"),
    ("SKILL_SV_TEMAS", "DRAFT", "wtp_servicio"),
    ("SKILL_SV_GARANTIA_DEVOLUCION", "DRAFT", "wtp_servicio"),
    ("SKILL_FI_CIERRE_NARRADO", "DRAFT", "wtp_finanzas_cierre"),
    ("SKILL_FI_ASIENTOS", "DRAFT", "wtp_finanzas_cierre"),
    ("SKILL_FI_VARIACIONES", "DRAFT", "wtp_finanzas_cierre"),
    ("SKILL_FI_EEFF", "DRAFT", "wtp_finanzas_cierre"),
    ("SKILL_LG_NDA_TRIAGE", "DRAFT", "wtp_legal"),
    ("SKILL_LG_CONTRATO_REVIEW", "DRAFT", "wtp_legal"),
    ("SKILL_LG_VENCIMIENTOS", "DRAFT", "wtp_legal"),
    ("SKILL_LG_PREFIRMA", "DRAFT", "wtp_legal"),
    ("SKILL_LG_VIGENCIA_NORMA", "DEFINITION_PENDING", "wtp_legal"),
    ("SKILL_GE_PULSO", "DRAFT", "wtp_gerencia"),
    ("SKILL_GE_BRIEF_RECURRENTE", "DRAFT", "wtp_gerencia"),
    ("SKILL_GE_QBR", "DRAFT", "wtp_gerencia"),
    ("SKILL_GE_RIESGOS", "DRAFT", "wtp_gerencia"),
    ("SKILL_OP_SOP", "DRAFT", "wtp_operaciones"),
    ("SKILL_OP_STATUS", "DRAFT", "wtp_operaciones"),
    ("SKILL_OP_PROVEEDOR_EVAL", "DRAFT", "wtp_operaciones"),
    ("SKILL_MK_CAMPANA", "DRAFT", "wtp_marketing"),
    ("SKILL_MK_CONTENIDO_VOZ", "DRAFT", "wtp_marketing"),
    ("SKILL_MK_BRAND_AUDIT", "DRAFT", "wtp_marketing"),
    ("SKILL_HR_CONTRATACION", "DRAFT", "wtp_rrhh"),
]


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    catalog_dir = repo_root / "faberloom"
    catalog_dir.mkdir(parents=True, exist_ok=True)

    generated = 0
    for skill_id, status, pack_id in SKILLS:
        path = catalog_dir / f"{skill_id}.md"
        path.write_text(_skill_md(skill_id, status, pack_id), encoding="utf-8")
        generated += 1

    print(f"Generated {generated} skill files in {catalog_dir}")


if __name__ == "__main__":
    main()

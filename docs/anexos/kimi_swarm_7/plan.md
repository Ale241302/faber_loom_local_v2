# Plan: Investigacion Operativa - SaaS B2B Agentes IA para PYMEs Manufactureras LATAM

## Objetivo
Producir 7 archivos markdown: D1.md a D6.md (una dimension por archivo) mas D0_CROSS_SUMMARY.md, con datos verificados, fuentes, y tablas duras. Cero diseno de producto, solo investigacion de hechos externos.

## Stage 1 - Research Swarm (6 dimensiones en paralelo)
Cargar skill: `deep-research-swarm`. Diseno: Route B - Focused Search (6 preguntas especificas con dimensiones claras).

- **D1_Verificacion_Google_OAuth_Gmail**: Tiempos, costos, requisitos reales de verificacion OAuth restringida Gmail 2026. Alternativas (testing, service account, SMTP).
- **D2_WhatsApp_Business_LATAM**: Onboarding Meta CR, precios mensaje 2026, BSPs LATAM, costos por pais para 300 conversaciones/mes.
- **D3_Base_Legal_Datos_B2B**: Leyes proteccion datos CR/CO/MX/GT/BR para datos B2B con LLM en US. Transferencias, minimos piloto, DPA Anthropic.
- **D4_Resolucion_Identidad_Email_CRM**: Patrones de matching email->cuenta en CRMs maduros (HubSpot, SFDC, etc). Benchmarks precision.
- **D5_Disposicion_Pago_PYMES_LATAM**: Precios publicos 2026 de competidores (Zapia, Yalo, Treble, etc). Estudios adopcion IA PYMEs LATAM.
- **D6_Economia_Inferencia_Anthropic**: Precios API Anthropic junio 2026, prompt caching TTL/break-even, batch API, rate limits, context windows.

Cada agente recibe:
1. Las instrucciones de su dimension (del prompt del usuario)
2. Las reglas del GUARD DE ALCANCE (vinculante)
3. El formato de salida exigido (RESUMEN/HALLAZGOS/TABLA/DATOS NO ENCONTRADOS/IMPLICACION)
4. RUN_ID: KIMI_SWARM_7_ATERRIZAJE_2026-06-12

## Stage 2 - Cross-Summary
El orquestador lee los 6 archivos D1-D6 y produce D0_CROSS_SUMMARY.md con:
- 10 hechos mas accionables
- Conflictos entre fuentes si los hay

## Output
7 archivos en /mnt/agents/output/:
- D1_Verificacion_Google_OAuth_Gmail.md
- D2_WhatsApp_Business_LATAM.md
- D3_Base_Legal_Datos_B2B.md
- D4_Resolucion_Identidad_Email_CRM.md
- D5_Disposicion_Pago_PYMES_LATAM.md
- D6_Economia_Inferencia_Anthropic.md
- D0_CROSS_SUMMARY.md

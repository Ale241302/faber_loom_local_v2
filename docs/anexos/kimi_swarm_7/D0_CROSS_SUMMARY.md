RUN_ID: KIMI_SWARM_7_ATERRIZAJE_2026-06-12

# D0 - CROSS-SUMMARY: 10 HECHOS MAS ACCIONABLES Y CONFLICTOS ENTRE FUENTES

---

## LOS 10 HECHOS MAS ACCIONABLES (de 6 dimensiones, ordenados por impacto operativo inmediato)

### H1. Gmail sin verificacion es posible HOY: dos caminos de cero costo y cero espera
**De:** D1 | **Confianza:** ALTO
- **Service Account + Domain-Wide Delegation** (Google Workspace propio): 30 min de setup, scope `gmail.send`, cero verificacion OAuth, cero costo CASA. Solo funciona para cuentas del mismo dominio Workspace.
- **App Password + SMTP** (cualquier cuenta con 2FA): 5 min de setup, cero verificacion, limite 500/dia (free) / 2,000/dia (Workspace). Less Secure Apps fue desactivado en marzo 2025, pero App Passwords con 2FA siguen funcionando en junio 2026.
- **Accion:** Para enviar desde buzon propio en piloto, NO se necesita verificacion Google. El camino SMTP es inmediato; DWD requiere Workspace.

### H2. Si se necesita leer buzones de terceros (gmail.readonly), el camino obligatorio cuesta $540-4,500 y 1-3 meses
**De:** D1 | **Confianza:** ALTO
- `gmail.readonly` es scope RESTRICTED → requiere CASA Tier 2 obligatoriamente. Costo minimo real: $540/año (TAC Security). Timeline real reportado por desarrolladores 2025-2026: 2-8 semanas de verificacion Google + 1-3 semanas de CASA = 1-3 meses end-to-end.
- **Accion:** Evitar scopes restricted en piloto. Usar solo `gmail.send` (sensitive, no restricted) que evita CASA por completo.

### H3. WhatsApp Business API: service messages son gratis ilimitadas; costo real para 300 msgs/mes es ~$4-7
**De:** D2 | **Confianza:** ALTO
- Meta migro a cobro por mensaje entregado en julio 2025. Las respuestas dentro de la ventana de 24h (service messages) son **gratis ilimitadas** desde noviembre 2024.
- Para 300 mensajes/mes mixtos (70% utility, 30% marketing) a clientes en CO/MX/GT: costo Meta solo ~$3.82/mes. Con Twilio: ~$5.32/mes total. Wati/360dialog: ~$52/mes (incluyen inbox UI).
- **Accion:** Estrategia de minimizar templates de pago maximizando respuestas en ventana 24h. Twilio para piloto tecnico; Wati si se necesita inbox visual.

### H4. Guatemala no tiene ley de proteccion de datos vigente; Costa Rica, Colombia, Mexico y Brasil si
**De:** D3 | **Confianza:** ALTO (requiere validacion con abogado local)
- Guatemala: **sin ley vigente** a junio 2026 (Iniciativa 6103 aprobada en 2do debate en 2023 pero no promulgada). No hay requisitos legales especificos de transferencia internacional.
- Mexico: nueva LFPDPPP vigente desde marzo 2025. Transferencia requiere contrato encargado (Arts. 36-40). Sanciones: hasta ~USD 1.8M.
- Colombia: Ley 1581/2012. Transferencia a EE.UU. prohibida salvo excepciones (consentimiento expreso o CCM de la RIPD - Circular 003/2025). Sanciones: hasta ~USD 65,000.
- Costa Rica: Ley 8968. Transferencia requiere garantias adecuadas (clausulas contractuales) o consentimiento.
- Brasil: LGPD. Requiere SCCs de la ANPD (Res. 19/2024). Sin decision de adecuacion para EE.UU.
- **Accion:** Cada pais requiere stack legal distinto. Guatemala es el de menor friccion legal hoy. Colombia y Mexico tienen los marcos mas exigentes.

### H5. En Colombia, datos corporativos puros escapan de la ley de proteccion de datos
**De:** D3 | **Confianza:** ALTO (requiere validacion con abogado local)
- Concepto oficial SIC Colombia (Radicado 23-571469, 2024): datos corporativos de persona juridica (email institucional, celular corporativo, direccion de contacto) **escapan del ambito de la Ley 1581/2012**. Solo los datos personales del representante legal o contacto natural (nombre, cedula, email personal, telefono personal) requieren autorizacion.
- **Accion:** Para clientes B2B en Colombia, datos de la empresa (email corporativo, telefono de oficina) tienen marco regulatorio mas laxo que datos personales del contacto individual.

### H6. El precio de entrada del mercado es USD 15-49/mes; USD 30-50 compite con Chately, Cliengo, CRMWhata, Zoko
**De:** D5 | **Confianza:** ALTO
- Tabla de competidores directos en banda USD 30-50: Chately ($39), Cliengo Starter ($45), CRMWhata ($39), Zoko Starter ($40). ManyChat Pro ($14-29) y Kommo ($15/usuario) son mas baratos pero requieren adicionales.
- Productos de mayor escala (Treble.ai $99, Respond.io $79-159, Wati $49-99, Leadsales $133) estan por encima de la banda.
- **Accion:** USD 30-50/mes es posicionable pero competitivo. La diferenciacion no sera el precio sino el valor demostrado en 14-30 dias.

### H7. 54% de PYMEs latinoamericanas ya usa IA; 70% planea seguir invirtiendo; pero 22% cita falta de presupuesto
**De:** D5 | **Confianza:** ALTO (Microsoft 2025, n no especificado)
- Disposicion de pago existe y es creciente. Las barreras son operativas (soporte deficiente, costos ocultos) no de demanda.
- Churn principal: soporte lento e ineficiente, markup sobre mensajes no transparentes, usuarios adicionales costosos.
- **Accion:** El mercado esta caliente para adopcion. El riesgo es churn por expectativas no cumplidas, no falta de demanda.

### H8. Prompt caching de Anthropic: 90% de descuento en lecturas, break-even en 2 lecturas
**De:** D6 | **Confianza:** ALTO (fuente oficial Anthropic)
- Cache read = 0.1x precio base input. TTL 5 min (default, se renueva con cada hit) o 1h (2x costo write). Break-even: 2 lecturas para 5-min, 3 lecturas para 1h. Minimo cacheable: 1,024 tokens. Max 4 breakpoints.
- Batch API: 50% descuento adicional en input/output, SLA 24h. Combinado con caching: costo efectivo de Sonnet 4.6 para workloads nocturnos con contexto repetido cae a ~$0.30 input + $7.50 output.
- **Accion:** El prompt caching es el lever de costo mas agresivo. Una arquitectura de contexto cacheado con prefix reutilizado reduce costos de input en ~80%.

### H9. Domain-matching exacto es el patron universal en CRMs; ninguno maneja bien los 3 casos borde clave
**De:** D4 | **Confianza:** ALTO
- HubSpot, Zendesk, Front, Attio usan matching exacto de dominio como regla primaria. HubSpot tiene lista de 4,746+ freemail domains excluidos. Salesforce es la excepcion: requiere custom Flow/Apex.
- Tres casos borde sin solucion elegante en ningun CRM: (1) subdominios como entidades separadas, (2) dominios compartidos entre subsidiarias, (3) contactos en multiples cuentas. Plus-addressing no esta documentado en ninguno.
- **Accion:** Matching por dominio exacto + lista de freemail exclusions es el minimo viable probado. No hay necesidad de reinventar la rueda; los casos borde requieren triage manual.

### H10. Tier 4 de Anthropic: 4,000 RPM y 10M ITPM por solo $400 de deposito acumulado
**De:** D6 | **Confianza:** ALTO (fuente oficial)
- Subir de Tier 1 a Tier 4 requiere $400 acumulados (no un pago upfront). Spend limit: Tier 4 = $200,000/mes. Context window: 1M tokens (Opus/Sonnet), 200K (Haiku).
- Degradacion: Opus 4.7 mantiene >=80% accuracy en multi-hop hasta 512K; degradacion modesta a 1M. Sonnet 4.5 cae a 18.5% en MRCR v2 a 1M. Long-context surcharge (>200K tokens) duplica el input rate.
- **Accion:** Tier 4 es accesible tempranamente. Para contexto >200K, Opus es superior a Sonnet. El caching es critico para mitigar el long-context surcharge.

---

## CONFLICTOS ENTRE FUENTES (documentados, no resueltos)

### C1. Tiempo real de verificacion Google OAuth: promesa oficial vs. realidad de desarrolladores
- **Google oficial:** 3-5 dias laborables para sensitive scopes.
- **Desarrolladores 2025-2026:** Reportes de 6-8+ semanas atorados en iteraciones (Google Developer Forums, enero 2026; 6+ semanas en fase Privacy Policy, mayo 2026).
- **Nango:** "< 1 week if you prepare well" (pero CASA es el cuello de botella principal).
- **Estatus:** CONFLICTO NO RESUELTO. El rango real consolidado es 2-8 semanas. La promesa oficial no se cumple en la practica para apps independientes.

### C2. Comportamiento de "Production sin verificar" con sensitive scopes
- **Stack Overflow (respuesta altamente votada):** "In production, tokens will NOT expire after 7 days." Confirmado por multiples usuarios.
- **n8n Community (caso individual, agosto 2025):** Usuario reporta token expiry incluso en production sin verificar.
- **Google:** No documenta oficialmente el comportamiento de este estado intermedio.
- **Estatus:** CONFLICTO NO RESUELTO. La mayoria de reportes indican tokens longevos en production, pero hay casos de excepcion no explicados.

### C3. Precios Meta WhatsApp: discrepancia entre fuentes BSP
- **Whautomate (abr 2026):** Colombia Marketing $0.0125, Mexico $0.0305
- **ManyChat (abr 2026):** Colombia Marketing $0.0144 (+15%), Mexico $0.0351 (+15%)
- **Estatus:** CONFLICTO PARCIALMENTE EXPLICADO. Las tarifas difieren por fechas de actualizacion distintas y posible markup del BSP. Se recomienda verificar directamente en la pagina oficial de Meta antes de presupuestar.

### C4. Costo de CASA Tier 2: rango extremo entre labs autorizados
- **TAC Security:** $540-$855 (reportado por cliente en 2026) / $675-$3,600 (pagina oficial)
- **Leviathan Security:** $3,000-$6,000
- **PwC:** Gratis hasta 2025; dejo de aceptar solicitudes en 2025
- **Estatus:** CONFLICTO NO RESUELTO. No existe precio estandar. El rango real es $540-$6,000 dependiendo del lab y complejidad. TAC Security es la opcion economica documentada.

### C5. Precio de Leadsales: fuentes divergentes
- **Fuente comparativa (febrero 2026):** Basico $97/mes, Profesional $133/mes
- **Fuente D5 directa:** Basico $83.99/mes
- **Estatus:** CONFLICTO NO RESUELTO. Posible cambio de precio entre fechas o planes distintos. Requiere verificacion directa.

---

## MATRIZ DE RIESGO CRUZADO (intersecciones dimensionales)

| Riesgo | Dimensiones | Severidad |
|--------|-------------|-----------|
| Legal: transferencia a US sin mecanismo adecuado en CO/MX/BR | D3 x D1/D6 (Anthropic API = proveedor US) | ALTA |
| Gmail: app en production sin verificar puede perder tokens impredeciblemente | D1 x D6 (dependencia de email para agente) | MEDIA |
| WhatsApp: onboarding 10-15 dias bloquea piloto rapido | D2 x D5 (expectativa de valor en 14-30 dias) | MEDIA |
| Precio: banda USD 30-50 es la mas competitiva del mercado | D5 x D6 (margen comprimido por costos de inferencia) | MEDIA |
| Identity: domain-matching falla con subdominios de empresas grandes | D4 x D1 (emails de clientes B2B manufactureros) | BAJA |

---

*Cross-summary compilado: 2026-06-13. Fuentes: 6 dimensiones de investigacion, 100+ busquedas independientes, 80+ fuentes citadas. Los conflictos se reportan tal como fueron encontrados; no se resolvieron a favor de ninguna fuente.*

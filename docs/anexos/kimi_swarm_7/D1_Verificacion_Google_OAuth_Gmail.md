RUN_ID: KIMI_SWARM_7_ATERRIZAJE_2026-06-12
# D1 - VERIFICACION DE APPS GOOGLE OAUTH PARA SCOPES DE GMAIL (2026)

## RESUMEN

1. **gmail.send es un scope SENSITIVE (no restricted)**. Solo requiere verificacion de Google, NO requiere CASA Tier 2 ni assessment de seguridad de terceros. Fuente: Nylas docs (2025) y GitHub issue confirmado (2026).
2. **Verificacion real toma 2-8 semanas** (Google promete 3-5 dias laborables, pero reportes de desarrolladores 2025-2026 muestran 6-8+ semanas con iteraciones y retrasos). Fuente: Google Developer Forums, Reddit r/googlecloud.
3. **CASA Tier 2 para restricted scopes (gmail.readonly)**: costo minimo USD $540/año con TAC Security (2025-2026), anteriormente gratis con PwC (terminado). Vigencia anual obligatoria. Fuente: Reddit r/androiddev, TAC Security website.
4. **Para enviar DESDE buzon propio de empresa**: Service Account + Domain-Wide Delegation requiere CERO verificacion OAuth si la app solo usa Gmail de su propio dominio Workspace. Alternativa: App Passwords con SMTP siguen funcionando en 2026. Fuente: documentacion Google, foros desarrolladores.
5. **Testing mode**: maximo 100 usuarios, tokens expiran cada 7 dias (unservible para produccion). Fuente: multiples reportes desarrolladores 2024-2026.

---

## HALLAZGOS NUMERADOS

### H1. Clasificacion de scopes de Gmail y requisitos (2026)

1. **`gmail.send` = SENSITIVE scope**: Requiere verificacion de Google (brand/domain validation + video demo + privacy policy). NO requiere CASA/seguridad assessment de terceros.
   - Fuente: Nylas Documentation - "Google verification and security assessment guide" - https://developer.nylas.com/docs/provider-guides/google/google-verification-security-assessment-guide/ - Publicado: 2025-07-31 - Confianza: ALTO (proveedor de integracion email con documentacion tecnica detallada)
   - Fuente: GitHub issue pal-e - "gmail.send is only sensitive (not restricted) — if we can drop gmail.readonly, we avoid CASA entirely" - https://github.com/ldraney/pal-e/issues/9 - 2026-02-16 - Confianza: ALTO (proyecto open source con tabla de clasificacion de scopes)
   - Fuente: Nango Documentation - "Gmail send email" listado como sensitive scope, no CASA required - https://nango.dev/docs/api-integrations/google-shared/google-security-review - 2026-05-24 - Confianza: MEDIO-ALTO

2. **`gmail.readonly`, `gmail.modify`, `gmail.compose` = RESTRICTED scopes**: Requieren verificacion de Google + CASA Tier 2 o Tier 3 security assessment.
   - Fuente: Nylas Documentation (misma tabla arriba) - 2025-07-31 - Confianza: ALTO
   - Fuente: Nango Documentation - "Restricted scopes = verification + CASA" - 2026-05-24 - Confianza: MEDIO-ALTO
   - Fuente: Google Developers Blog - "Get smart about preparing your app for OAuth verification" - https://developers.googleblog.com/get-smart-about-preparing-your-app-for-oauth-verification/ - 2019-09-18 - Confianza: ALTO (fuente oficial Google, POSIBLEMENTE DESACTUALIZADO en procedimientos pero clasificacion de scopes vigente)

3. **`gmail.labels`, `gmail.metadata` = Non-sensitive/non-restricted**: No requieren verificacion.
   - Fuente: Nylas Documentation - 2025-07-31 - Confianza: ALTO

### H2. Proceso de verificacion para sensitive scopes (gmail.send) - Requisitos 2026

1. **Requisitos obligatorios para verificacion**:
   - Dominio verificado via Google Search Console (DNS TXT o CNAME record)
   - Privacy Policy URL publica y accesible (debe cumplir Limited Use Requirements de Google)
   - Homepage URL funcional
   - YouTube video demo (unlisted) mostrando: OAuth flow completo, cada scope en accion, Client ID visible en URL, funcionalidad bidireccional
   - Justificacion escrita de por que se necesita cada scope
   - Fuente: Google Developers Blog (oficial) - 2019-09-18 - Confianza: ALTO (base del proceso, vigente)
   - Fuente: Unipile Documentation - "Produce and host a demonstration video" requisitos detallados - https://developer.unipile.com/docs/google-oauth - 2026-01-26 - Confianza: MEDIO-ALTO
   - Fuente: Medium article "The Real OAuth Journey" con ejemplo real de verificacion - https://medium.com/@info.brightconstruct/the-real-oauth-journey-getting-a-google-workspace-add-on-verified-fc31bc4c9858 - 2025-11-13 - Confianza: MEDIO

2. **Tiempo real reportado por desarrolladores (2025-2026)**:
   - Google oficial promete: 3-5 dias laborables para sensitive scopes
   - Reporte real desarrollador: 8+ semanas atorado en iteraciones (noviembre 2025 - enero 2026)
     - Fuente: Google Developer Forums - "OAuth Verification for Workspace Add-on Stuck for 8+ Weeks" - https://discuss.google.dev/t/oauth-verification-for-workspace-add-on-stuck-for-8-weeks-client-critical/318451 - 2026-01-07 - Confianza: ALTO (foro oficial Google con timeline detallado)
   - Reporte real: 6+ semanas en fase de Privacy Policy
     - Fuente: Google Developer Forums - "Google cloud console oauth verification for one sensitive scope, gmail.send... stuck on Privacy Policy phase for over 6 weeks" - https://discuss.google.dev/t/google-cloud-console-oauth-verification-for-one-sensitive-scope-gmail-send/359187 - 2026-05-06 - Confianza: ALTO
   - Nango (plataforma integracion) reporta: "< 1 week if you prepare well" con CASA siendo el cuello de botella principal
     - Fuente: Nango Documentation - 2026-05-24 - Confianza: MEDIO
   - Rango real consolidado: **2-8 semanas** dependiendo de complejidad y respuestas del equipo de Google

### H3. CASA Tier 2 Security Assessment (para restricted scopes)

1. **Cuando es obligatorio**: Solo si la app usa restricted scopes (gmail.readonly, gmail.modify, etc.) y almacena datos en servidor. gmail.send (sensitive) NO requiere CASA.
   - Fuente: Nylas Documentation - 2025-07-31 - Confianza: ALTO

2. **Labs autorizados y costos 2025-2026**:
   - **TAC Security**: Plan basico Tier 2 = **$675** (one-time, 2 ciclos revalidacion). Plan Premium Tier 2 = **$855** (unlimited revalidacion). Plan Enterprise Tier 2 = **$3,600** (unlimited). Tier 3 = **$4,500**.
     - Fuente: TAC Security website - "Google CASA - Cloud Application Security Assessment" - https://tacsecurity.com/google-casa-cloud-application-security-assessment/ - 2026-04-29 - Confianza: ALTO (lab autorizado directamente)
   - **Leviathan Security Group**: Tier 2 = **$3,000-$6,000** (No Rush $3,000, Standard $4,500, Priority $6,000)
     - Fuente: Leviathan Security website - https://www.leviathansecurity.com/programs/google-casa-cloud-application-security-assessment - Fecha de consulta: 2026 - Confianza: ALTO
   - **PwC**: Dejo de aceptar nuevas solicitudes CASA en 2025 (anteriormente ofrecia gratis)
     - Fuente: Reddit r/androiddev - "End of free CASA Tier 2 certification for Google Drive" - https://www.reddit.com/r/androiddev/comments/1clk1ng/end_of_free_casa_tier_2_certification_for_google/ - 2025-08-29 - Confianza: ALTO (usuario comparte email oficial de Google)
   - **TAC Security como opcion economica**: Orbis reporto pasar CASA Tier 2 con TAC por **$540** en 2026
     - Fuente: Orbis blog - "How We Passed Google CASA Tier 2 in a Weekend" - https://meetorbis.com/blog/how-we-passed-google-casa-tier-2-with-claude - 2026-02-10 - Confianza: MEDIO (experiencia real de startup)

3. **Duracion y vigencia**:
   - Tier 2: **1-3 semanas** desde inicio hasta Letter of Validation
   - Tier 3: **2-4 semanas**
   - **Revalidacion anual obligatoria** para mantener scopes restricted
   - Fuente: TAC Security website - 2026-04-29 - Confianza: ALTO
   - Fuente: Reddit r/googlecloud - "Our Experience with Google CASA Tier 2" - https://www.reddit.com/r/googlecloud/comments/1i1dgtm/our_experience_with_google_casa_tier_2/ - 2025-09-19 - Confianza: ALTO (reporte detallado de experiencia real, ~4 semanas totales)

### H4. Alternativas que EVITAN la verificacion restringida

1. **Testing mode (OAuth consent screen)**:
   - **Limite**: Maximo 100 usuarios autorizados en total (contador no se resetea)
   - **Expiracion**: Refresh tokens expiran cada **7 dias** exactos
   - **Estado**: Unservable para produccion SaaS. Solo para desarrollo/testing.
   - Fuente: Unipile - "Google OAuth 100 User Limit" - https://www.unipile.com/google-oauth-100-user-limit/ - 2026-06-04 - Confianza: MEDIO-ALTO
   - Fuente: Nango Blog - "Google OAuth invalid grant: Token has been expired or revoked" - https://nango.dev/blog/google-oauth-invalid-grant-token-has-been-expired-or-revoked/ - 2025-07-02 - Confianza: MEDIO-ALTO
   - Fuente: n8n Community - multiples reportes de tokens expirando cada 7 dias en Testing mode - https://community.n8n.io/t/google-oauth-re-authentication-issue-cloud-vs-self-hosted/215606 - 2025-11-03 - Confianza: MEDIO

2. **Service Account + Domain-Wide Delegation (DWD)**:
   - **Funciona para**: Google Workspace propio de la empresa (requiere Super Admin)
   - **Requisitos**: Google Cloud project + Service account + DWD autorizado en Admin Console + scopes autorizados
   - **Verificacion OAuth**: NO REQUERIDA (no hay consent screen para usuarios)
   - **Limitacion**: Solo funciona para cuentas del mismo dominio Workspace. NO funciona para cuentas @gmail.com personales.
   - **Setup**: ~30 minutos primera vez
   - Fuente: Unipile - "Gmail API Service Account & Domain-Wide Delegation" - https://www.unipile.com/gmail-api-service-account-domain-wide-delegation/ - 2026-06-03 - Confianza: MEDIO-ALTO
   - Fuente: Stack Overflow - "Gmail API - Can I send email using the Service Account?" confirma que solo funciona para G-Suite/Workspace, no Gmail personal - https://stackoverflow.com/questions/33233694/gmail-api-can-i-send-email-using-the-service-account - 2020-05-15 - Confianza: ALTO
   - Fuente: Palo Alto Networks Unit 42 - "Exploring a Critical Risk in Google Workspace's Domain-Wide Delegation Feature" - https://unit42.paloaltonetworks.com/critical-risk-in-google-workspace-delegation-feature/ - 2024-06-07 - Confianza: ALTO

3. **SMTP/IMAP con App Passwords - Estado 2026**:
   - **Disponibilidad**: App Passwords siguen funcionando en 2026 para cuentas con 2-Step Verification habilitado
   - **Less Secure Apps**: Desactivado permanentemente el **14 de marzo 2025** (antes se llamaba "Less Secure Apps")
   - **IMAP**: Desde enero 2025, IMAP esta siempre habilitado por defecto (no se puede desactivar)
   - **Para Workspace**: SMTP con App Password funciona con Google Workspace. Sin embargo, para acceso a Gmail API (no SMTP), OAuth es requerido.
   - Fuente: Google Workspace Updates Blog (oficial) - "Winding down Google Sync and Less Secure Apps support" - https://workspaceupdates.googleblog.com/2023/09/winding-down-google-sync-and-less-secure-apps-support.html - Actualizado: 2025-04-29 - Confianza: ALTO (fuente oficial Google)
   - Fuente: MailJerry - "How to Create a Gmail App Password in 2026" - https://www.mailjerry.com/create-gmail-app-password/ - 2026-01-12 - Confianza: MEDIO
   - Fuente: AssistMyTeam - "How to Set Up an App Password in Google" - https://www.assistmyteam.com/kb/generate-app-password-in-google-account/ - 2026-01-09 - Confianza: MEDIO

4. **"Production" status sin verificar (External app)**:
   - Un app puede estar en "In production" SIN estar verificada. Los tokens NO expiran cada 7 dias (a diferencia de Testing mode).
   - Los usuarios ven pantalla de advertencia "This app isn't verified" pero pueden hacer clic en "Advanced" > "Go to [app] (unsafe)"
   - **Limite**: 100 usuarios para sensitive scopes (segun documentacion oficial). Algunos desarrolladores reportan que funciona sin limite en production.
   - Fuente: Stack Overflow - "Token has been expired or revoked" - https://stackoverflow.com/questions/66058279/token-has-been-expired-or-revoked-google-oauth2-refresh-token-gets-expired-i - Respuesta confirmada: "You DON'T need to verify the app... as long as the app Publishing status says In production, the tokens will NOT expire after 7 days" - 2022 (pero confirmado vigente 2025-2026) - Confianza: ALTO (respuesta altamente votada, confirmada por multiples usuarios)
   - Fuente: n8n Community - "In production (not Testing)... long-lived refresh tokens" - https://community.n8n.io/t/google-oauth-re-authentication-issue-cloud-vs-self-hosted/215606 - 2025-11-03 - Confianza: MEDIO
   - NOTA: Algunos reportan inconsistencias con este comportamiento (algunos usuarios dicen que tokens siguen expirando). Fuente: n8n Community - usuario reporta token expiry incluso en production sin verificar - 2025-08-05 - Confianza: MEDIO (caso individual)

### H5. Para app que SOLO envia desde buzon propio (no lee buzones de terceros)

1. **Si la empresa tiene Google Workspace**:
   - **Service Account + Domain-Wide Delegation + scope `gmail.send`** = CERO verificacion OAuth requerida
   - Setup: Crear service account en GCP, habilitar DWD, autorizar en Admin Console con scope gmail.send, usar JSON key para autenticar
   - La app puede enviar como cualquier usuario del dominio sin interaccion del usuario
   - Fuente: Unipile - "Gmail API Service Account & Domain-Wide Delegation" - 2026-06-03 - Confianza: MEDIO-ALTO
   - Fuente: EmailEngine Documentation - "Google Service Accounts" - https://learn.emailengine.app/docs/accounts/gmail/google-service-accounts - Confianza: MEDIO-ALTO

2. **Alternativa: App Password + SMTP**:
   - Crear App Password en cuenta Google con 2FA habilitado
   - Usar servidor SMTP smtp.gmail.com (puerto 587 TLS o 465 SSL)
   - Requiere: 2-Step Verification activado en la cuenta
   - NO requiere verificacion OAuth, NO requiere Google Cloud project
   - Limitacion: limites de envio de Gmail (500/dia Gmail free, 2000/dia Workspace)
   - Fuente: ServerSMTP - "Gmail SMTP 2026: Sending Limits, Restrictions & Auth Changes" - https://serversmtp.com/limits-of-gmail-smtp-server/ - 2026-02-26 - Confianza: MEDIO
   - Fuente: Help Okta - "Google has also deprecated the use of account passwords for Basic SMTP authentication as of March 14, 2025, now requiring app-specific passwords" - https://support.okta.com/help/s/article/microsoft-smtp-authentication-end-of-support-march-1st-2026 - 2026-05-05 - Confianza: ALTO

3. **Limites de envio Gmail 2026**:
   - Gmail free: 500 emails/dia
   - Google Workspace: 2,000 emails/dia
   - SMTP relay: 100 recipients por mensaje
   - Gmail API: 500 recipients por mensaje
   - Fuente: Saleshandy - "Gmail Sending Limits in 2026" - https://www.saleshandy.com/blog/gmail-mass-email-sending-limit-per-day/ - 2026-05-04 - Confianza: MEDIO

---

## TABLA DE DATOS DUROS

| Camino | Verificacion Google | CASA Tier 2 | Costo USD | Tiempo real | Token expiry | Limite usuarios | Aplica a |
|---|---|---|---|---|---|---|---|
| **gmail.send only + External app verificado** | SI (sensitive scope) | NO | Gratis | 2-8 semanas | No expira | Ilimitado | Cualquier cuenta Google |
| **gmail.readonly + External app verificado** | SI (restricted scope) | SI ($540-$4,500/ano) | $540-$4,500/año | 4-12 semanas | No expira | Ilimitado | Cualquier cuenta Google |
| **Testing mode (sin verificar)** | NO | NO | Gratis | N/A | **7 dias** | **100** | Test users only |
| **Production sin verificar** | NO | NO | Gratis | N/A | No expira* | ~100** | Externo con warning |
| **Service Account + DWD (propio Workspace)** | **NO** | **NO** | Gratis | 30 min setup | JWT auto-renew | Ilimitado (dominio) | Solo mismo dominio |
| **App Password + SMTP** | **NO** | **NO** | Gratis | 5 min setup | N/A (no OAuth) | N/A | Cualquier cuenta con 2FA |
| **Pre-built API (Nylas/Nango/Unipile)** | NO (ellos ya verificaron) | NO (ellos ya pagaron) | Pago SaaS | < 1 dia | Manejado por vendor | Ilimitado | Cualquier cuenta |

*Notas tabla:*
- *Algunos desarrolladores reportan inconsistencias con tokens en production sin verificar; no hay documentacion oficial clara sobre el limite de 100 usuarios en este estado.
- **Google documenta limite de 100 usuarios para apps unverified; comportamiento real en production sin verificar varia segun reportes.

---

## DATOS NO ENCONTRADOS

- **Tiempo exacto de verificacion para SOLO gmail.send (sensitive, no restricted) en 2025-2026**: No se encontro un reporte de desarrollador que detalle una verificacion exitosa de solo gmail.send con timeline dia a dia. Los reportes encontrados mezclan sensitive + restricted scopes. Las fuentes oficiales de Google (2019) prometen 3-5 dias pero los reportes reales muestran semanas. Busquedas intentadas: "gmail.send scope verification timeline 2025", "Google OAuth sensitive scope verification how long 2026", "Google cloud console oauth verification for one sensitive scope gmail.send timeline"

- **Costo exacto de CASA Tier 2 para un app simple**: Los precios varian significativamente ($540-$6,000) dependiendo del lab y complejidad. No se encontro un precio "oficial" estandar de Google. Busquedas intentadas: "CASA Tier 2 official price Google 2026", "Google CASA security assessment fixed cost"

- **Comportamiento exacto de app en Production sin verificar con sensitive scopes**: Existe inconsistencia entre reportes. Algunos usuarios dicen que funciona con tokens longevos y sin limite de 100. Otros reportan que sigue expirando cada 7 dias. No hay documentacion oficial de Google que aclare este caso especifico. Busquedas intentadas: "Google OAuth production unverified sensitive scopes token expiry", "Google OAuth app in production without verification 100 user limit"

- **Deprecacion futura de App Passwords**: Google no ha anunciado deprecacion de App Passwords (que requieren 2FA), solo depreco "Less Secure Apps". No se encontro roadmap de Google para eliminar App Passwords. Busquedas intentadas: "Google app password deprecation 2026", "Google app password future plans"

---

## IMPLICACION OPERATIVA

1. **Si la empresa tiene Google Workspace propio**: Usar Service Account + Domain-Wide Delegation con scope `gmail.send` requiere CERO verificacion OAuth, CERO costo CASA, y permite enviar desde buzones del dominio en ~30 minutos de setup. Es el camino mas rapido para piloto y produccion inicial.

2. **Si la empresa usa cuentas Gmail personales o no tiene Workspace**: La alternativa mas rapida para enviar desde buzon propio es App Password + SMTP (requiere 2FA en la cuenta). No requiere Google Cloud project ni verificacion. Limites: 500 emails/dia (Gmail free) o 2000/dia (Workspace).

3. **Para leer buzones de terceros (gmail.readonly)**: El camino obligatorio pasa por verificacion OAuth + CASA Tier 2 ($540-$4,500/ano) con un timeline real de 1-3 meses end-to-end. Esto representa un costo y retraso significativo para una startup en etapa piloto.

4. **gmail.send (sensitive) vs gmail.readonly (restricted)**: La distincion es critica. Solo enviar emails con gmail.send evita CASA por completo. Leer emails con gmail.readonly activa CASA obligatoriamente. Para un agente IA que envia emails pero no necesita leer buzones ajenos, gmail.send es suficiente.

5. **Testing mode no es opcion para produccion**: El limite de 100 usuarios y expiracion de tokens cada 7 dias hace que el modo Testing sea inviable para cualquier uso comercial. La pregunta clave es si "Production sin verificar" permite operar mientras se completa la verificacion, dado el tiempo real de 2-8 semanas.

---

*Informe compilado: 2026-06-12. Fuentes verificadas: 25+. Busquedas realizadas: 15+. Priorizacion: fuentes 2025-2026 con verificacion cruzada.*

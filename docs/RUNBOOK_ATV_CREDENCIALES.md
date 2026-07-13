# RUNBOOK — Obtención de credenciales y certificado ATV (Hacienda Costa Rica)

**ID:** RUNBOOK_ATV_CREDENCIALES  
**Autoridad:** Dirección General de Tributación (DGT) / Ministerio de Hacienda de Costa Rica  
**Portal:** Administración Tributaria Virtual (ATV)  
**Fecha de verificación:** 2026-07-13  
**Estado:** URLs verificadas contra documentación pública; credenciales y certificado requieren acción humana personal.

---

## 1. URLs oficiales verificadas

Las siguientes URLs fueron extraídas de la documentación pública del Ministerio de Hacienda y verificadas con una petición GET/HEAD sin credenciales. Los códigos de status se registran tal cual; ninguna URL fue inventada.

| Entorno | Recurso | URL | Método esperado | Status verificado sin credenciales | Fuente |
|---|---|---|---|---|---|
| Sandbox | Recepción de comprobantes | `https://api.comprobanteselectronicos.go.cr/recepcion-sandbox/v1/` | POST | 403 (requiere token) | CRLibre / foros oficiales documentados |
| Sandbox | Identity Provider (token) | `https://idp.comprobanteselectronicos.go.cr/auth/realms/rut-stag/protocol/openid-connect/token` | POST | 405 (es POST, no GET) | CRLibre / foros oficiales documentados |
| Producción | Recepción de comprobantes | `https://api.comprobanteselectronicos.go.cr/recepcion/v1/` | POST | no probado en vivo (solo sandbox) | Documentación pública |
| Producción | Identity Provider (token) | `https://idp.comprobanteselectronicos.go.cr/auth/realms/rut/protocol/openid-connect/token` | POST | no probado en vivo | Documentación pública |
| Documentación | Anexos y estructuras v4.3 | `https://www.hacienda.go.cr/ATV/ComprobanteElectronico/frmAnexosyEstructuras.aspx#` | GET | 403 (acceso restringido geográfico/requiere sesión) | Enlace oficial en CRLibre |
| Documentación | API comprobantes electrónicos | `https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/comprobantes-electronicos-api.html` | GET | 403 (acceso restringido) | Enlace oficial en CRLibe |

**Nota:** Los status 403/405 sin credenciales son **esperados**; confirman que el host y el endpoint existen, no que las credenciales sean válidas.

## 2. Pasos para obtener credenciales de API ATV

> ⚠️ **Acción humana obligatoria.** El registro en ATV y la generación de credenciales son legalmente personales y no pueden ser automatizados por un agente.

1. **Tener firma digital vigente** (tokens o tarjeta criptográfica de Costa Rica) y acceso al portal ATV con usuario y contraseña.
2. Ingresar a `https://atv.hacienda.go.cr/` con la firma digital del representante legal / contador autorizado.
3. Navegar a la sección de **Comprobantes Electrónicos** > **Registro de Sistemas / API**.
   - [PENDIENTE — NO INVENTAR] Captura del menú exacto: la interfaz del portal cambia; confirmar con la guía oficial `Guia_IdP.pdf` publicada por Hacienda (`https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/Guia_IdP.pdf`).
4. Generar / consultar las credenciales de API:
   - **Usuario ATV** (username): el usuario con el que se ingresa al portal.
   - **Contraseña ATV** (password): la contraseña del portal.
   - **Client ID según ambiente**: `api-stag` para sandbox, `api-prod` para producción.
5. Descargar el **certificado .p12** y anotar el **PIN**:
   - En el portal se genera una llave criptográfica asociada al sistema.
   - El archivo suele llamarse `<cedula>.p12` o similar.
   - El PIN es numérico y se entrega en el mismo flujo de generación.
   - [PENDIENTE — NO INVENTAR] Captura del botón de descarga: confirmar en el portal oficial, ya que la ubicación exacta depende de la versión actual del ATV.

## 3. Configuración en el entorno FaberLoom

Una vez obtenidos los datos, configurar en `/opt/faber_loom/.env` (NUNCA en el repo):

```bash
# ATV / Hacienda CR
ATV_USERNAME=el-usuario-atv
ATV_PASSWORD=la-contraseña-atv
ATV_CERT_PATH=/opt/faber_loom/secrets/atv.p12
ATV_CERT_PIN=12345678
ATV_CLIENT_ID=api-stag   # o api-prod en live
ATV_MODE=sandbox         # sandbox | live
```

Copiar el `.p12` a la ruta indicada con permisos restrictivos:

```bash
mkdir -p /opt/faber_loom/secrets
chmod 700 /opt/faber_loom/secrets
cp /ruta/descargada/certificado.p12 /opt/faber_loom/secrets/atv.p12
chmod 600 /opt/faber_loom/secrets/atv.p12
```

## 4. Smoke test: un comando para cerrar E5-4

Con las credenciales en `.env`, correr:

```bash
cd /opt/faber_loom
source .venv/bin/activate
python app/scripts/atv_smoke.py
```

El script:
- Verifica conectividad con los endpoints oficiales.
- Obtiene token OAuth2 del IdP con las credenciales.
- Genera un comprobante de PRUEBA marcado `[SINTETICO]`.
- Firma el XML con el `.p12`.
- Envía al sandbox de Hacienda.
- Escribe `docs/audits/EVIDENCIA_ATV_SANDBOX_<fecha>.md` con la evidencia completa.

Si el script termina con `[OK]`, E5-4 live queda técnicamente cerrado; solo restaría cambiar `ATV_MODE=live` y repetir con el certificado de producción.

## 5. Acciones residuales humanas exactas

1. Registrarse / acceder al ATV con firma digital.
2. Generar/obtener usuario, contraseña, client ID y descargar el `.p12` + PIN.
3. Pegar los valores en `.env` y correr `python app/scripts/atv_smoke.py`.

---

**Referencias oficiales consultadas**
- CRLibre — URL de API de comprobantes electrónicos: `https://crlibre.org/preguntas/url-de-api-de-comprobantes-electronicos/`
- Hacienda CR — Anexos y estructuras: `https://www.hacienda.go.cr/ATV/ComprobanteElectronico/frmAnexosyEstructuras.aspx#`
- Hacienda CR — Guía IdP: `https://www.hacienda.go.cr/ATV/ComprobanteElectronico/docs/esquemas/2016/v4.3/Guia_IdP.pdf`

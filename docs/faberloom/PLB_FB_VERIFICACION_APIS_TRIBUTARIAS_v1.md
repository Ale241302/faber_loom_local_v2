# PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1

**Objetivo:** verificar acceso real a las APIs tributarias oficiales de ATV (Costa Rica), SAT (México) y DIAN (Colombia) antes de encender modos `sandbox` o `live` en producción.

**Timebox:** 3 días hábiles.

**Reglas inviolables:**

* No se inventan URLs, certificados, tokens ni respuestas oficiales.
* Mientras no exista verificación real, los conectores permanecen en modo `mock` o, con credenciales reales, fallan cerrado con `[PENDIENTE — NO INVENTAR]`.
* Todos los secretos (API keys, certificados, contraseñas) se almacenan cifrados por tenant en `TenantSecretStore`; la configuración no secreta vive en `tenant_settings`.

## 1. Conectores soportados

| País | Autoridad | Código | Métodos implementados |
|------|-----------|--------|----------------------|
| Costa Rica | ATV | `atv` | `check_document_status`, `fetch_taxpayer_info` |
| México | SAT | `sat` | `check_document_status`, `fetch_taxpayer_info` |
| Colombia | DIAN | `dian` | `check_document_status`, `fetch_taxpayer_info` |

## 2. Configuración requerida por tenant

### 2.1 Configuración no secreta (`tenant_settings`)

```text
connectors.tax.<authority>.mode              # mock | sandbox | live
connectors.tax.<authority>.base_url          # URL base oficial
connectors.tax.<authority>.document_status_endpoint  # path opcional
connectors.tax.<authority>.taxpayer_info_endpoint    # path opcional
```

### 2.2 Secretos (`TenantSecretStore`)

```text
connectors/tax/<authority>/api_key
connectors/tax/<authority>/api_secret
connectors/tax/<authority>/certificate   # PEM / contenido del certificado (live)
```

## 3. Checklist de verificación

### ATV (Costa Rica)

- [ ] Obtener credenciales de API o certificado firma ante Ministerio de Hacienda.
- [ ] Confirmar URL base oficial y endpoints de consulta de comprobantes y contribuyentes.
- [ ] Verificar que el certificado permite consulta (no solo firma) si aplica.
- [ ] Ejecutar al menos una consulta real de prueba y guardar evidencia en `docs/audits/`.
- [ ] Registrar hallazgos en `ENT_FB_SKILL_CATALOG_v1.1.md` (skill `SKILL_FE_STATUS_CHECK`).

### SAT (México)

- [ ] Confirmar si se usará SOAP/REST y versión del servicio de consulta.
- [ ] Obtener FIEL/CIEC o token de API según el servicio.
- [ ] Verificar URL base y WSDL/endpoint REST.
- [ ] Ejecutar al menos una consulta real de prueba y guardar evidencia.
- [ ] Registrar hallazgos en `ENT_FB_SKILL_CATALOG_v1.1.md`.

### DIAN (Colombia)

- [ ] Obtener credenciales de la API de consulta (software proveedor o token propio).
- [ ] Confirmar URL base y endpoints de estado de documento e información de contribuyente.
- [ ] Verificar cadena de certificados para ambiente de producción/pruebas.
- [ ] Ejecutar al menos una consulta real de prueba y guardar evidencia.
- [ ] Registrar hallazgos en `ENT_FB_SKILL_CATALOG_v1.1.md`.

## 4. Criterio de éxito

* Para cada autoridad verificada, existe un documento de evidencia en `docs/audits/EVIDENCIA_API_<AUTHORITY>_YYYYMMDD.md` con:
  * fecha/hora de la prueba,
  * identificador del comprobante/contribuyente consultado (sin datos sensibles reales),
  * URL/endpoint usado,
  * resumen de la respuesta (HTTP status y validez estructural),
  * nombre de la persona que ejecutó la prueba.
* Los endpoints oficiales se configuran en `tenant_settings` de un tenant canario o de prueba.
* Se actualiza `PLB_FB_VERIFICACION_APIS_TRIBUTARIAS_v1.md` marcando `[VERIFICADO]` en la autoridad correspondiente.

## 5. Pendientes humanos / externos

* Credenciales ATV/SAT/DIAN: `[PENDIENTE — NO INVENTAR]`.
* Certificados digitales vigentes: `[PENDIENTE — NO INVENTAR]`.
* Aprobación de términos de uso de cada API por parte del CEO/socios.

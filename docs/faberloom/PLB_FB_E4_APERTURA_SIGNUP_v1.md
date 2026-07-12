# PLB — Apertura de signup público (E4-7)

## Estado
- **Gate comercial:** cerrado (default `signup.approval = manual`).
- **Capacidad técnica:** lista en modo `auto` bajo defensas configurables.

## Checklist para abrir signup real

1. **Madurez del tenant canario / early-access**
   - [ ] Tenant externo operativo ≥ 30 días.
   - [ ] ≥ 10 casos reales procesados en producción.
   - [ ] 0 fugas cross-tenant confirmadas por la contamination suite E4-8.

2. **Seguridad y defensas**
   - [ ] Captcha provider real configurado (`signup.captcha.provider`).
   - [ ] `signup.captcha.required = true`.
   - [ ] Lista de dominios desechables actualizada (`signup.disposable_domains`).
   - [ ] Límite global diario ajustado al volumen esperado (`signup.daily_limit`).
   - [ ] Rate limit por IP monitoreado (default 5 intentos / 15 min).

3. **Operaciones**
   - [ ] Primera factura pagada por al menos un tenant early-access.
   - [ ] Canal de soporte definido para cuentas auto-aprobadas.
   - [ ] Procedimiento de rollback: setear `signup.approval = manual` y suspender tenant si es necesario.

4. **Monitoreo**
   - [ ] Dashboard de health del tenant expuesto (`/api/admin/metrics`, `/api/admin/tenants/{id}/health`).
   - [ ] Alerta si la tasa de aprobación automática supera umbral o si aparece spike de signups.

## Riesgo residual
- El modo `auto` elimina la revisión humana de platform_admin. Cualquier regresión en las defensas puede exponer la plataforma a spam o tenants maliciosos.

## Owner
- Producto / platform_admin.

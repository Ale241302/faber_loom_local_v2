# PLB_INCIDENT_RESPONSE — Playbook Respuesta a Incidentes
id: PLB_INCIDENT_RESPONSE
status: DRAFT
visibility: [INTERNAL]
version: 1.0
domain: Compliance (IDX_COMPLIANCE)
classification: PLAYBOOK — Instrucciones operativas: qué hacer cuando algo sale mal
aplica_a: [SHARED]

refs:
  - ENT_PLAT_SEGURIDAD (framework de seguridad — estado de controles)
  - ENT_PLAT_INFRA (infraestructura afectada)
  - ENT_GOB_RIESGOS (riesgos estratégicos)

---

## A. Clasificación de incidentes

| Severidad | Definición | Ejemplos | SLA respuesta | SLA resolución |
|-----------|-----------|----------|--------------|---------------|
| CRÍTICA | Acceso no autorizado confirmado, datos expuestos, sistema comprometido | Breach de datos, cuenta comprometida, ransomware, API key en repo público | <1h | <24h (contener) |
| ALTA | Intento de ataque detectado, servicio degradado, vulnerabilidad explotable | Brute force masivo, servicio caído >30min, certificado expirado, secret expuesto internamente | <4h | <48h |
| MEDIA | Vulnerabilidad detectada sin exploit, anomalía en logs, degradación menor | CVE en dependencia, intentos de login fallidos inusuales, backup fallido | <24h | Próximo sprint |
| BAJA | Best practice faltante, actualización disponible, mejora de seguridad | Dependencia desactualizada, header faltante, configuración subóptima | Próximo ciclo mantenimiento | Planificado |

---

## B. Protocolo de respuesta — CRÍTICA y ALTA

### B1. Contener (primeros 60 minutos)

1. **Confirmar:** ¿es real o falso positivo? Verificar logs, no asumir.
2. **Aislar:** si hay acceso no autorizado activo, desconectar el servicio afectado (docker stop, Nginx block IP, revocar token).
3. **Preservar evidencia:** NO borrar logs. Copiar logs relevantes a archivo separado antes de cualquier acción.
4. **Notificar:** CEO inmediatamente. Si Ale está disponible, también.
5. **NO publicar:** no comunicar externamente hasta tener facts confirmados.

### B2. Investigar (horas 1-24)

1. **Alcance:** ¿qué datos fueron accedidos/expuestos? ¿Cuántos usuarios afectados?
2. **Vector:** ¿cómo entraron? (credencial robada, vulnerabilidad, social engineering, insider)
3. **Timeline:** ¿cuándo empezó? ¿Sigue activo?
4. **Impacto:** ¿datos de clientes expuestos? ¿IP expuesta? ¿Financiero?

### B3. Remediar (horas 24-48)

1. **Cerrar el vector:** parchar vulnerabilidad, rotar credenciales, bloquear acceso.
2. **Restaurar:** si hay corrupción de datos, restaurar desde backup verificado.
3. **Verificar:** confirmar que el vector está cerrado y no hay persistence (backdoor, cron malicioso).
4. **Documentar:** registro completo del incidente para post-mortem.

### B4. Comunicar (si aplica)

- **Clientes afectados:** notificar si sus datos fueron expuestos. Ser directo, no minimizar.
- **LGPD (Brasil):** si datos biométricos del scanner fueron expuestos, notificar ANPD (Autoridade Nacional de Proteção de Dados) en 72h. Ref → ENT_COMP_REGULATORIO.
- **Reguladores:** según jurisdicción del dato expuesto.

---

## C. Protocolo de respuesta — MEDIA y BAJA

1. Registrar en ENT_GOB_PENDIENTES con referencia al incidente.
2. Evaluar si requiere acción inmediata o puede esperar al próximo sprint.
3. Si es CVE en dependencia: verificar si es explotable en nuestro contexto. Si sí → promover a ALTA.
4. Ejecutar fix en el siguiente ciclo de mantenimiento.

---

## D. Contactos de emergencia

| Rol | Nombre | Canal primario | Canal backup |
|-----|--------|---------------|-------------|
| CEO / Decisor | Santiago | Teléfono: [PENDIENTE] | Email: [PENDIENTE] |
| Dev / Ejecutor técnico | Alejandro | WhatsApp: [PENDIENTE] | Email: [PENDIENTE] |
| Hosting (KVM) | [PENDIENTE — proveedor] | [PENDIENTE] | [PENDIENTE] |
| Dominio/DNS | [PENDIENTE — registrador] | [PENDIENTE] | [PENDIENTE] |

---

## E. Post-mortem (después de cada incidente CRÍTICA o ALTA)

Dentro de 7 días del cierre del incidente, documentar:

```
Incidente: [nombre descriptivo]
Fecha detección: [fecha]
Fecha contención: [fecha]
Fecha resolución: [fecha]
Severidad: CRÍTICA / ALTA
Vector: [cómo ocurrió]
Impacto: [qué datos/servicios se afectaron]
Root cause: [causa raíz]
Acciones tomadas: [lista]
Acciones preventivas: [qué se cambia para que no pase de nuevo]
Lecciones: [qué aprendimos]
```

Archivo: crear REPORTE_INCIDENTE_{FECHA}.md en la KB.

---

## F. Simulacro

Cada 6 meses (cuando haya capacidad operativa), simular:
- Restauración de backup completo (PostgreSQL + MinIO + configs)
- Revocación y re-emisión de JWT/API keys
- Bloqueo de IP atacante en Nginx

[PENDIENTE — primer simulacro cuando los procesos de backup estén implementados]

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO

Changelog:
- v0.1 (2026-03-14): stub creado para resolver referencia rota desde ENT_COMP_ISO_ROADMAP.md. Ola E3.
- v1.0 (2026-03-15): STUB → DRAFT. Clasificación 4 niveles, protocolo CRÍTICA/ALTA (contener→investigar→remediar→comunicar), contactos, post-mortem, simulacro. Ref LGPD para datos biométricos.

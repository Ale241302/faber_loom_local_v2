# SPEC_FB_WORKSPACE_v1 -- Workspace Conversacional FaberLoom
id: SPEC_FB_WORKSPACE_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: ENT_FB_DECISIONES_E1_v1.md · SPEC_FB_ROUTINES_v1.md

---

## Declaracion

El Workspace es donde el usuario construye, itera y automatiza.
Distinto de WorkLoom (donde opera y aprueba).

WorkLoom = TRABAJO del dia (que tengo que hacer YO)
Workspace = SISTEMA vivo + CONSTRUCCION (como esta MI MAQUINA)

Existe solo en desktop Electron en E1.
La web app tiene Agent Factory y Skill Factory pero no Workspace.

---

## 1. Layout 3 columnas

COL IZQ: conversaciones recientes + [+ Nueva conv]
COL CENTRO: welcome compacto + stream + composer fijo + patrones
COL DER: Tab Agentes / Tab Skills / Tab Aprendizaje / Contexto activo

Composer fijo: [+ Archivo] [+ Knowledge] [@mencion] [Modo] [Enviar]
Atajos: A=aprobar E=editar R=regenerar I=info S=escalar D=descartar

Breakpoints Electron:
  >= 1400px: 3 columnas full
  1100-1399px: col izq como drawer FAB
  < 1100px: ambas laterales como drawers

---

## 2. Los 3 modos (deteccion automatica)

### Modo 1 -- OPERACIONAL

Trigger: usuario invoca agentes existentes para tarea inmediata.
Senales: @agente + verbo, pregunta directa, solicitud inmediata.
Resultado: agentes en secuencia lineal, output a WorkLoom si HITL requerido.
Working memory: se descarta al cerrar la conversacion.
NO crea agentes ni rutinas.

### Modo 2 -- AUTOMATIZACION

Trigger: usuario describe algo que quiere automatico.
Senales: cuando llegue, cada dia, automaticamente, avisame si.
Resultado: propuesta de rutina --> SANDBOX --> Owner aprueba --> ACTIVE.
Ver SPEC_FB_ROUTINES_v1 para flujo completo.

### Modo 3 -- CONSTRUCCION

Trigger: sistema detecta gap (tarea sin agente, flujo sin automatizar).
Resultado: propuesta de agente nuevo con AgentSpec pre-completado.
Agente --> shadow --> Agent Factory --> Owner aprueba --> active.

Restricciones TIER 1 modos 2 y 3:
  HITL absoluto: nada va a PROD sin firma Owner/Admin
  Single-agent por task: agentes nuevos son atomicos
  Sandbox obligatorio antes de promote
  Audit log con actor_role_at_decision

---

## 3. Panel derecho -- 4 tabs

### Tab Agentes
Por categoria (Canal / Recurso / Cognitivo / Proceso):
  @mail_ventas [ON] estado: active
  @cotizador [ON] estado: active
  @seguidor [ON] estado: active, ultimo run: 2h
Acciones: switch ON/OFF, [@mencion rapida] inserta en composer

### Tab Skills
SEALED (FaberLoom, con candado): no editables
CUSTOM (tenant): editables en Skill Factory
Por skill: nombre, archetype, estado, autonomy_ceiling, thermometer

### Tab Aprendizaje
Gold samples candidatos con [Aprobar y guardar] [Mantener] [Descartar]
Reglas candidatas con [Activar] [Mantener] [Descartar]
Estado: 78/100 -- Produccion sin cambios recientes

### Contexto activo (fijo abajo)
Knowledge: kb_marluvas v2.3 -- 18.4k -> 5.8k (68% cache)
Caso activo: RFQ Sondel #4521 (si hay uno abierto)
Freshness: precios vigentes hasta 2026-07-01
Tokens: 5.8k / 50k budget
[Ver contexto completo] --> drawer con 6 secciones

---

## 4. Inbound activo usuario (tipos 12-13)

Tipo 12 -- Upload archivo:
  Formatos: PDF, DOCX, XLSX, CSV, TXT, PNG, JPG
  Max: 10MB por archivo, 50MB por sesion
  Path MinIO: /tenants/{tenant_id}/uploads/
  Flujo: archivo --> L1 clasifica data_class --> feed.item.received
  Si N3/N4: hard gate D9, no sale a providers sin DPA

Tipo 13 -- Inicio de tarea:
  Usuario escribe o arrastra --> task (invocation_mode=ad_hoc)
  WorkLoom si requires_human_gate=true
  Ejecucion directa si autonomy_ceiling lo permite

---

## 5. SpaceLoom en E1

No es espacio separado en E1.
Existe como boton [Pensar con IA] en cards de casos complejos WorkLoom.
Abre panel lateral en Workspace con contexto del caso pre-cargado.
Output: instruccion al agente --> WorkLoom como draft listo.

Post-beta: si >40% de casos usan este modo, SpaceLoom se convierte
en espacio propio con persistencia de sesiones.

---

## 6. Working memory

Se crea al abrir conversacion, contiene contexto + historial + agentes.
Se descarta al cerrar (sin gate humano nunca va a Persistent memory).
Timeout: 24h sin actividad --> descarte automatico.

---

## 7. Conversaciones recientes

Ultimas 30 por usuario por tenant.
Nombre auto-generado del primer mensaje.
Indicador de modo + tipo de output producido.

---
Changelog:
- v1.0 (2026-06-24): Creacion. Layout 3 columnas. 3 modos.
  Panel derecho 4 tabs. Inbound 12-13. SpaceLoom E1.
  Cubre gap G2. Alineado con ENT_FB_DECISIONES_E1_v1 D4.

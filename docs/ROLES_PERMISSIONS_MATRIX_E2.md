# Matriz de roles y permisos — E2

**id:** ROLES_PERMISSIONS_MATRIX_E2  
**versión:** 1.0  
**fecha:** 2026-07-06  
**estado:** versionada antes de E2-2  

---

## 1. Roles operativos

| Rol | Descripción | Equivalente Foundation (hoy) |
|---|---|---|
| **CEO / Owner** | Control total del tenant; puede otorgar/quitar roles, configurar presupuestos globales y aprobar excepciones. | `owner` |
| **Curador** | Revisa calidad de KB, gold loop, rutinas publicadas y WorkLoom. No ejecuta acciones irreversibles sin segundo gate. | `admin` |
| **AM (Account Manager)** | Opera el día a día: chat, drafts, rutinas, inbox, WorkLoom. No promueve a gold sin verificación ni administra usuarios. | `operator` |
| **Viewer** | Solo lectura en workspaces asignados. | `viewer` |
| **Admin técnico** | Configura routing, proveedores, budgets técnicos, objetos/MinIO. No accede a datos de negocio sin workspace asignado. | `admin` + scope técnico |

---

## 2. Matriz de permisos por área

### 2.1 WorkLoom

| Acción | CEO | Curador | AM | Viewer | Admin técnico |
|---|---|---|---|---|---|
| Ver cola propia/equipo | ✅ | ✅ | ✅ | ✅* | ❌ |
| Tomar item | ✅ | ✅ | ✅ | ❌ | ❌ |
| Reasignar item | ✅ | ✅ | ✅ (propios) | ❌ | ❌ |
| Resolver item reversible | ✅ | ✅ | ✅ | ❌ | ❌ |
| Resolver item irreversible | ✅ | ✅ (con doble confirmación) | ❌ | ❌ | ❌ |
| Ver métricas de equipo | ✅ | ✅ | ✅ | ✅* | ❌ |

\* Viewer solo ve items públicos/no-confidenciales del workspace.

### 2.2 Knowledge Base

| Acción | CEO | Curador | AM | Viewer | Admin técnico |
|---|---|---|---|---|---|
| Ver fuentes y hechos | ✅ | ✅ | ✅ | ✅ | ❌ |
| Ingestar fuente | ✅ | ✅ | ✅ | ❌ | ❌ |
| Editar fuente propia | ✅ | ✅ | ✅ (propias) | ❌ | ❌ |
| Borrar fuente | ✅ | ✅ (doble confirmación) | ❌ | ❌ | ❌ |
| Aprobar hecho duro/gold | ✅ | ✅ (segundo gate) | ❌ | ❌ | ❌ |

### 2.3 Rutinas (Skills / Agents / Templates)

| Acción | CEO | Curador | AM | Viewer | Admin técnico |
|---|---|---|---|---|---|
| Ver rutinas activas | ✅ | ✅ | ✅ | ✅ | ✅ (técnicas) |
| Crear rutina personal | ✅ | ✅ | ✅ | ❌ | ❌ |
| Editar rutina propia | ✅ | ✅ | ✅ (propias) | ❌ | ❌ |
| Aprobar rutina (HITL) | ✅ | ✅ | ❌ | ❌ | ❌ |
| Ejecutar rutina aprobada | ✅ | ✅ | ✅ | ❌ | ❌ |
| Promover a gold | ✅ | ✅ (segundo gate) | ❌ | ❌ | ❌ |

### 2.4 Routing y modelos

| Acción | CEO | Curador | AM | Viewer | Admin técnico |
|---|---|---|---|---|---|
| Ver catálogo de modelos | ✅ | ✅ | ✅ | ✅ | ✅ |
| Configurar allowlist por workspace | ✅ | ✅ | ❌ | ❌ | ✅ |
| Configurar presupuesto por workspace | ✅ | ✅ | ❌ | ❌ | ✅ |
| Configurar proveedor/key gestionada | ✅ | ❌ | ❌ | ❌ | ✅ |
| Ver ledger de costos | ✅ | ✅ | ✅ (propios) | ❌ | ✅ |

### 2.5 Budgets

| Acción | CEO | Curador | AM | Viewer | Admin técnico |
|---|---|---|---|---|---|
| Ver presupuesto restante | ✅ | ✅ | ✅ | ✅ | ✅ |
| Configurar cap global | ✅ | ✅ | ❌ | ❌ | ✅ |
| Configurar cap por workspace | ✅ | ✅ | ❌ | ❌ | ✅ |
| Solicitar excepción | ✅ | ✅ | ✅ | ❌ | ❌ |

### 2.6 Objetos / MinIO (E2-6)

| Acción | CEO | Curador | AM | Viewer | Admin técnico |
|---|---|---|---|---|---|
| Ver objetos del workspace | ✅ | ✅ | ✅ | ✅ | ❌ |
| Subir archivo | ✅ | ✅ | ✅ | ❌ | ❌ |
| Generar presigned URL de descarga | ✅ | ✅ | ✅ | ✅ | ❌ |
| Borrar objeto | ✅ | ✅ (doble confirmación) | ❌ | ❌ | ✅ (bucket) |
| Configurar bucket/políticas | ✅ | ❌ | ❌ | ❌ | ✅ |

---

## 3. Segundo gate gold

| Paso | Actor | Registro obligatorio |
|---|---|---|
| Run genera candidate | AM (ejecutor) | `approved_by` = AM |
| Promoción a gold | Curador/CEO | `approved_by` ≠ `verified_by` |
| Aplicación a rutina | Curador/CEO | `gold_candidate.applied_to_routine` audit event |

**Regla:** quien aprueba el run no puede ser quien verifica la promoción a gold cuando el candidate contiene campos duros (precios, SKUs, stock, fechas). La columna `gold_candidate.verified_by` registra al verificador independiente.

---

## 4. Implementación en E2-2

1. Mapear roles operativos a `fnd_roles` de Foundation (posiblemente renombrar `operator` → `am`, `admin` → `curador` + `admin_tecnico`).
2. Añadir permisos granulares en `SYSTEM_ROLES` de Foundation.
3. Middleware/dependency `require_permission(permission: str)` en endpoints.
4. UI: ocultar/desactivar acciones no permitidas en lugar de confiar en el backend.
5. Tests: `test_e2_2_rbac_*` para cada combinación rol/acción crítica.

---

## 5. Referencias

- `app/src/foundation/core.py` (`SYSTEM_ROLES`)
- `app/src/foundation/m09_rbac.py`
- `app/src/gold.py` (`promote_gold_candidate`)
- `app/tests/test_e2_0_gold_second_gate.py`
- `docs/CONTEXT_RLS_CONTRACT_E2.md`

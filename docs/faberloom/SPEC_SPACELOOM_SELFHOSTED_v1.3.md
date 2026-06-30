---
id: SPEC_SPACELOOM_SELFHOSTED_v1_3
version: 1.3
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: DRAFT 2026-06-17 - decision de distribucion: app instalable Win/Mac (unica forma de producto)
fecha: 2026-06-17
agente: Claude (Cowork) - Arquitecto Ejecutor
extiende: SPEC_SPACELOOM_SELFHOSTED_v1.1 + v1.2 (todo lo no tocado sigue vigente)
---

# SPEC_SPACELOOM_SELFHOSTED_v1.3 (addendum)
## Distribucion: app de escritorio instalable Win/Mac

> Reemplaza la seccion de distribucion de v1.1. El motor (FastAPI + SQLite/FTS5 + LiteLLM) y el
> modelo de agente (v1.2) NO cambian. Cambia solo el envoltorio (shell) y el empaque.

## A. Decision

La unica forma viable de producto es una **app de escritorio instalable (Windows y macOS)**: doble clic,
ventana nativa, sin terminal, sin navegador, sin localhost a la vista. La audiencia (profesionales no
tecnicos, y Alvaro) no usa CLI. `uvx`/`docker` dejan de ser canal de producto y quedan SOLO como loop
de desarrollo interno.

## B. Stack del shell (recomendado, con el porque)

**pywebview + PyInstaller (o Briefcase) — 100% Python.** El mismo motor FastAPI+SQLite+LiteLLM corre
embebido; pywebview lo muestra en una ventana nativa (WKWebView en Mac, WebView2 en Windows). La UI sigue
siendo web (HTML/CSS/JS) pero renderizada como app, no en pestana de browser.

Por que esto y no Tauri/Electron:
- **pywebview/PyInstaller:** un solo lenguaje (tu stack), sin Rust ni Node, empaqueta el motor que ya
  especificamos. El camino mas corto de codigo-a-.app/.exe.
- **Tauri** (Rust + webview, bundle de sidecar Python): shell mas chico/rapido, pero suma Rust y
  complejidad de sidecar. Solo si despues querés bajar peso. NO en v1.
- **Electron:** descartado, binario pesado y dos runtimes.

## C. Lo que cambia (y lo que no)

No cambia: motor, esquema SQLite, modelo de agente (v1.2), runtime guarantees, seguridad, licencia.
Cambia:
- **Datos:** carpeta de datos por OS (`~/Library/Application Support/SpaceLoom` en Mac, `%APPDATA%\SpaceLoom` en Win). Backup = copiar esa carpeta.
- **API key:** keyring nativo del OS (Keychain / Credential Manager), no archivo plano. Mas seguro que la opcion de v1.1.
- **Sin puerto expuesto / CSRF de browser:** la webview es same-origin local; desaparece esa clase de riesgo.

## D. Realidad honesta del desktop (costos y trabajo que SI o SI aparecen)

El desktop es el canal correcto para tu audiencia, pero es el **mas caro de shippear bien**. No lo maquillo:
- **Firma de codigo / notarizacion:** sin firmar, Gatekeeper (Mac) y SmartScreen (Win) asustan al usuario no-tecnico con "app no verificada". Necesitas: Apple Developer (USD 99/ano) + notarizacion; certificado Windows code-signing (~USD 100-400/ano). Es requisito, no lujo, para esta audiencia.
- **Auto-update:** una app distribuida necesita actualizarse. Minimo viable: "check de version + descarga + reinstala"; mejor: Sparkle (Mac) / WinSparkle (Win). Puede ser basico en v1, pero tiene que existir.
- **Quirks por OS:** WebView2 (Win) requiere runtime (auto-instalable); WKWebView (Mac) difiere en JS/CSS. Probar en ambos, no asumir.

## E. Disciplina de desarrollo (no empaquetar cada iteracion)

Durante el build corres el motor por `python -m spaceloom` / `uvx` (rapido, recarga en caliente). El
empaque desktop (pywebview + PyInstaller + firma) se hace **en SL4**, no en cada commit. Asi mantenes el
loop de dogfood rapido y dejas el costo de empaque para el final.

## F. Etapas - delta sobre v1.1/v1.2

- SL0-SL3.5: se corren via `python -m`/uvx (dev loop). El gate de "instalable" NO aplica aca.
- **SL4 se redefine: "Desktop app firmada Win/Mac".** Sub-tareas:
  1. Wrap del motor en pywebview (ventana nativa).
  2. Empaque PyInstaller/Briefcase -> .app (Mac) + instalador (Win).
  3. Firma + notarizacion (ambos OS).
  4. Auto-update basico.
  5. Carpeta de datos por OS + key en keyring + first-run (pedir API key).
  Gate SL4: **un profesional no-tecnico instala con doble clic y corre una tarea real sin terminal ni ayuda.**
  Estimacion SL4 sube de 2 a ~3 semanas (firma/notarizacion/auto-update son trabajo real). Total ~11.5-12 sem.

## G. Changelog

- v1.3 (2026-06-17): distribucion = app instalable Win/Mac (unica forma de producto); uvx/docker degradados a dev-loop interno. Shell recomendado pywebview + PyInstaller (100% Python); Tauri/Electron descartados para v1. Datos por carpeta-OS, API key en keyring nativo. Flag honesto de costos: firma de codigo + notarizacion + auto-update. SL4 redefinido a "desktop app firmada" (~3 sem). No cambia motor ni modelo de agente. No toca FROZEN.

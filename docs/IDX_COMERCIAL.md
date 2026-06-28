# Índice comercial — SpaceLoom SL1b

> **⚠️ DEMO / FALLBACK — NO SON DATOS REALES DE MWT**
>
> Este índice y las entidades vinculadas (`ENT_COMERCIAL_*`) contienen datos
> sintéticos usados únicamente para cerrar el hito SL1b con dogfood reproducible.
> Los datos comerciales reales de MWT están pendientes de entrega por parte del
> CEO (ítem PRC-01 del `PROCUREMENT_LEDGER.md`). Hasta entonces, todo campo no
> cubierto por estas fuentes demo se reportará como `[PENDIENTE — NO INVENTAR]`.

## Fuentes disponibles

| Entidad | Archivo | Tipo | Frescura default |
|---|---|---|---|
| Productos | `ENT_COMERCIAL_PRODUCTOS.md` | md | 90 días |
| Precios | `ENT_COMERCIAL_PRECIOS.md` | md | 30 días |
| Stock | `ENT_COMERCIAL_STOCK.md` | md | 7 días |
| Equivalencias | `ENT_COMERCIAL_EQUIVALENCIAS.md` | md | 90 días |
| Términos comerciales | `ENT_COMERCIAL_TERMINOS.md` | md | 90 días |

## Prompts de dogfood SL1b

Ver `harness/prompts/sl1b_dogfood_prompts.json`.

## Estado de sourcing

- `fully_sourced`: campo duro con fuente demo.
- `[PENDIENTE — NO INVENTAR]`: campo duro no cubierto por fuente demo; el draft
  debe dejar el placeholder explícito.

## DIMENSIÓN 6 — Document Processing y B2B Workflow

> **Fecha investigación:** 2026-04-30  
> **Ámbito:** Skills para procesar/generar PDFs, Excel, Word a escala en flujos B2B (MWT = Marluvas/Tecmater; FB = FaberLoom).  
> **Regla:** Solo skills con URL verificable. Skills ya instaladas excluidas por mandato (`anthropic-skills/*`, `obra/superpowers`, Cowork core).

---

### Skills relevantes encontrados

| Skill | Repo | Instalación | Score MWT | Score FB | Por qué (1 línea) |
|---|---|---|---|---|---|
| **nutrient-document-processing** | `PSPDFKit-labs/nutrient-agent-skill` | `npx skills add PSPDFKit-labs/nutrient-agent-skill` | **ALTO** | **ALTO** | OCR multilenguaje (20+), extracción de tablas de catálogos PDF, conversión PDF↔DOCX/XLSX/PPTX, firma digital, redacción PII, fill forms. Requiere API key de Nutrient (commercial). |
| **kreuzberg** | `kreuzberg-dev/kreuzberg` | `npx skills add kreuzberg-dev/kreuzberg` | **ALTO** | **ALTO** | Extracción de texto, tablas, metadata e imágenes de 97+ formatos. OCR con Tesseract/EasyOCR/PaddleOCR. Core Rust, bindings Python/Node.js. Ideal para parsear fichas técnicas de calzado en PDF. |
| **pdf-creator** | `daymade/claude-code-skills` (daymade-docs suite) | `claude plugin install daymade-docs@daymade-skills` → `/daymade-docs:pdf-creator` | MEDIO | ALTO | Genera PDF profesionales desde Markdown con WeasyPrint/Chrome. Soporte CJK (chino/japonés/coreano). Temas parametrizados (formal, warm-terra). Útil para cotizaciones B2B con branding Marluvas/Tecmater. |
| **excel-automation** | `daymade/claude-code-skills` | `claude plugin install excel-automation@daymade-skills` | ALTO | ALTO | Creación de Excel formateado vía `openpyxl`, parser de `.xlsm` complejos con stdlib XML/ZIP, control Excel macOS via AppleScript. Perfecto para fichas técnicas paramétricas y cotizaciones con tablas de precios. |
| **doc-to-markdown** | `daymade/claude-code-skills` (daymade-docs) | `claude plugin install daymade-docs@daymade-skills` → `/daymade-docs:doc-to-markdown` | MEDIO | MEDIO | Convierte documentos Office a Markdown para pipeline RAG. Útil para ingestar fichas técnicas históricas de Marluvas/Tecmater en FaberLoom. |
| **contract-review** | `claude-office-skills/skills` | Copiar carpeta `contract-review/` a `.claude/skills/` o usar `install.sh --category legal` | MEDIO | BAJO | Análisis de riesgos en contratos B2B, clause-by-clause. No es específico de calzado/LATAM pero aplicable a contratos de distribución MWT. |
| **invoice-generator** | `tmigone/skills` (OpenClaw registry) | `npx skills add tmigone/invoice-generator` o vía clawhub | ALTO | MEDIO | Genera PDF invoices desde JSON con script Bash/Node.js. Template parametrizable. Podría adaptarse para cotizaciones Marluvas/Tecmater. |
| **invoice-organizer** | `ComposioHQ/awesome-claude-skills` | Copiar `invoice-organizer/SKILL.md` a `.claude/skills/` | MEDIO | BAJO | Extrae datos de invoices PDF/imágenes, renombra, organiza por categoría y genera CSV. Útil para procesar remisiones/facturas entrantes de clientes LATAM. |
| **pdf-ocr** | `claude-office-skills/skills` (OpenClaw) | Instalar vía `install.sh --category pdf` | MEDIO | ALTO | OCR de PDFs escaneados con PaddleOCR (100+ idiomas). Escritorio/batch processing. Ideal para digitalizar catálogos físicos de calzado. |
| **doc-parser** | `claude-office-skills/skills` (basado en `docling`) | Instalar vía `install.sh --category parsing` | MEDIO | ALTO | Parser de IBM para layouts complejos. Extrae tablas, jerarquía, imágenes de PDF/DOCX. Excelente para fichas técnicas con tablas de especificaciones técnicas. |
| **table-extractor** | `claude-office-skills/skills` (basado en `camelot`) | Instalar vía `install.sh --category parsing` | ALTO | BAJO | Extracción precisa de tablas de PDFs. Crítico para extraer tablas de tallas, materiales, normas técnicas de catálogos Marluvas/Tecmater. |
| **translate-book** | `deusyu/translate-book` | `npx skills add deusyu/translate-book` | MEDIO | BAJO | Traducción paralela de libros/documentos (PDF/DOCX/EPUB) con subagentes. Útil para traducir fichas técnicas portugués→español para clientes LATAM. |
| **write-concisely** | `NeoLabHQ/context-engineering-kit` (docs suite) | `npx skills add NeoLabHQ/context-engineering-kit` → `/write-concisely` | BAJO | MEDIO | Aplica principios de *The Elements of Style* a documentación. Mejora redacción de fichas técnicas y propuestas comerciales. |
| **charlie-cfo-skill** | `EveryInc/charlie-cfo-skill` | `npx skills add EveryInc/charlie-cfo-skill` | MEDIO | BAJO | Framework financiero para startups (cash management, unit economics, forecasting). Aplicable a análisis financiero de cotizaciones B2B y runway de MWT. |
| **awesome-legal-skills** | `lawvable/awesome-legal-skills` | `git clone https://github.com/lawvable/awesome-legal-skills.git` + copiar skills individuales | MEDIO | BAJO | 42 skills legales: NDA review, tech contract negotiation, GDPR compliance, debt recovery. Útil para contratos de distribución internacional de calzado. |
| **contract-review (CUAD)** | `evolsb/claude-legal-skill` | `git clone https://github.com/evolsb/claude-legal-skill ~/.claude/skills/contract-review` | MEDIO | BAJO | Review de contratos basado en dataset CUAD. F1 ~0.62 en extracción de cláusulas. First-pass review para contratos B2B de distribución. |

---

### Skills descartados (mencionados pero no aplica)

| Skill | Razón descarte |
|---|---|
| `anthropic-skills/pdf`, `docx`, `xlsx`, `pptx` | **Ya instalados** por mandato de la misión. No se pueden recomendar. |
| `anthropic-skills/schedule` | Ya instalado. |
| `obra/superpowers` y sub-skills (`writing-plans`, `executing-plans`, `verification-before-completion`, `writing-skills`) | Ya instalados. |
| `openaccountants/openaccountants` | 371 tax skills para 134 países. Especializado en impuestos personales/empresariales USA/EU. Brasil/México/Colombia no están en el top de cobertura. No aplica a document processing de calzado. |
| `tax-organizer` (`elderengineer/tax-organizer`) | Especializado en W-2, 1099s, IRS USA. Cero relevancia para B2B LATAM de calzado. |
| `claude-seo` (`AgriciDaniel/claude-seo`) | Skill de SEO técnico con 19 sub-skills. No tiene dimensión document processing ni B2B workflow. |
| `ai-legal-claude` (`zubair-trabzada`) | 14 skills legales genéricas. Menor calidad que `lawvable/awesome-legal-skills`. Descartado por duplicación inferior. |
| `invoice-reconciliation` (mcpmarket.com) | Listado en MCP Market con 11 estrellas, pero **no se encontró repositorio GitHub verificable**. Posiblemente es un skill generado/curado sin repo propio. No cumple regla de URL verificable. |
| `financial-reconciliation` (mcpmarket.com) | Similar al anterior: listado en marketplace sin repo verificable. No se puede instalar vía `npx skills add`. |
| `pdf-processor` (`trilogy-group`) | Skill de Smithery con OCR, pero es un listing de marketplace sin instalación estándar. Requiere configuración manual extensa. No aporta valor incremental sobre nutrient/kreuzberg. |
| `norman-overdue-reminders` / `smartbill-invoicing` | Skills de nicho (reminders alemán / SmartBill.ro API rumana). Sin relevancia para LATAM. |
| `ppt-creator` (`daymade-docs`) | Genera presentaciones. MWT no mencionó necesidad de PPT en su flujo B2B. |
| `meeting-minutes-taker` (`daymade`) | No aplica a document processing ni flujo B2B de calzado. |
| `deep-research` (`daymade`) | Genera reportes de investigación. No específico a documentos ni B2B. |
| `prompt-optimizer`, `skill-creator`, `skill-reviewer` | Meta-skills. No aportan document processing directo. |

---

### Gaps detectados (skills que MWT/FB debería escribir)

| Nombre propuesto | Justificación | Para MWT o FB | Prioridad |
|---|---|---|---|
| **ficha-tecnica-extractor** | Ningún skill del ecosistema está entrenado para extraer automáticamente especificaciones técnicas de calzado industrial (normas SRA, puntera de acero, suela PU/nitrilo, CA/EP de Brasil) desde catálogos PDF de Marluvas/Tecmater. Kreuzberg y Nutrient extraen texto/tablas genéricas, pero no entienden el dominio del calzado de seguridad. | MWT | **P0 — Crítica** |
| **cotizacion-b2b-marluvas** | No existe skill que genere cotizaciones parametrizadas con templates de marca (logo Marluvas/Tecmater, tablas de precios por volumen, condiciones de pago LATAM, INCOTERMS). `tmigone/invoice-generator` es genérico JSON→PDF. | MWT | **P0 — Crítica** |
| **licitaciones-latam-parser** | Cero skills para parsear carteles de licitaciones públicas de México (Compranet), Colombia (SECOP), Chile (ChileCompra), Perú (OSCE). MWT vive de licitaciones. Necesita extraer requisitos, fechas, pliegos, formatos de entrega. | MWT | **P1 — Alta** |
| **conciliacion-po-factura-remision** | No existe skill de 3-way matching para flujo B2B brasileño: Purchase Order (pedido) → Remisión (nota de entrega) → Factura. El `invoice-reconciliation` de MCP Market no tiene repo verificable. MWT necesita validar cantidades, precios, CA/EP por lote. | MWT | **P1 — Alta** |
| **invoice-parser-latam** | Los skills de invoice organizer existentes (ComposioHQ) están optimizados para tax prep USA (W-2, 1099). Ninguno maneja layout típico de notas fiscales brasileñas (NF-e), CFDI México, factura electrónica Colombia UBL 2.1. | MWT | **P1 — Alta** |
| **docx-template-autofill** | Aunque `docxtpl` existe en `claude-office-skills`, no hay un skill que orqueste autofill de templates DOCX con datos extraídos de fichas técnicas. FaberLoom necesita esto para generar documentos automáticamente. | FB | **P2 — Media** |
| **batch-pdf-catalog-processor** | Ningún skill hace batch processing específico de catálogos de producto: extraer SKU, descripción, precio, imagen, tabla de tallas de múltiples PDFs y generar JSON/Excel unificado. Nutrient y Kreuzberg son genéricos. | MWT + FB | **P2 — Media** |
| **translate-pt-es-technical** | `deusyu/translate-book` traduce libros enteros. MWT necesita traducción técnica específica portugués (Brasil) → español (LATAM) con glosario de términos de calzado de seguridad (biqueira de aço → puntera de acero). | MWT | **P2 — Media** |
| **proposal-writer-b2b-latam** | `claude-office-skills` tiene `proposal-writer` genérico. Falta skill con conocimiento de cultura comercial LATAM, formalismos de propuestas técnicas, términos de garantía de calzado industrial. | MWT | **P3 — Baja** |

---

### Caveats técnicos

- **Nutrient API key:** El skill `PSPDFKit-labs/nutrient-agent-skill` requiere `NUTRIENT_API_KEY` (producto comercial). Sin API key el skill no opera. Costo por crédito de procesamiento. No es self-hosted.
- **Kreuzberg licencia:** `kreuzberg-dev/kreuzberg` usa Elastic License 2.0 (ELv2), **no es MIT/Apache**. Restricciones en uso como servicio gestionado. Verificar compatibilidad con modelo de negocio de FaberLoom antes de adopción comercial.
- **Kreuzberg dependencias:** OCR requiere instalar backends adicionales (`pip install kreuzberg[easyocr]`, Tesseract system dependency). En macOS/Linux requiere `tesseract-ocr` + language packs (`tesseract-ocr-spa`, `tesseract-ocr-por` para LATAM).
- **daymade skills vía plugin:** `daymade-docs`, `excel-automation`, etc. se instalan vía `claude plugin install` (plugin marketplace de Claude Code), **no** vía `npx skills add`. Son plugins, no skills estándar del ecosistema skills.sh. Pueden no ser portables a Codex/Cursor sin adaptación.
- **claude-office-skills:** Es una colección de **136+ skills** sin packaging unificado. La instalación vía `install.sh` copia carpetas masivamente. Puede generar bloat de contexto si se instalan todas las categorías. Recomendado: instalar solo skills individuales (`contract-review`, `pdf-ocr`, `table-extractor`).
- **PaddleOCR (Smart OCR):** Soporta español y portugués, pero la precisión en documentos técnicos con tablas complejas (fichas técnicas de calzado) puede requerir fine-tuning o pre-procesamiento de imágenes.
- **Camelot (Table Extractor):** Extrae tablas de PDFs basado en líneas/bordes. Si las fichas técnicas de Marluvas/Tecmater usan tablas sin bordes visibles (solo espaciado), Camelot fallará. Recomendado evaluar con `flavor='stream'` vs `flavor='lattice'`.
- **Invoice-generator (tmigone):** Genera invoices desde JSON. No tiene capacidad de OCR ni extracción de datos de PDFs existentes. Es generador puro, no parser.
- **translate-book (deusyu):** Requiere Calibre (`ebook-convert`) + Pandoc instalados en el sistema. No es un skill standalone; depende de binarios externos. Además, está optimizado para libros, no para documentos técnicos cortos.
- **Conflictos potenciales:** `kreuzberg` y `nutrient-agent-skill` pueden competir por el mismo trigger ("procesa este PDF"). Recomendado instalar solo uno por proyecto o definir `CLAUDE.md` con reglas de precedencia explícitas.
- **Falta de skills.sh indexación:** Muchos skills valiosos (`daymade/*`, `claude-office-skills/*`, `lawvable/*`) **no aparecen en skills.sh** (el índice oficial de Vercel). Están en GitHub directamente o en marketplaces alternativos (ClawHub, OpenClaw). La búsqueda en skills.sh con keywords "invoice", "pdf", "ocr" retorna 0 resultados relevantes para B2B document processing.

---

### Fuentes consultadas

- `skills.sh` — búsquedas: document, pdf, excel, invoice, ocr, contract, quote (resultados limitados para B2B)
- `clawskills.sh` / OpenClaw registry — búsquedas: invoice-generator, pdf-ocr, doc-parser
- GitHub repos verificados: `PSPDFKit-labs/nutrient-agent-skill`, `kreuzberg-dev/kreuzberg`, `daymade/claude-code-skills`, `claude-office-skills/skills`, `lawvable/awesome-legal-skills`, `evolsb/claude-legal-skill`, `deusyu/translate-book`, `NeoLabHQ/context-engineering-kit`, `EveryInc/charlie-cfo-skill`, `tmigone/skills`, `ComposioHQ/awesome-claude-skills`, `alirezarezvani/claude-skills`
- Artículos/ecosistemas: `VoltAgent/awesome-agent-skills`, `heilcheng/awesome-agent-skills`, `junminhong/awesome-agent-skills`, `firecrawl.dev/blog/best-claude-code-skills`, `growthexe.substack.com` (1,116 skills catalogados)
- MCP Market listings (invoice-reconciliation, financial-reconciliation) — descartados por falta de repo verificable

---

### Resumen ejecutivo

**Skills directamente aplicables encontrados: 16.**  
**Skills descartados (ya instalados / no verificables / no aplica): 17.**  
**Gaps detectados que requieren escritura interna: 9** (4 P0/P1 críticos para MWT, 3 para FaberLoom).

**Recomendación inmediata para MWT:**
1. Instalar `kreuzberg-dev/kreuzberg` para extraer tablas de fichas técnicas PDF.
2. Instalar `tmigone/invoice-generator` como base para cotizaciones parametrizadas (requiere adaptación de template).
3. Escribir **urgentemente** `ficha-tecnica-extractor` y `cotizacion-b2b-marluvas` como skills propietarios — no existen en el ecosistema.

**Recomendación inmediata para FaberLoom:**
1. Instalar `PSPDFKit-labs/nutrient-agent-skill` para OCR y conversión de documentos a escala (requiere API key comercial).
2. Instalar `daymade/excel-automation` para generar/reportar en Excel desde pipelines de agentes.
3. Escribir `docx-template-autofill` y `batch-pdf-catalog-processor` como skills de document generation.

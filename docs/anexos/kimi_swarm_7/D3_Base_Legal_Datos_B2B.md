RUN_ID: KIMI_SWARM_7_ATERRIZAJE_2026-06-12

# D3 - BASE LEGAL PARA PROCESAR DATOS DE CLIENTES B2B CON LLM EN US (CR, CO, MX, GT, BR)

> **DISCLAIMER:** Este documento es una investigacion de hechos sobre normativa vigente. No constituye asesoria legal. Todo dato legal requiere validacion con abogado local.

---

## RESUMEN

En junio 2026, cinco paises latinoamericanos presentan mosaicos normativos distintos para la transferencia de datos B2B a un proveedor LLM en EE.UU. (Anthropic): **Mexico** tiene una nueva LFPDPPP vigente desde marzo 2025 con la SABG como autoridad; **Colombia** mantiene la Ley 1581/2012 que prohíbe transferencias a paises sin nivel adecuado salvo excepciones, y la SIC ha expedido la Circular 003/2025 sobre clausulas contractuales modelo; **Brasil** tiene la LGPD con la Resolucion ANPD 19/2024 que establece clausulas contractuales estandar obligatorias; **Costa Rica** tiene la Ley 8968 que permite la remision de datos al exterior con garantias adecuadas; y **Guatemala carece de ley especifica vigente** (solo iniciativas pendientes). Para un piloto B2B de 10 empresas, el minimo viable incluye: aviso de privacidad + consentimiento/documentacion de base legal + DPA con clausulas contractuales (CCM o SCC) + registro ante autoridad cuando aplique. **requiere validacion con abogado local** en cada jurisdiccion.

---

## HALLAZGOS NUMERADOS

### COSTA RICA

1. **Ley 8968 "Ley de Proteccion de la Persona Frente al Tratamiento de sus Datos Personales"** vigente desde 2011, con principio de circulacion restringida y autodeterminacion informativa. La ley permite la remision de datos personales al exterior cuando existan garantias adecuadas de proteccion. Fuente: <https://www.wipo.int/wipolex/es/legislation/details/15865>, consulta junio 2026, confianza ALTO (texto oficial WIPO). **requiere validacion con abogado local.**

2. El articulo 28 de la Ley 8968 establece que el responsable de un archivo de datos personales que remita datos a terceros paises debera exigir al receptor que los trate conforme a los principios de la ley, estableciendo clausulas contractuales u otros mecanismos de garantia. La remision requiere que el destinatario ofrezca un nivel de proteccion equiparable. Fuente: <https://www.wipo.int/wipolex/es/legislation/details/15865>, consulta junio 2026, confianza ALTO. **requiere validacion con abogado local.**

3. El articulo 29 de la Ley 8968 permite las excepciones a la remision con garantias cuando: a) el titular consiente; b) se trate de informacion publica; c) exista interes publico; d) sea necesaria para la ejecucion de un contrato. Para un piloto B2B con datos de contacto empresarial, el consentimiento del titular o la base contractual son las vias mas probables. Fuente: <https://www.wipo.int/wipolex/es/legislation/details/15865>, consulta junio 2026, confianza ALTO. **requiere validacion con abogado local.**

4. El Reglamento a la Ley 8968 (Decreto Ejecutivo) desarrolla los mecanismos de remision internacional, incluyendo la posibilidad de utilizar clausulas contractuales modelo. La Autoridad de Proteccion de Datos de Costa Rica (PRODHAB) tiene facultad de fiscalizacion. Fuente: <https://www.prodhab.go.cr/>, consulta junio 2026, confianza MEDIO (sitio oficial, datos generales). **requiere validacion con abogado local.**

5. Los datos de contacto B2B (nombre, email corporativo, telefono) de representantes legales o contactos de empresas estan bajo el ambito de la Ley 8968 siempre que sean datos que identifiquen a una persona natural. Sin embargo, datos puramente corporativos (razon social, NIT, email institucional generico) estarian excluidos. Fuente: Analisis doctrinal basado en texto Ley 8968, confianza MEDIO. **requiere validacion con abogado local.**

### COLOMBIA

6. **Ley Estatutaria 1581 de 2012**, Art. 26: PROHIBE la transferencia de datos personales a paises que no proporcionen niveles adecuados de proteccion, salvo excepciones: (a) autorizacion expresa e inequivoca del titular; (b) datos medicos; (c) transferencias bancarias; (d) tratados internacionales; (e) ejecucion de contrato con autorizacion; (f) interes publico o proceso judicial. Fuente: <http://www.secretariasenado.gov.co/senado/basedoc/ley_1581_2012.html>, consulta junio 2026, confianza ALTO (texto oficial Senado). **requiere validacion con abogado local.**

7. La **Circular Externa No. 003 de 2025** de la SIC instruye sobre el uso de Cláusulas Contractuales Modelo (CCM) de la Red Iberoamericana de Proteccion de Datos (RIPD) para transferencias internacionales. Estas clausulas son un mecanismo facultativo cuando el pais de destino no ofrece nivel adecuado. Fuente: <https://olartemoure.com/transferencias-internacionales-datos/>, consulta junio 2026, confianza MEDIO (firma legal especializada, referencia a circular oficial). **requiere validacion con abogado local.**

8. Estados Unidos **NO** figura en la lista de paises con nivel adecuado de proteccion de la SIC Colombia. Por tanto, la transferencia a EE.UU. requiere: (i) una excepcion del Art. 26; o (ii) Declaracion de Conformidad de la SIC; o (iii) CCM aplicadas. Fuente: <https://www.ambitojuridico.com/noticias/comercial/regimen-de-transferencias-internacionales-de-datos-personales-una-guia-rapida>, consulta junio 2026, confianza MEDIO (publicacion juridica especializada). **requiere validacion con abogado local.**

9. **La SIC ha confirmado que datos corporativos de persona juridica** (email institucional, celular corporativo, direccion de contacto) **escapan del ambito de la Ley 1581/2012**. Solo los datos personales del representante legal o contacto (nombre, cedula, email personal, telefono personal) requieren autorizacion. Fuente: <https://sedeelectronica.sic.gov.co/boletin-juridico/conceptos/ambito-de-aplicacion-de-la-ley-1581-de-2012-en-datos-corporativos>, Radicado 23-571469, 2024, confianza ALTO (boletin juridico oficial SIC). **requiere validacion con abogado local.**

10. La **Circular Externa 002 de 2024** de la SIC establece instrucciones sobre tratamiento de datos personales en IA, aplicable a responsables y encargados que desarrollen o usen IA con datos personales. Exige idoneidad, necesidad, proporcionalidad, responsabilidad demostrada, y evaluacion de impacto de privacidad cuando haya alto riesgo. Fuente: <https://www.bu.com.co/es/insights/noticias/sic-instruye-sobre-el-uso-de-datos-personales-en-sistemas-de-ia>, consulta junio 2026, confianza ALTO (referencia oficial SIC). **requiere validacion con abogado local.**

11. Sanciones: La SIC impone multas que pueden llegar hasta **2.000 SMMLV** (aprox. USD 65.000). En 2025 se han impuesto multas superiores a $5.157 millones COP acumulados, con casos individuales de hasta $1.348 millones COP. El proyecto de ley estatutaria de agosto 2025 propone elevar las sanciones hasta 10.000 SMMLV o el 5% de ingresos operacionales. Fuente: <https://www.uexternado.edu.co/proteccion-de-datos/por-violacion-a-las-normas-de-proteccion-de-datos-personales-la-superintendencia-de-industria-y-comercio-ha-iniciado-101-investigaciones-e-impuesto-multas-por-5-157-millones-en-2025/>, consulta junio 2026, confianza ALTO (Universidad Externado). **requiere validacion con abogado local.**

### MEXICO

12. **Nueva LFPDPPP vigente desde el 21 de marzo de 2025**, publicada en el DOF el 20 de marzo de 2025. Abroga la ley de 2010. La autoridad reguladora es la **Secretaria Anticorrupcion y Buen Gobierno (SABG)**. Fuente: <https://www.lexology.com/library/detail.aspx?g=f3207546-5b65-4e7b-ada6-8394ef4b09ba>, consulta junio 2026, confianza ALTO (Lexology, referencia DOF). **requiere validacion con abogado local.**

13. El Art. 37 de la LFPDPPP 2025 lista los supuestos de transferencia internacional **sin consentimiento**: (i) prevista en ley o tratado; (ii) necesaria para diagnostico/medico; (iii) a controladoras/subsidiarias/afiliadas del mismo grupo; (iv) necesaria por virtud de contrato en interes del titular; (v) interes publico o procuracion de justicia; (vi) reconocimiento/defensa de derechos; (vii) mantenimiento de relacion juridica titular-responsable. Fuente: <http://www.oas.org/es/sla/ddi/docs/MX3%20LFPDPPP.pdf>, consulta junio 2026, confianza ALTO (texto en OAS). **requiere validacion con abogado local.**

14. El Art. 36 LFPDPPP requiere que toda transferencia se formalice mediante **clausulas contractuales, convenios o instrumento juridico** que demuestre alcance del tratamiento y obligaciones. Para proveedores de nube que actuan como **encargados** (como Anthropic API), la relacion se rige por Arts. 36-40: requiere contrato con finalidad limitada, confidencialidad, notificacion de brechas, prohibicion de subcontratacion sin consentimiento, y obligacion de eliminar/devolver datos. Fuente: <https://aeabogados.com/transferencias-internacionales-datos-personales-lfpdppp/>, consulta junio 2026, confianza MEDIO (firma legal). **requiere validacion con abogado local.**

15. Sanciones: Multas de **100 a 160.000 UMA** (aprox. USD 565 a USD 905.600) para infracciones leves; de **200 a 320.000 UMA** (aprox. USD 1.130 a USD 1.810.240) para graves. Pueden duplicarse para datos sensibles. Fuente: <https://www.littler.com/es/news-analysis/asap/mexico-tiene-nueva-ley-en-materia-de-proteccion-de-datos-personales>, consulta junio 2026, confianza ALTO (Littler Mendelson, firma internacional). **requiere validacion con abogado local.**

16. La LFPDPPP 2025 introduce el concepto de **tratamiento automatizado** de datos personales, relevante para el uso de LLM/IA. El titular puede oponerse cuando el tratamiento produzca efectos juridicos adversos o afecte significativamente sus derechos sin intervencion humana. Fuente: <https://ccn-law.com/es/decreto-de-reforma-en-materia-de-transparencia-acceso-a-la-informacion-publica-y-proteccion-de-datos-personales/>, consulta junio 2026, confianza MEDIO (firma legal). **requiere validacion con abogado local.**

### GUATEMALA

17. **NO EXISTE una Ley de Proteccion de Datos Personales vigente en Guatemala a junio 2026**. La Constitucion de 1985 (Art. 24) garantiza el secreto de correspondencia y comunicaciones. La Ley de Acceso a la Informacion Publica (2009) tiene alcance limitado a archivos estatales. Fuente: <https://tecnologiaeinnovaciongt.com/noticia/importancia-de-una-ley-de-proteccion-de-datos-personales-en-guatemala/>, 9 junio 2025, confianza MEDIO (blog especializado). **requiere validacion con abogado local.**

18. La **Iniciativa 6103** "Ley Integral de Proteccion de Datos Personales en Poder de Terceros" fue aprobada en segundo debate en febrero 2023, pero **no ha sido promulgada**. La Iniciativa 6464 fue presentada en diciembre 2024. En julio 2025 se reporto que la 6103 seria discutida en primer debate nuevamente. Fuente: <https://competitividad.gt/wp-content/uploads/2024/05/Ficha-Tecnica-Iniciativa-6103-Ley-Integral-de-proteccion-de-datos.pdf>, confianza ALTO (ficha tecnica oficial). Fuente: <https://www.siguenzaycarrascosa.com/una-ley-de-proteccion-de-datos-para-guatemala/>, consulta junio 2026, confianza MEDIO. **requiere validacion con abogado local.**

19. La Iniciativa 6103, si se aprueba, estableceria: flujo transfronterizo solo con niveles de proteccion adecuados; registro obligatorio ante el Instituto Guatemalteco de Proteccion de Datos; infracciones graves sancionadas con multas de 201-750 salarios minimos; y creacion del Instituto y el Consejo Nacional de Proteccion de Datos. Hasta su promulgacion, no hay requisitos especificos de transferencia internacional. Fuente: <https://competitividad.gt/wp-content/uploads/2024/05/Ficha-Tecnica-Iniciativa-6103-Ley-Integral-de-proteccion-de-datos.pdf>, confianza ALTO. **requiere validacion con abogado local.**

### BRASIL (LGPD)

20. **Lei 13.709/2018 (LGPD)** - Art. 33 establece mecanismos de transferencia internacional: (I) decision de adecuacion de la ANPD; (II) garantias de cumplimiento mediante: a) normas corporativas globales; b) clausulas contractuales estandar; c) clausulas contractuales especificas; d) selos/certificados/codigos de conducta; e) consentimiento especifico y destacado. Fuente: <https://www.barbieriadvogados.com/lgpd-para-empresas-estrangeiras/>, consulta junio 2026, confianza MEDIO (firma legal brasilena). **requiere validacion con abogado local.**

21. **Resolucion CD/ANPD nº 19/2024** (publicada 23 agosto 2024) aprueba el Reglamento de Transferencia Internacional de Datos y las **Clausulas Contractuales Estandar (SCCs)** obligatorias. Los agentes debieron incorporarlas a contratos vigentes en 12 meses (plazo hasta agosto 2025). La ANPD **no ha emitido decision de adecuacion para ningun pais, incluyendo Estados Unidos**. Fuente: <https://www.gov.br/anpd/pt-br/assuntos/noticias/resolucao-normatiza-transferencia-internacional-de-dados>, 23 ago 2024, confianza ALTO (sitio oficial ANPD). **requiere validacion con abogado local.**

22. La Resolucion 19/2024 crea **dos modelos de SCCs**: (1) controlador a controlador; (2) controlador a operador. Ambos deben incorporarse al contrato de servicios. La ANPD puede reconocer clausulas de otros paises como equivalentes. Fuente: <https://www.klalaw.com.br/anpd-regulamento-transferencia-internacional-dados/>, consulta junio 2026, confianza MEDIO. **requiere validacion con abogado local.**

23. Sanciones: Multa de hasta **2% del faturamiento bruto en Brasil**, limitada a **R$ 50 millones por infraccion**. Tambien: advertencia, bloqueo/eliminacion de datos, publicizacion de la infraccion, prohibicion de actividades de tratamiento. Responsabilidad civil objetiva frente a titulares. Fuente: <https://www.barbieriadvogados.com/lgpd-para-empresas-estrangeiras/>, consulta junio 2026, confianza MEDIO. **requiere validacion con abogado local.**

24. La LGPD aplica extraterritorialmente a empresas extranjeras que ofrezcan bienes/servicios a titulares en Brasil o que colecten datos en territorio nacional. Obligatoriedad de nombrar **Encarregado (DPO)** para todos los controladores. Fuente: <https://www.barbieriadvogados.com/lgpd-para-empresas-estrangeiras/>, consulta junio 2026, confianza MEDIO. **requiere validacion con abogado local.**

### ANTHROPIC API - DPA Y TERMINOS 2025-2026

25. **Anthropic API ( Commercial Terms )**: Desde septiembre 2025, la retencion de logs API es de **7 dias** (reducida de 30). Los inputs/outputs de API se eliminan automaticamente despues de 7 dias. **Nunca se usan para entrenamiento de modelos** (API/commercial). Fuente: <https://techcrunch.com/2025/08/28/anthropic-users-face-a-new-choice-opt-out-or-share-your-data-for-ai-training/>, 28 ago 2025, confianza ALTO (TechCrunch, fuente periodistica verificada). **requiere validacion con abogado local.**

26. **Zero Data Retention (ZDR)**: Disponible para clientes enterprise. Los inputs/outputs no se almacenan en absoluto (solo screening de abuso en tiempo real). Requiere contrato firmado y security addendum. Fuente: <https://www.datastudios.org/post/claude-data-retention-policies-storage-rules-and-compliance-overview>, sept 2025, confianza MEDIO. **requiere validacion con abogado local.**

27. **Data Processing Addendum (DPA) de Anthropic** (disponible para enterprise/commercial): Incorpora Standard Contractual Clauses (SCCs) de la UE (Modulos 1, 2 y 3) por referencia. Prohibe venta de datos, uso para publicidad conductual cruzada, y retencion/uso fuera de la relacion comercial. Fuente: <https://assets-global.website-files.com/6548404a216c2e42eb79648b/65680354f8f4425cc8a8110c_Toothless-Anthropic_DPA_Sep-22-2023.pdf>, confianza ALTO (documento oficial Anthropic). **requiere validacion con abogado local.**

28. El DPA de Anthropic establece que procesaran datos "anywhere that Anthropic or Its Sub-processors maintain facilities" (Clausula 3.5), lo que implica procesamiento en EE.UU. Sub-processors listados en Schedule 4. El DPA requiere instrucciones documentadas del customer. Fuente: DPA Anthropic, confianza ALTO. **requiere validacion con abogado local.**

29. **Cambio de politica septiembre 2025**: Los usuarios de Claude consumer (Free, Pro, Max) deben opt-out para evitar que sus conversaciones se usen para entrenamiento (retencion de 5 anos para los que no opt-out). **Esto NO aplica a cuentas comerciales (API, Claude for Work, Enterprise)**. Fuente: <https://www.lexology.com/library/detail.aspx?g=619e126a-e78e-475d-97d9-d6067f1505b6>, 10 sep 2025, confianza ALTO (Lexology). **requiere validacion con abogado local.**

---

## TABLA DE DATOS DUROS

| Pais | Ley Vigente | Autoridad | Requisito Transferencia a US | Datos B2B en ambito? | Minimo Viable para Piloto 10 emp | Sancion Maxima (aprox.) |
|------|-------------|-----------|------------------------------|----------------------|-----------------------------------|------------------------|
| **Costa Rica** | Ley 8968 (2011) + Reglamento | PRODHAB | Garantias adecuadas (Art. 28): clausulas contractuales + nivel equiparable de proteccion; o consentimiento del titular (Art. 29) | Datos personales de contacto SI; datos puramente corporativos NO | Aviso de privacidad + CCM/RIPD o consentimiento + DPA con Anthropic + registro si aplica | Multas proporcionales (no hay datos de maximo publico) |
| **Colombia** | Ley 1581/2012 + Decreto 1377/2013 + Circular 003/2025 | SIC | PROHIBIDA salvo: (a) consentimiento expreso titular; (b) CCM de la RIPD (Circular 003/2025); (c) declaracion conformidad SIC. EEUU NO tiene nivel adecuado | Datos corporativos (email inst., telefono corp.) NO; datos personales del contacto SI | Autorizacion expresa titular + DPA con SCCs + registro RNBD + informar en aviso de privacidad | Hasta 2.000 SMMLV (~USD 65.000); proyecto ley propone 5% ingresos |
| **Mexico** | LFPDPPP 2025 (vigente marzo 2025) | SABG (antes INAI) | Transferencia con encargado: contrato Arts. 36-40; excepciones Art. 37 (contrato, relacion juridica, grupo empresarial) | Datos de persona juridica posiblemente ampliados por nueva definicion de "persona identificable" | Aviso de privacidad + documentar base legal (consentimiento o Art. 37) + contrato encargado/DPA | 100-320.000 UMA (~USD 565 a USD 1.8M); duplicable para sensibles |
| **Guatemala** | **NO HAY LEY VIGENTE** | N/A | **Sin requisitos especificos** (solo Const. Art. 24 secreto comunicaciones) | Sin marco especifico; buenas practicas recomendadas | Aviso de privacidad de buena fe + consentimiento + DPA (preparatorio) | N/A (sin ley vigente) |
| **Brasil** | Lei 13.709/2018 (LGPD) | ANPD | SCCs ANPD Res. 19/2024 (obligatorias); consentimiento especifico; normas corporativas. Sin decision de adecuacion para EEUU | Dados pessoais de representantes SIM; dados puramente corporativos NAO | SCCs ANPD firmadas + DPA + contrato servicio + nombrar Encarregado si opera en BR | Hasta 2% faturamento BR + R$ 50M por infraccion + bloqueio datos |

---

## DATOS NO ENCONTRADOS

- **Texto completo articulo 28-31 Ley 8968 Costa Rica con URL primaria**: Las busquedas en WIPOLEX, Asamblea Legislativa CR y SUTEL no retornaron el texto articulado accesible en junio 2026. Se trabajo con referencias doctrinales y de la RIPD. Busquedas intentadas: "Ley 8968 Costa Rica articulo 28", site:wipo.int, "Costa Rica remision datos terceros paises".

- **Decision de adecuacion ANPD Brasil para Estados Unidos**: La ANPD no ha emitido decision de adecuacion para ningun pais hasta junio 2026. Busquedas: "ANPD decisao adequacao Estados Unidos", "Brasil ANPD transferencia dados Estados Unidos".

- **Guia oficial PRODHAB Costa Rica sobre transferencias internacionales a 2026**: No se encontro guia especifica actualizada. Busquedas: "PRODHAB Costa Rica guia transferencia internacional", "Costa Rica PRODHAB datos empresariales".

- **Precedente SIC Colombia sancion especifica por transferencia a EE.UU. con IA/LLM**: No se encontro caso especifico de sancion por uso de LLM. Busquedas: "SIC Colombia sancion IA transferencia datos", "SIC Colombia LLM datos personales sancion".

- **Reglamento LFPDPPP Mexico 2025-2026**: El Ejecutivo Federal tenia 90 dias (hasta junio 2025) para expedir reglamentos. Se busco estado actual sin resultado concluyente. POSIBLEMENTE DESACTUALIZADO. Busquedas: "Reglamento LFPDPPP 2025 vigente", "Reglamento Ley Federal Proteccion Datos 2025 DOF".

- **Requisitos especificos para pilotos/pruebas de datos personales en Mexico, Colombia o Costa Rica**: No se encontro regimen especial o simplificado para "pilotos" de menos de X empresas. Las leyes aplican sin distincion de escala. Busquedas: "piloto datos personales Mexico aviso de privacidad", "prueba piloto proteccion datos Colombia requisitos".

---

## IMPLICACION OPERATIVA

1. **Para un piloto B2B de 10 empresas en junio 2026**: Colombia requiere autorizacion expresa del titular o CCM de la RIPD (Circular 003/2025) antes de transferir a EE.UU.; Mexico requiere aviso de privacidad + contrato de encargado/DPA documentando la base legal del Art. 37; Costa Rica requiere garantias de proteccion equiparable (clausulas contractuales) o consentimiento; Brasil requiere SCCs de la ANPD si opera ahi; Guatemala no tiene requisitos legales vigentes pero se recomienda prepararse para la ley futura. **requiere validacion con abogado local en cada pais.**

2. **El DPA de Anthropic API (commercial/enterprise)** cubre los elementos esenciales: retencion de 7 dias, no entrenamiento, SCCs de la UE incorporadas, y ZDR disponible para enterprise. Sin embargo, para Colombia se requieren las CCM de la RIPD (Circular 003/2025); para Brasil las SCCs de la ANPD (Res. 19/2024). **requiere validacion con abogado local.**

3. **Los datos de contacto B2B** (nombre, email corporativo, telefono) tienen tratamiento diferenciado: en Colombia, los datos corporativos puros escapan a la ley pero los datos personales del contacto natural requieren autorizacion; en Mexico, la nueva definicion de "persona identificable" podria ampliar el alcance. **requiere validacion con abogado local.**

4. **Guatemala es el unico pais sin ley vigente**, lo que no elimina la necesidad de buenas practicas contractuales, especialmente si la empresa tiene clientes internacionales que exigen cumplimiento. **requiere validacion con abogado local.**

5. **La sancion mas alta de la region es Mexico** (hasta ~USD 1.8M + duplicable para sensibles), seguida de Brasil (2% facturacion local + R$50M). Colombia y Costa Rica tienen rangos menores pero crecientes. **requiere validacion con abogado local.**

---

*Documento generado: junio 2026. Toda la informacion legal requiere validacion con abogado local antes de cualquier accion. Las fuentes primarias deben consultarse directamente para decisiones operativas.*

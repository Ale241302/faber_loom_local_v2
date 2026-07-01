# LOC_SVC_PT — Localização: Templates de Atendimento ao Cliente (Português BR)
id: LOC_SVC_PT
status: DRAFT
visibility: [INTERNAL]
version: 1.0
domain: Plataforma (IDX_PLATAFORMA)
classification: LOC — Data localizada por idioma (português brasileiro)
aplica_a: [MWT]

refs:
  - PLB_INTERACCION_CLIENTE (playbook que consome estes templates)
  - ENT_OPS_STATE_MACHINE (estados canônicos — FROZEN)
  - ENT_PLAT_I18N (regras gerais de idioma)

---

## A. Templates por estado do expediente

| Estado | Código | Template |
|--------|--------|----------|
| Registro | REGISTRO | Seu pedido {expediente_ref} está em fase de registro. Estamos processando a ordem de compra. |
| Produção | PRODUCCION | Seu pedido {expediente_ref} está em produção na fábrica. A data estimada de conclusão é {fecha_estimada}. |
| Preparação | PREPARACION | A produção do seu pedido {expediente_ref} foi concluída. Estamos coordenando a logística de envio. |
| Despacho | DESPACHO | Seu pedido {expediente_ref} está aprovado para despacho. Em breve você receberá as informações de embarque. |
| Trânsito | TRANSITO | Sua carga {expediente_ref} está em trânsito. Rastreio: {tracking}. Transportadora: {carrier}. |
| No destino | EN_DESTINO | Sua carga {expediente_ref} chegou em {destino}. Estamos coordenando a entrega final. |
| Encerrado | CERRADO | Seu pedido {expediente_ref} foi encerrado. A entrega foi confirmada em {fecha_cierre}. |
| Cancelado | CANCELADO | Seu pedido {expediente_ref} foi cancelado. Para mais detalhes, entre em contato com seu executivo MWT. |

---

## B. Templates de interação geral

| Situação | Template |
|----------|----------|
| Saudação | Olá, sou o Assistente MWT. Como posso ajudá-lo? |
| Não identificado | Este número não está registrado em nosso sistema. Por favor entre em contato com seu executivo MWT para configurar seu acesso. |
| Sem informação | Não tenho essa informação disponível no momento. Seu executivo MWT foi notificado e entrará em contato nas próximas {sla_horas} horas úteis. |
| Documento enviado | Aqui está o documento solicitado: {nombre_documento}. {link_descarga} (este link é válido por 15 minutos). |
| Documento não disponível | O documento {nombre_documento} não está disponível para seu pedido no momento. Seu executivo MWT entrará em contato com mais informações. |
| Lista de pedidos | Você tem {cantidad} pedidos abertos: {lista_expedientes}. Sobre qual deseja consultar? |
| Crédito / pagamento | Seu pedido {expediente_ref} está com {dias_credito} de {dias_limite} dias de crédito. |
| Escalamento | Essa solicitação requer atenção personalizada. Seu executivo MWT foi notificado e entrará em contato nas próximas {sla_horas} horas úteis. |

---

## C. Regras de estilo PT-BR

- Tratar por "você" (padrão business brasileiro). Não usar "tu".
- Assinar como "Assistente MWT".
- Não usar jargão técnico: "expediente" / "pedido" (não "state machine"), "documento" (não "ART-XX").
- Datas: formato DD/MM/AAAA.
- Moeda: USD salvo quando contexto exigir BRL.

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO

Changelog:
- v1.0 (2026-03-15): criação. 8 templates por estado + 8 templates interação geral + regras estilo PT-BR.

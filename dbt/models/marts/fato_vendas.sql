-- Grão: um item de pedido entregue. Cancelamentos não compõem o faturamento.
select
    i.item_id,
    i.pedido_id,
    p.cliente_id,
    i.produto_id,
    p.data_pedido,
    i.quantidade,
    i.preco_unitario,
    i.quantidade * i.preco_unitario as valor_total
from {{ ref('stg_itens') }} i
join {{ ref('stg_pedidos') }} p on p.pedido_id = i.pedido_id
where p.status = 'ENTREGUE'


select
    data_pedido,
    count(distinct pedido_id) as pedidos_entregues,
    sum(quantidade) as pizzas_vendidas,
    sum(valor_total) as faturamento,
    round(sum(valor_total) / nullif(count(distinct pedido_id), 0), 2) as ticket_medio
from {{ ref('fato_vendas') }}
group by data_pedido


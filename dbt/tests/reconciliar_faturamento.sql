-- Compara a Gold com um cálculo independente a partir da origem.
with origem as (
    select coalesce(sum(i.quantidade::numeric * i.preco_unitario_centavos::numeric / 100), 0) as total
    from {{ source('bronze', 'itens') }} i
    join {{ source('bronze', 'pedidos') }} p on p.pedido_id = i.pedido_id
    where upper(trim(p.status)) = 'ENTREGUE'
),
destino as (
    select coalesce(sum(faturamento), 0) as total
    from {{ ref('faturamento_diario') }}
)
select o.total as origem, d.total as destino
from origem o cross join destino d
where o.total <> d.total


select
    p.produto_id,
    p.nome as sabor,
    sum(f.quantidade) as pizzas_vendidas,
    sum(f.valor_total) as faturamento
from {{ ref('fato_vendas') }} f
join {{ ref('dim_produtos') }} p on p.produto_id = f.produto_id
group by p.produto_id, p.nome


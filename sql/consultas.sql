-- Exemplos de exploração das tabelas Gold.
select * from dbt_gold.faturamento_diario order by data_pedido;
select * from dbt_gold.vendas_por_sabor order by pizzas_vendidas desc;

-- Ticket do período: receita total / pedidos distintos, sem média simples dos tickets diários.
select
    count(distinct pedido_id) as pedidos,
    sum(valor_total) as faturamento,
    round(sum(valor_total) / nullif(count(distinct pedido_id), 0), 2) as ticket_medio
from dbt_gold.fato_vendas;

-- Faturamento por cidade.
select c.cidade, sum(f.valor_total) as faturamento
from dbt_gold.fato_vendas f
join dbt_gold.dim_clientes c using (cliente_id)
group by c.cidade
order by faturamento desc;


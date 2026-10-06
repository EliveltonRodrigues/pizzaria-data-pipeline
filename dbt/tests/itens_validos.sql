-- Um teste SQL falha quando retorna linhas.
select *
from {{ ref('stg_itens') }}
where quantidade <= 0 or preco_unitario <= 0


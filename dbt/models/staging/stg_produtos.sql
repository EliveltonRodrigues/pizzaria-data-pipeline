select
    produto_id::integer as produto_id,
    trim(nome) as nome,
    preco_centavos::numeric / 100 as preco_atual
from {{ source('bronze', 'produtos') }}


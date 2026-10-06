select
    item_id::integer as item_id,
    pedido_id::integer as pedido_id,
    produto_id::integer as produto_id,
    quantidade::integer as quantidade,
    preco_unitario_centavos::numeric / 100 as preco_unitario
from {{ source('bronze', 'itens') }}


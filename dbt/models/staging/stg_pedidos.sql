select
    pedido_id::integer as pedido_id,
    cliente_id::integer as cliente_id,
    data_pedido::date as data_pedido,
    upper(trim(status)) as status
from {{ source('bronze', 'pedidos') }}


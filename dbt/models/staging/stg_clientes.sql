select
    cliente_id::integer as cliente_id,
    upper(trim(cidade)) as cidade
from {{ source('bronze', 'clientes') }}


select cliente_id, cidade from {{ ref('stg_clientes') }}


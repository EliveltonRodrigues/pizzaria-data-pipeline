select produto_id, nome, preco_atual from {{ ref('stg_produtos') }}


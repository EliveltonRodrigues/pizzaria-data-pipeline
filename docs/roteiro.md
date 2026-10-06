# Roteiro de aprendizagem

Estude uma etapa por sessão. Leia o código, execute, confira a saída e faça um commit com o que entendeu ou alterou.

## 1. Origem e grão dos dados

Leia scripts/gerar_dados.py. Identifique as quatro entidades e suas chaves. Por que pedido e item precisam de tabelas diferentes?

Execute o gerador duas vezes e observe que os arquivos são iguais. Depois mude a semente e compare as quantidades por status.

Critério de conclusão: conseguir explicar os relacionamentos e por que há mais itens que pedidos.

## 2. Ingestão e reexecução

Leia scripts/carregar_bronze.py. Execute a carga duas vezes; a tabela de pedidos deve continuar com 500 linhas.

Explique a transação e o risco de apagar a tabela fora dela. A idempotência deste projeto vem da substituição do snapshot, não de um upsert. Não há histórico das versões anteriores.

Critério de conclusão: demonstrar que a segunda carga não duplica a primeira.

## 3. Modelagem com dbt

Leia primeiro sources.yml, depois os quatro stg_*.sql e fato_vendas.sql.

Investigue:
- source() referencia a origem; ref() conecta modelos e declara dependências.
- Por que upper(trim(status))?
- Por que usamos preço do item?
- Por que ticket médio usa pedidos distintos?
- Por que a média simples dos tickets médios diários pode estar errada?

Exercício: acrescente um modelo Gold faturamento_por_cidade, com testes e descrição.

## 4. Qualidade e falhas controladas

Após gerar os CSVs, altere manualmente uma quantidade em itens.csv para -1.
Execute a carga manual e dbt build; observe o teste itens_validos falhar.

Depois regenere os dados, carregue e execute dbt build novamente.

Outro exercício: duplique uma linha em clientes.csv e execute o teste da origem.

Faça estes exercícios manualmente: a primeira tarefa da DAG regenera os CSVs e apagaria a alteração intencional. Não execute o script manual ao mesmo tempo que a DAG.

## 5. Orquestração

Antes de disparar a DAG, execute cada comando manualmente. Depois abra os logs das quatro tarefas no Airflow.

Exercício: desligue o banco com docker compose stop, dispare a DAG e observe a falha/retentativa. Ligue novamente o banco com docker compose up -d --wait e reexecute a tarefa necessária.

Observe como a falha bloqueia as dependências. A DAG valida a origem antes de transformar. dbt build também executa testes, mas não oferece publicação atômica de toda a Gold: modelos já concluídos podem ter sido atualizados antes de uma falha posterior.

## 6. Portfólio

- Guarde capturas sem credenciais em docs/screenshots.
- Escreva, com suas palavras, três decisões técnicas e duas limitações.
- Verifique o workflow de CI depois do push.
- Inclua no README os resultados que você realmente verificou.

## Evoluções, em ordem

1. Faturamento por cidade e taxa de cancelamento por dia.
2. Mais testes de qualidade e descrições das colunas.
3. Dados incrementais por data, upsert e reprocessamento de um dia.
4. Substituição do gerador por uma fonte pública documentada.
5. Dashboard no Power BI ou Metabase, conectado à Gold.
6. Contêineres para os outros componentes, mantendo persistência e segredos separados.

Spark, Kafka, Kubernetes e cloud podem entrar em projetos posteriores quando houver um problema que justifique cada ferramenta.


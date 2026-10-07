# Pizzaria Data Pipeline

Projeto didático de engenharia de dados: gerar vendas fictícias, carregar um PostgreSQL, transformar e testar com dbt e orquestrar com Airflow.

**Objetivo de negócio:** responder quanto a pizzaria faturou, quantos pedidos entregou, qual foi o ticket médio e quais sabores mais vendeu.

Dados 100% sintéticos. Não representam uma empresa real.

## Tecnologias e responsabilidades

| Tecnologia | Papel |
|---|---|
| Python 3.12 | Geração de CSVs e ingestão |
| PostgreSQL 16 | Armazenamento Bronze, Silver e Gold |
| dbt Core + dbt-postgres | Transformações SQL, dependências, documentação e testes |
| Airflow 3 | Orquestração, logs e retentativas |
| Docker Compose | Banco local isolado e persistente |
| Git e GitHub | Histórico e apresentação do projeto |
| GitHub Actions | Testes automáticos do gerador e integração Python/dbt/Postgres |

O Airflow já instalado em `~/airflow/.venv` será aproveitado. O dbt tem seu próprio ambiente em `pizzaria-data-pipeline/.venv`. A DAG usa subprocessos para chamar esse ambiente.

Não é necessário instalar Airflow novamente.

## Arquitetura e grãos

Fluxo: gerador Python → CSV → PostgreSQL Bronze → dbt Silver → dbt Gold.

O Airflow coordena quatro tarefas: gerar dados, carregar Bronze, testar a origem, construir e testar os modelos dbt.

| Camada | Schema PostgreSQL | Conteúdo |
|---|---|---|
| Bronze | bronze | Snapshot completo dos quatro CSVs, preservando campos como texto |
| Silver | dbt_silver | Tipos corrigidos, status e cidades padronizados |
| Gold | dbt_gold | Dimensões, fato de vendas e agregações |

O prefixo `dbt_` é adicionado pelo comportamento padrão de schemas personalizados do dbt.

- `clientes`: uma linha por cliente fictício (apenas identificador e cidade).
- `produtos`: uma linha por sabor.
- `pedidos`: uma linha por pedido.
- `itens`: uma linha por item de pedido.
- `fato_vendas`: uma linha por item de pedido **entregue**.
- `faturamento_diario`: uma linha por data do pedido com venda entregue.
- `vendas_por_sabor`: uma linha por sabor vendido.

A receita usa o preço histórico do item, não o preço atual do cadastro. Ticket médio = receita / pedidos distintos. Cancelados ficam na Bronze e Silver, mas não entram no faturamento. Não há frete, desconto, imposto ou estorno nesta versão.

Esta é uma demonstração das camadas em schemas relacionais; não é um data lake.

## Etapa 1 — abrir o projeto no WSL

No Ubuntu:

```bash
mkdir -p ~/projetos
cd ~/projetos
explorer.exe .
```

Na pasta aberta no Windows, extraia o ZIP. A pasta final deve ser `~/projetos/pizzaria-data-pipeline` (evite uma pasta extra com o mesmo nome dentro dela).

```bash
cd ~/projetos/pizzaria-data-pipeline
code .
python3 --version
git --version
docker --version
docker compose version
```

No VS Code, confirme o indicador WSL. Se Git não estiver instalado, execute `sudo apt install git`.

Se Docker não existir, instale o Docker Desktop para Windows seguindo a documentação oficial e habilite a integração com Ubuntu-24.04 em Settings → Resources → WSL Integration. Mantenha o Docker Desktop iniciado. Se for computador corporativo, siga as permissões e o licenciamento aplicáveis da organização.

Documentação: https://docs.docker.com/desktop/features/wsl/

## Etapa 2 — gerar e entender os dados, sem banco

O gerador só utiliza a biblioteca padrão Python:

```bash
python3 scripts/gerar_dados.py
python3 -m unittest discover -s tests -v
```

Abra os CSVs em `data/raw`. O padrão gera 500 pedidos, 60 clientes, seis produtos e 1.020 itens em setembro de 2026. Datas fixas e semente 42 tornam a experiência reproduzível. Não são dados de hoje.

Exercício inicial: escolha um pedido e localize seus itens, seu cliente e os sabores comprados.

## Etapa 3 — preparar ambiente e banco

Crie um ambiente próprio do projeto, separado do Airflow:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
cp .env.example .env
code .env
```

Escolha uma senha local no campo PGPASSWORD e salve. Não publique o arquivo `.env`; ele já está no `.gitignore`.

O arquivo `requirements-lock.txt` fixa todas as dependências resolvidas no ambiente de validação. `requirements.txt` declara as faixas diretas para uma atualização futura.

Suba somente o PostgreSQL:

```bash
docker compose up -d --wait
docker compose ps
```

O banco usa a porta local **5433**, para reduzir conflitos com instalações existentes. Os dados ficam em um volume do Docker. Alterar a senha no `.env` depois da primeira inicialização não altera automaticamente a senha do usuário já criado no banco.

## Etapa 4 — carregar a Bronze

```bash
python scripts/carregar_bronze.py
```

A carga é FULL: substitui o conteúdo das quatro tabelas dentro de uma única transação. Em caso de erro, a transação é revertida. Não há CDC ou carga incremental nesta versão.

Abra o SQL do banco:

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

No prompt do PostgreSQL:

```sql
select count(*) from bronze.pedidos;
select * from bronze.pedidos limit 5;
```

Use `\q` para sair.

## Etapa 5 — transformar e testar com dbt

```bash
python scripts/dbt_local.py debug
python scripts/dbt_local.py test --select 'source:*'
python scripts/dbt_local.py build
```

O wrapper `dbt_local.py` carrega o `.env`, seleciona o executável dbt do ambiente do projeto e aponta para `dbt/profiles.yml`.

O `build` constrói modelos e executa os testes conforme suas dependências.

Testes incluídos:
- IDs obrigatórios e únicos.
- Relacionamentos entre clientes, pedidos, itens e produtos.
- Status aceitos.
- Quantidades e preços positivos.
- Reconciliação entre a receita de origem e o agregado Gold.

Abra novamente o psql e execute as consultas de `sql/consultas.sql`.

Para os dados padrão, os resultados calculados pelo gerador são:

| Indicador | Valor esperado |
|---|---:|
| Pedidos totais | 500 |
| Pedidos entregues | 458 |
| Pedidos cancelados | 42 |
| Pizzas vendidas em pedidos entregues | 1.380 |
| Faturamento | R$ 70.853,00 |
| Ticket médio do período | R$ 154,70 |

Se você alterar a semente ou quantidade, esses valores também mudarão.

Para explorar a documentação e a linhagem do dbt:

```bash
python scripts/dbt_local.py docs generate
python scripts/dbt_local.py docs serve --port 8081
```

Abra http://localhost:8081. O Airflow permanece na porta 8080.

## Etapa 6 — orquestrar no Airflow

Se já houver um `airflow standalone` rodando, encerre-o com Ctrl+C no terminal correspondente. Inicie esta configuração:

```bash
cd ~/projetos/pizzaria-data-pipeline
bash scripts/iniciar_airflow.sh
```


O script copia apenas `dags/pizzaria_pipeline.py` para a pasta de DAGs do Airflow existente, define o caminho absoluto do projeto e inicia o Airflow. Execute esse script novamente após editar a DAG.

Abra http://localhost:8080, use seu login existente, procure `pizzaria_pipeline`, ative a DAG e clique em Trigger.

A primeira descoberta pode levar alguns minutos. O fluxo é manual (`schedule=None`), com uma execução ativa por vez e uma retentativa por tarefa.

O PostgreSQL precisa estar iniciado. O terminal do Airflow permanece aberto. Não execute a carga manualmente ao mesmo tempo que a DAG; `max_active_runs` controla apenas execuções desta DAG.

<img width="2550" height="916" alt="image" src="https://github.com/user-attachments/assets/749d8a13-0ad4-4df2-abf0-d963861f956e" />


## Etapa 7 — publicar no seu GitHub pessoal

Crie no GitHub um repositório vazio chamado `pizzaria-data-pipeline`. Depois de executar e entender o projeto, na pasta local:

```bash
git init -b main
git add .
git status
git commit -m "feat: pipeline de vendas com Python, dbt e Airflow"
```

Confira no `git status` que `.env`, ambientes virtuais, CSVs gerados e logs ficaram de fora. Configure `user.name` e `user.email` se o Git solicitar.

Substitua SEU_USUARIO pelo seu usuário real:

```bash
git remote add origin https://github.com/SEU_USUARIO/pizzaria-data-pipeline.git
git push -u origin main
```

A autenticação do GitHub será feita no seu computador. O fluxo de GitHub Actions executa testes de integração com PostgreSQL temporário; não usa seu banco local e não testa a interface ou o agendador do Airflow.

Na descrição do repositório, pode usar:
"Pipeline didático de vendas com Python, PostgreSQL, dbt e Airflow; camadas Bronze/Silver/Gold, testes de qualidade e CI."

Registre evidências reais: uma execução bem-sucedida da DAG, a linhagem do dbt e uma consulta Gold. Não afirme que o projeto processa dados de produção.

## Retomar em outro dia

Terminal 1, no Ubuntu:

```bash
cd ~/projetos/pizzaria-data-pipeline
docker compose up -d --wait
bash scripts/iniciar_airflow.sh
```

Terminal 2, para trabalhar nos scripts:

```bash
cd ~/projetos/pizzaria-data-pipeline
source .venv/bin/activate
```

Para parar: Ctrl+C no Airflow e `docker compose stop` no projeto. Este comando preserva o volume do banco.

## Próximos exercícios

Veja [docs/roteiro.md](docs/roteiro.md). Conclua o fluxo manual antes de aumentar o volume ou incluir outras ferramentas.

## Validação do pacote

- Testes Python do gerador e reexecução determinística: executados.
- Sintaxe dos arquivos Python e Bash: verificada.
- Arquivos YAML e interpretação do projeto dbt (`dbt parse`): verificados.
- PostgreSQL/Docker e DAG no Airflow: exigem execução no ambiente local; não foram executados no ambiente de preparação deste pacote.
- O CI foi incluído, mas só poderá ser considerado aprovado após a execução no GitHub.

## Referências oficiais

- Airflow TaskFlow: https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html
- BashOperator: https://airflow.apache.org/docs/apache-airflow-providers-standard/stable/operators/bash.html
- dbt com PostgreSQL: https://docs.getdbt.com/docs/local/connect-data-platform/postgres-setup
- dbt build: https://docs.getdbt.com/reference/commands/build
- Docker e WSL: https://docs.docker.com/desktop/features/wsl/


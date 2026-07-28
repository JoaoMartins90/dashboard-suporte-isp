# Dashboard de Suporte — Provedor de Internet

Dashboard em Streamlit para acompanhamento operacional do setor de suporte de um provedor de internet (ISP), construído sobre a base de dados do sistema MK Solutions.

O objetivo era substituir a extração manual de planilhas por uma visualização direta do banco, com filtros por operador, período e bairro — e, principalmente, identificar **clientes reincidentes**: quem abre o mesmo tipo de chamado repetidamente em um curto intervalo, sinalizando um problema de infraestrutura que não foi realmente resolvido.

> Projeto desenvolvido durante estágio, em 2024.

---

## Funcionalidades

### Atendimentos

Visão geral do volume de chamados, com filtros combináveis na barra lateral (operador, intervalo de datas e bairro).

- Atendimentos por operador no período
- Atendimentos por bairro (dividido em dois gráficos para legibilidade)
- Atendimentos por classificação
- Distribuição cruzada de operador × classificação
- Métricas de abertos, fechados e total — separando os que já viraram Ordem de Serviço

### Reincidências

O núcleo do projeto. Identifica clientes que abriram **o mesmo tipo de problema mais de uma vez em um intervalo de 60 dias**, considerando apenas as falhas de conexão que interessam à operação:

`Não Conecta` · `Não Navega` · `Conexão Caindo` · `Alteração no Wi-Fi` · `Navegação Lenta`

A lógica ordena os chamados por cliente e tipo de problema, calcula a diferença entre datas consecutivas e mantém apenas os grupos com duas ou mais ocorrências dentro da janela:

```python
df_reincidencias = df_filtrado.sort_values(['username', 'nome_processo', 'dt_abertura'])
df_reincidencias['dentro_2_meses'] = (
    df_reincidencias.groupby(['username', 'nome_processo'])['dt_abertura']
    .diff()
    .le(pd.Timedelta(days=60))
)
```

O `groupby` impede que a comparação atravesse a fronteira entre clientes, e a primeira ocorrência de cada grupo fica como `NaT` — ou seja, não conta como reincidência.

A saída é uma tabela de reincidências filtrável por cliente e por tipo de problema, acompanhada da contagem de ocorrências por cliente e por categoria — usada para priorizar visitas técnicas.

---

## Stack

| Camada | Ferramenta |
|---|---|
| Interface | Streamlit |
| Gráficos | Plotly Express |
| Manipulação de dados | pandas |
| Acesso ao banco | SQLAlchemy + psycopg2 |
| Banco de dados | PostgreSQL (MK Solutions) ou SQLite (base de exemplo) |

Compatível com pandas 2 e 3.

---

## Estrutura

```
.
├── home.py              # Entrypoint do Streamlit
├── seed.py              # Gera a base SQLite de exemplo
├── utils.py             # Conexão com o banco e leitura genérica de tabelas
├── data_proc.py         # Uma função por tabela de origem, já com colunas renomeadas
├── pages/
│   ├── Atendimentos.py  # Gráficos e métricas de volume
│   └── Reincidências.py # Detecção de chamados repetidos
└── requirements.txt
```

A separação segue três camadas: `utils.py` sabe conversar com o banco, `data_proc.py` sabe quais tabelas e colunas existem, e as páginas em `pages/` só cuidam de agregação e apresentação. Trocar a origem dos dados exige mexer em um arquivo só.

---

## Como rodar

```bash
git clone https://github.com/JoaoMartins90/dashboard-suporte-isp.git
cd dashboard-suporte-isp

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Com a base de exemplo (recomendado)

O projeto acompanha um gerador de dados fictícios, então não é preciso ter acesso a nenhum banco para experimentar:

```bash
python seed.py
streamlit run home.py
```

O [`seed.py`](seed.py) cria um SQLite local (`dados_exemplo.db`) reproduzindo o schema das tabelas de origem, com 600 atendimentos, 60 clientes e 15 bairros. As datas são geradas a partir do dia da execução, de modo que a janela de 60 dias da página de Reincidências sempre encontra casos. Usa apenas a biblioteca padrão e é determinístico — a mesma semente gera sempre a mesma base.

O `utils.py` detecta a base de exemplo automaticamente quando não há Postgres configurado.

### Com a base real (PostgreSQL)

Requer acesso a uma base com o schema do MK Solutions (tabelas `mk_atendimento`, `mk_bairros`, `mk_pessoas`, `mk_conexoes`, `mk_ate_processos`, `mk_ate_os`, `mk_atendimento_classificacao`).

```bash
cp .env.example .env
```

Preencha as variáveis de conexão a partir de [`.env.example`](.env.example). Definir `DB_HOST` faz a aplicação usar o Postgres em vez do SQLite. O `.env` está no `.gitignore` e **nunca deve ser versionado**.

```bash
streamlit run home.py
```

---

## Demonstração

<!-- Adicione as capturas em docs/ e referencie aqui:
![Atendimentos](docs/atendimentos.png)
![Reincidências](docs/reincidencias.png)
-->

_Capturas de tela em breve._

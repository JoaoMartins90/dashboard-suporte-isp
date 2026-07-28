import streamlit as st
import pandas as pd
from data_proc import processa_tabela_atendimentos

st.set_page_config(page_title='Dashboard de Suporte', page_icon='📡', layout='wide')


@st.cache_data
def carrega_resumo():
    df = processa_tabela_atendimentos()
    df['dt_abertura'] = pd.to_datetime(df['dt_abertura'], errors='coerce', format='%d/%m/%Y')
    df = df.dropna(subset=['dt_abertura'])
    return df


st.title('Dashboard de Suporte')
st.markdown(
    'Acompanhamento operacional do setor de suporte de um provedor de internet. '
    'Os dados vêm direto da base de atendimentos, sem exportação manual de planilhas.'
)

st.divider()

# A conexão pode falhar por falta de banco configurado ou de base de exemplo.
# Nesse caso vale orientar em vez de deixar o traceback estourar na tela.
try:
    df = carrega_resumo()
except Exception as erro:
    st.error('Não foi possível carregar os dados.')
    st.code(str(erro), language=None)
    st.info(
        'Para experimentar sem acesso a um banco, gere a base de exemplo:\n\n'
        '```\npython seed.py\n```'
    )
    st.stop()

# Panorama geral
total_atendimentos = len(df)
total_clientes = df['cliente_cadastrado'].nunique()
finalizados = (df['finalizado'] == 'S').sum()
taxa_finalizados = finalizados / total_atendimentos if total_atendimentos else 0

coluna1, coluna2, coluna3, coluna4 = st.columns(4)
coluna1.metric('Atendimentos', f'{total_atendimentos:,}'.replace(',', '.'))
coluna2.metric('Clientes atendidos', f'{total_clientes:,}'.replace(',', '.'))
coluna3.metric('Finalizados', f'{taxa_finalizados:.0%}')
coluna4.metric(
    'Período',
    f"{df['dt_abertura'].min():%m/%Y} – {df['dt_abertura'].max():%m/%Y}"
)

st.divider()

# Navegação
st.subheader('Páginas')

coluna_esquerda, coluna_direita = st.columns(2)

with coluna_esquerda:
    st.page_link('pages/Atendimentos.py', label='**Atendimentos**', icon='📊')
    st.caption(
        'Volume de chamados por operador, bairro e classificação, '
        'com filtros de período e métricas de abertos e fechados.'
    )

with coluna_direita:
    st.page_link('pages/Reincidências.py', label='**Reincidências**', icon='🔁')
    st.caption(
        'Clientes que abriram o mesmo tipo de problema mais de uma vez '
        'em até 60 dias — sinal de falha de infraestrutura não resolvida.'
    )

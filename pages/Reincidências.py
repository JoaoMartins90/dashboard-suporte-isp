import streamlit as st
import pandas as pd
from data_proc import processa_tabela_atendimentos, processa_tabela_bairros, atendimento_classificacao, atendimento_pessoas, atendimento_processos, atendimento_conexao
from datetime import datetime, timedelta


# Cache the data loading functions to improve performance
@st.cache_data
def load_data():
    df_atendimentos = processa_tabela_atendimentos()
    df_bairros = processa_tabela_bairros()
    df_class = atendimento_classificacao()
    df_pessoas = atendimento_pessoas()
    df_processos = atendimento_processos()
    df_conexao = atendimento_conexao()
    return df_atendimentos, df_bairros, df_class, df_pessoas, df_processos, df_conexao

df_atendimentos, df_bairros, df_class, df_pessoas, df_processos, df_conexao = load_data()


# Merge dos dataframes
df_final_1 = pd.merge(df_atendimentos, df_bairros, on='codbairro', how='left')
df_final = pd.merge(df_final_1, df_class, on='codatclass', how='left')
df_final_2 = df_final.fillna(0)

df_final_2 = pd.merge(df_final_2, df_pessoas, on='cliente_cadastrado', how='left')
df_completa = pd.merge(df_final_2, df_processos, on='cd_processo', how='left')
df_completa = pd.merge(df_completa, df_conexao, on='conexao', how='left')

# Remover colunas desnecessárias
df_completa = df_completa.drop(columns=['cliente_cadastrado', 'codbairro', 'codatclass', 'como_foi_contato', 'cd_processo'])

# Garantir que todos os valores em 'username' sejam strings
df_completa['username'] = df_completa['username'].astype(str)

# Filtrar as linhas de interesse na coluna 'nome_processo'
valores_interesse = ['Não Conecta', 'Não Navega', 'Conexão Caindo', 'Alteração no Wi-fi', 'Navegação Lenta']

# Converter dt_abertura para datetime
# O formato é explícito porque as datas vêm como texto em dd/mm/aaaa: sem ele o
# pandas infere o formato pela primeira linha e transforma o resto em NaT.
df_filtrado = df_completa[df_completa['nome_processo'].isin(valores_interesse)].copy()
df_filtrado['dt_abertura'] = pd.to_datetime(df_filtrado['dt_abertura'], errors='coerce', format='%d/%m/%Y')

# Marcar os chamados abertos até 60 dias depois do anterior do mesmo cliente
# para o mesmo problema. Ordenar antes é o que dá sentido ao diff(), e o
# groupby garante que a comparação não atravesse a fronteira entre grupos.
# A primeira ocorrência de cada grupo fica como NaT e, portanto, False.
df_reincidencias = df_filtrado.sort_values(['username', 'nome_processo', 'dt_abertura'])
df_reincidencias['dentro_2_meses'] = (
    df_reincidencias.groupby(['username', 'nome_processo'])['dt_abertura']
    .diff()
    .le(pd.Timedelta(days=60))
)
df_reincidencias = df_reincidencias.reset_index(drop=True)

# Filtrar as reincidências
df_reincidencias_final = df_reincidencias[df_reincidencias['dentro_2_meses'] == True]

# Manter apenas as reincidências com a mesma combinação de username e tipo de problema
df_reincidencias_final = df_reincidencias_final.groupby(['username', 'nome_processo']).filter(lambda x: len(x) >= 2)

# Selecionar colunas relevantes, incluindo o nome do cliente
colunas_relevantes = ['username', 'nome_processo', 'dt_abertura', 'bairro', 'nome_razaosocial']
df_reincidencias_final = df_reincidencias_final[colunas_relevantes]

# Renomear colunas
df_reincidencias_final = df_reincidencias_final.rename(columns={
    'username': 'Username',
    'nome_processo': 'Tipo de Problema',
    'dt_abertura': 'Data de Abertura',
    'bairro': 'Bairro',
    'nome_razaosocial': 'Nome do Cliente' 
})

# Calcular a data de dois meses atrás
data_dois_meses_atras = datetime.now() - timedelta(days=60)

# Filtrar dados dos últimos dois meses e com mais de uma reincidência nesse período
df_reincidencias_final = df_reincidencias_final[df_reincidencias_final['Data de Abertura'] >= data_dois_meses_atras]
df_reincidencias_final = df_reincidencias_final.groupby(['Username', 'Tipo de Problema']).filter(lambda x: len(x) >= 2)

# Recalcular contagem de usernames únicos
contagem_usernames = df_reincidencias_final['Username'].value_counts()

# Obter os usernames únicos na tabela atual
usernames_na_tabela = df_reincidencias_final['Username'].unique()
st.sidebar.title('Filtro :')
usernames_disponiveis = sorted(usernames_na_tabela)
usernames_selecionados = st.sidebar.multiselect('Selecione os usernames', usernames_disponiveis)

# Aplicar filtro de username
if usernames_selecionados:
    df_reincidencias_final = df_reincidencias_final[df_reincidencias_final['Username'].isin(usernames_selecionados)]

# Recalcular contagem de reincidências por tipo
contagem_reincidencias_tipo = df_reincidencias_final['Tipo de Problema'].value_counts().reset_index()
contagem_reincidencias_tipo = contagem_reincidencias_tipo.sort_values(by='Tipo de Problema', ascending=False)

# Filtro por tipo de reincidência usando barra lateral (sidebar)
tipos_reincidencias = df_reincidencias_final['Tipo de Problema'].unique()
tipos_selecionados = st.sidebar.multiselect('Selecione os tipos de reincidência:', tipos_reincidencias)

# Filtrar dados baseado na seleção do usuário
if tipos_selecionados:
    df_reincidencias_final = df_reincidencias_final[df_reincidencias_final['Tipo de Problema'].isin(tipos_selecionados)]

# Formatar a coluna 'Data de Abertura' para dia/mês/ano antes de exibir
df_reincidencias_final['Data de Abertura'] = df_reincidencias_final['Data de Abertura'].dt.strftime('%d/%m/%Y')

# Visualização
st.write("Reincidências:")
st.write(df_reincidencias_final)

coluna1, coluna2 = st.columns(2)
with coluna1:  
    st.write('Chamadas de Usernames:')
    st.write(contagem_usernames)
with coluna2:
    st.write('Contagem de Reincidências por Tipo:')
    st.write(contagem_reincidencias_tipo)

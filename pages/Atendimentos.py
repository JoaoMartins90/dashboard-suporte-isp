import streamlit as st
import pandas as pd
from data_proc import processa_tabela_atendimentos, processa_tabela_bairros, atendimento_classificacao, atendimento_os
import plotly.express as px


df_atendimentos = processa_tabela_atendimentos()
df_bairros = processa_tabela_bairros()
df_class = atendimento_classificacao()
df_atendimento_os = atendimento_os()

df_atendimentos['em_os'] = df_atendimentos['codatendimento'].apply(lambda x: 'S' if x in df_atendimento_os['codatendimento'].values else 'N')


df_final_1 = pd.merge(df_atendimentos, df_bairros, on='codbairro', how='left')
df_final = pd.merge(df_final_1, df_class, on='codatclass', how='left')
df_final = df_final.fillna('Indefinido')

df_final = df_final[df_final['cliente_cadastrado'] != 'Indefinido']

df_filtrado = df_final
df_filtrado_grafico = df_filtrado[df_filtrado['bairro'] != 'Indefinido']

df_final = df_final[df_final['dt_abertura'] != 'Indefinido']
df_final['dt_abertura'] = pd.to_datetime(df_final['dt_abertura'], format='%d/%m/%Y')
df_final['ano'] = df_final['dt_abertura'].dt.year

st.title('Dados Suporte')

st.divider()

# Filtros
st.sidebar.title('Filtros')
with st.sidebar.expander('Operadores'):
    operadores_disponiveis = sorted(df_final['operador_abertura'].unique())
    operadores_selecionados = st.multiselect('Selecione os operadores', operadores_disponiveis, default=operadores_disponiveis)

with st.sidebar.expander('Filtro por Período'):
    start_date = st.date_input('Data de Início', min_value=df_final['dt_abertura'].min(), max_value=df_final['dt_abertura'].max())
    end_date = st.date_input('Data de Fim', min_value=df_final['dt_abertura'].min(), max_value=df_final['dt_abertura'].max(), value=df_final['dt_abertura'].max())

with st.sidebar.expander('Bairros'):
    bairros_disponiveis = sorted(df_final['bairro'].unique())
    bairros_selecionados = st.multiselect('Selecione os bairros', bairros_disponiveis, default=bairros_disponiveis)

# Aplicando filtros de operador, período e bairro
df_filtrado['dt_abertura'] = pd.to_datetime(df_filtrado['dt_abertura'], errors='coerce', format='%d/%m/%Y').dt.date
df_filtrado = df_filtrado[(df_filtrado['operador_abertura'].isin(operadores_selecionados)) & 
                          (df_filtrado['dt_abertura'] >= start_date) & 
                          (df_filtrado['dt_abertura'] <= end_date) &
                          (df_filtrado['bairro'].isin(bairros_selecionados))]

atendimentos_por_operador_periodo = df_filtrado.groupby('operador_abertura').size().reset_index(name='Número de Atendimentos por Operador')

atendimentos_por_bairro = df_filtrado.groupby('bairro').size().reset_index(name='Número de Atendimentos por Bairro')

bairros_1 = atendimentos_por_bairro['bairro'][:len(atendimentos_por_bairro)//2]
bairros_2 = atendimentos_por_bairro['bairro'][len(atendimentos_por_bairro)//2:]
atendimentos_por_bairro_1 = atendimentos_por_bairro[atendimentos_por_bairro['bairro'].isin(bairros_1)]
atendimentos_por_bairro_2 = atendimentos_por_bairro[atendimentos_por_bairro['bairro'].isin(bairros_2)]

atendimentos_por_classificacao = df_filtrado.groupby('descricao').size().reset_index(name='Número de Atendimentos por Classificação')
atendimentos_por_operador_classificacao = df_filtrado.groupby(['operador_abertura', 'descricao']).size().reset_index(name='Número de Atendimentos')


atendimentos_por_operador_periodo = atendimentos_por_operador_periodo[atendimentos_por_operador_periodo['operador_abertura'] != 'Indefinido']
atendimentos_por_bairro_1 = atendimentos_por_bairro_1[atendimentos_por_bairro_1['bairro'] != 'Indefinido']
atendimentos_por_bairro_2 = atendimentos_por_bairro_2[atendimentos_por_bairro_2['bairro'] != 'Indefinido']
atendimentos_por_classificacao = atendimentos_por_classificacao[atendimentos_por_classificacao['descricao'] != 'Indefinido']
atendimentos_por_operador_classificacao = atendimentos_por_operador_classificacao[atendimentos_por_operador_classificacao['operador_abertura'] != 'Indefinido']

# Graficos
fig_atendimento_operador_periodo = px.bar(atendimentos_por_operador_periodo,
                                          x='operador_abertura',
                                          y='Número de Atendimentos por Operador',
                                          text='Número de Atendimentos por Operador',
                                          title=f'Atendimento por Operador ({start_date.strftime("%d/%m/%Y")} - {end_date.strftime("%d/%m/%Y")})')

fig_atendimento_por_bairro_1 = px.bar(atendimentos_por_bairro_1,
                                      x='bairro',
                                      y='Número de Atendimentos por Bairro',
                                      text='Número de Atendimentos por Bairro',
                                      title='Atendimento por Bairro (Parte 1)')

fig_atendimento_por_bairro_2 = px.bar(atendimentos_por_bairro_2,
                                      x='bairro',
                                      y='Número de Atendimentos por Bairro',
                                      text='Número de Atendimentos por Bairro',
                                      title='Atendimento por Bairro (Parte 2)')


fig_atendimento_classificacao = px.bar(atendimentos_por_classificacao,
                                       x='descricao',
                                       y='Número de Atendimentos por Classificação',
                                       text='Número de Atendimentos por Classificação',
                                       title='Atendimentos por Classificação')

fig_atendimento_operador_classificacao = px.bar(atendimentos_por_operador_classificacao,
                                                x='operador_abertura',
                                                y='Número de Atendimentos',
                                                text_auto=True,
                                                color='descricao',
                                                title='Atendimentos por Operador e Classificação')



# Mestricas
df_metrica = df_filtrado[df_filtrado['em_os'] == 'N']
atendimentos_abertos = df_metrica[df_metrica['finalizado'] == 'N'].shape[0]
atendimentos_fechados = df_metrica[df_metrica['finalizado'] == 'S'].shape[0]
total_atendimentos_periodo = df_filtrado.shape[0]

df_metrica_os = df_filtrado[df_filtrado['em_os'] == 'S']
atendimentos_abertos_os = df_metrica_os[df_metrica_os['finalizado'] == 'N'].shape[0]



# Visualização
aba1, aba2, aba3 = st.tabs(['Operador', 'Classificação', 'Métricas'])


with aba1:
    st.plotly_chart(fig_atendimento_operador_periodo)
    st.plotly_chart(fig_atendimento_por_bairro_1)
    st.plotly_chart(fig_atendimento_por_bairro_2)

with aba2:
    st.plotly_chart(fig_atendimento_classificacao)
    st.plotly_chart(fig_atendimento_operador_classificacao)

# Métricas
with aba3:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric(label='Atendimentos Abertos: ', value=atendimentos_abertos)
        st.metric(label='Atendimentos Fechados: ', value=atendimentos_fechados)
    with coluna2:
        st.metric(label='Atendimentos Abertos(OS):', value=atendimentos_abertos_os)
        st.metric(label='Total de Atendimentos: ', value=total_atendimentos_periodo)

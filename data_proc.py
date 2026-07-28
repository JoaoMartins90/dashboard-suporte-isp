import pandas as pd
from utils import ler_tabela

def processa_tabela_atendimentos():
    colunas_selecionadas = """codatendimento,
                              cliente_cadastrado,
                              conexao,
                              dt_abertura,
                              bairro,
                              operador_abertura,
                              classificacao_atendimento,
                              como_foi_contato,
                              finalizado,
                              dt_finaliza,
                              operador_encerramento,
                              cd_processo,
                              em_os"""
    

    df_atendimentos = ler_tabela(colunas_selecionadas, 'mk_atendimento')
    df_atendimentos = df_atendimentos.rename(columns={'bairro': 'codbairro', 'classificacao_atendimento': 'codatclass'})
    return df_atendimentos

def processa_tabela_bairros():
    bairros = '''codbairro,
                 bairro'''

    df_bairros = ler_tabela(bairros, 'mk_bairros')
    return df_bairros


def atendimento_classificacao():
    classificacao = '''codatclass,
                       descricao'''
    df_class = ler_tabela(classificacao, 'mk_atendimento_classificacao')
    return df_class

def atendimento_pessoas():
    pessoas = '''codpessoa,
                 nome_razaosocial'''
    df_pessoas = ler_tabela(pessoas, 'mk_pessoas')
    df_pessoas_rename = df_pessoas.rename(columns={'codpessoa': 'cliente_cadastrado'})
    return df_pessoas_rename

    
def atendimento_processos():
    processos = '''codprocesso,
                   nome_processo'''
    df_processos = ler_tabela(processos, 'mk_ate_processos')
    df_processos_rename = df_processos.rename(columns={'codprocesso': 'cd_processo'})
    return df_processos_rename

def atendimento_conexao():
    conexao = '''codconexao,
                 username'''
    df_conexao = ler_tabela(conexao, 'mk_conexoes')
    df_conexao_rename = df_conexao.rename(columns={'codconexao': 'conexao'})
    return df_conexao_rename
    
def atendimento_os():
    os = '''cd_atendimento,
            codateos'''
    os = ler_tabela(os, 'mk_ate_os')
    os = os.rename(columns={'cd_atendimento': 'codatendimento'})
    return os
"""
Gera uma base SQLite de exemplo para rodar o dashboard sem acesso ao banco real.

Reproduz o schema das tabelas do MK Solutions usadas pelo projeto, com dados
fictícios. As datas são geradas a partir da data de execução, então a página de
Reincidências sempre encontra casos dentro da janela de 60 dias.

Uso:
    python seed.py

Não depende de nada além da biblioteca padrão.
"""

import os
import random
import sqlite3
from datetime import date, timedelta

SEMENTE = 42
ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_exemplo.db")

DIAS_DE_HISTORICO = 150
TOTAL_ATENDIMENTOS = 600
TOTAL_CLIENTES = 60

PROCESSOS_CONEXAO = [
    "Não Conecta",
    "Não Navega",
    "Conexão Caindo",
    "Alteração no Wi-fi",
    "Navegação Lenta",
]

PROCESSOS_OUTROS = [
    "Segunda Via de Boleto",
    "Mudança de Endereço",
    "Upgrade de Plano",
    "Cancelamento",
]

BAIRROS = [
    "Centro", "Jardim América", "Vila Nova", "Bela Vista", "Santa Luzia",
    "São José", "Parque das Flores", "Alto da Serra", "Boa Esperança",
    "Cidade Jardim", "Vila Industrial", "Recanto Verde", "Morada do Sol",
    "Nova Aurora", "Campo Belo",
]

CLASSIFICACOES = [
    "Suporte Técnico", "Financeiro", "Comercial",
    "Cancelamento", "Reclamação", "Informação",
]

OPERADORES = [
    "Ana Ribeiro", "Bruno Tavares", "Carla Mendes",
    "Diego Farias", "Elisa Nogueira", "Felipe Castro",
]

CANAIS = ["Telefone", "WhatsApp", "Presencial", "Aplicativo"]

PRIMEIROS_NOMES = [
    "Adriana", "Alexandre", "Beatriz", "Caio", "Camila", "Daniel", "Débora",
    "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Juliana", "Leonardo",
    "Mariana", "Nathalia", "Otávio", "Patrícia", "Rafael", "Sabrina",
    "Thiago", "Vanessa", "William", "Yasmin",
]

SOBRENOMES = [
    "Almeida", "Barbosa", "Cardoso", "Duarte", "Esteves", "Freitas",
    "Gonçalves", "Henriques", "Lima", "Machado", "Nunes", "Oliveira",
    "Pereira", "Queiroz", "Rocha", "Siqueira", "Teixeira", "Vieira",
]


def formata(d):
    """O dashboard espera datas como texto em dd/mm/aaaa."""
    return d.strftime("%d/%m/%Y")


def cria_tabelas(con):
    con.executescript(
        """
        DROP TABLE IF EXISTS mk_atendimento;
        DROP TABLE IF EXISTS mk_bairros;
        DROP TABLE IF EXISTS mk_atendimento_classificacao;
        DROP TABLE IF EXISTS mk_pessoas;
        DROP TABLE IF EXISTS mk_ate_processos;
        DROP TABLE IF EXISTS mk_conexoes;
        DROP TABLE IF EXISTS mk_ate_os;

        CREATE TABLE mk_atendimento (
            codatendimento           INTEGER PRIMARY KEY,
            cliente_cadastrado       INTEGER,
            conexao                  INTEGER,
            dt_abertura              TEXT,
            bairro                   INTEGER,
            operador_abertura        TEXT,
            classificacao_atendimento INTEGER,
            como_foi_contato         TEXT,
            finalizado               TEXT,
            dt_finaliza              TEXT,
            operador_encerramento    TEXT,
            cd_processo              INTEGER,
            em_os                    TEXT
        );

        CREATE TABLE mk_bairros (
            codbairro INTEGER PRIMARY KEY,
            bairro    TEXT
        );

        CREATE TABLE mk_atendimento_classificacao (
            codatclass INTEGER PRIMARY KEY,
            descricao  TEXT
        );

        CREATE TABLE mk_pessoas (
            codpessoa        INTEGER PRIMARY KEY,
            nome_razaosocial TEXT
        );

        CREATE TABLE mk_ate_processos (
            codprocesso   INTEGER PRIMARY KEY,
            nome_processo TEXT
        );

        CREATE TABLE mk_conexoes (
            codconexao INTEGER PRIMARY KEY,
            username   TEXT
        );

        CREATE TABLE mk_ate_os (
            codateos       INTEGER PRIMARY KEY,
            cd_atendimento INTEGER
        );
        """
    )


def popula_cadastros(con, rng):
    bairros = [(i + 1, nome) for i, nome in enumerate(BAIRROS)]
    con.executemany("INSERT INTO mk_bairros VALUES (?, ?)", bairros)

    classes = [(i + 1, nome) for i, nome in enumerate(CLASSIFICACOES)]
    con.executemany("INSERT INTO mk_atendimento_classificacao VALUES (?, ?)", classes)

    processos = [(i + 1, nome) for i, nome in enumerate(PROCESSOS_CONEXAO + PROCESSOS_OUTROS)]
    con.executemany("INSERT INTO mk_ate_processos VALUES (?, ?)", processos)

    pessoas, conexoes, usados = [], [], set()
    for i in range(TOTAL_CLIENTES):
        cod = 1000 + i
        nome = f"{rng.choice(PRIMEIROS_NOMES)} {rng.choice(SOBRENOMES)}"
        pessoas.append((cod, nome))

        base = nome.split()[0].lower()
        username = base
        sufixo = 1
        while username in usados:
            sufixo += 1
            username = f"{base}{sufixo}"
        usados.add(username)
        conexoes.append((cod, username))

    con.executemany("INSERT INTO mk_pessoas VALUES (?, ?)", pessoas)
    con.executemany("INSERT INTO mk_conexoes VALUES (?, ?)", conexoes)

    return [c for c, _ in pessoas], len(bairros), len(classes), len(processos)


def monta_atendimento(cod, cliente, dia, cod_processo, rng, n_bairros, n_classes):
    finalizado = "S" if rng.random() < 0.7 else "N"
    if finalizado == "S":
        fecha = dia + timedelta(days=rng.randint(0, 5))
        dt_finaliza = formata(min(fecha, date.today()))
        operador_fim = rng.choice(OPERADORES)
    else:
        dt_finaliza, operador_fim = None, None

    return (
        cod,
        cliente,
        cliente, 
        formata(dia),
        rng.randint(1, n_bairros),
        rng.choice(OPERADORES),
        rng.randint(1, n_classes),
        rng.choice(CANAIS),
        finalizado,
        dt_finaliza,
        operador_fim,
        cod_processo,
        "N",
    )


def popula_atendimentos(con, rng, clientes, n_bairros, n_classes, n_processos):
    hoje = date.today()
    atendimentos = []
    cod = 1

    # Casos de reincidência: mesmo cliente e mesmo problema, repetidos dentro
    # dos últimos 55 dias. Garante que a página de Reincidências tenha conteúdo.
    for cliente in rng.sample(clientes, 12):
        processo = rng.randint(1, len(PROCESSOS_CONEXAO))
        dia = hoje - timedelta(days=rng.randint(40, 55))
        for _ in range(rng.randint(2, 4)):
            if dia > hoje:
                break
            atendimentos.append(
                monta_atendimento(cod, cliente, dia, processo, rng, n_bairros, n_classes)
            )
            cod += 1
            dia += timedelta(days=rng.randint(6, 20))

    while cod <= TOTAL_ATENDIMENTOS:
        dia = hoje - timedelta(days=rng.randint(0, DIAS_DE_HISTORICO))
        atendimentos.append(
            monta_atendimento(
                cod, rng.choice(clientes), dia,
                rng.randint(1, n_processos), rng, n_bairros, n_classes,
            )
        )
        cod += 1

    atendimentos.append(
        monta_atendimento(cod, rng.choice(clientes), hoje,
                          rng.randint(1, n_processos), rng, n_bairros, n_classes)
    )

    con.executemany(
        "INSERT INTO mk_atendimento VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        atendimentos,
    )

    # ~15% dos atendimentos viram Ordem de Serviço.
    ordens = [
        (i + 1, linha[0])
        for i, linha in enumerate(a for a in atendimentos if rng.random() < 0.15)
    ]
    con.executemany("INSERT INTO mk_ate_os VALUES (?, ?)", ordens)

    return len(atendimentos), len(ordens)


def main():
    rng = random.Random(SEMENTE)

    if os.path.exists(ARQUIVO):
        os.remove(ARQUIVO)

    con = sqlite3.connect(ARQUIVO)
    try:
        cria_tabelas(con)
        clientes, n_bairros, n_classes, n_processos = popula_cadastros(con, rng)
        n_atend, n_os = popula_atendimentos(
            con, rng, clientes, n_bairros, n_classes, n_processos
        )
        con.commit()
    finally:
        con.close()

    print(f"Base de exemplo criada em {ARQUIVO}")
    print(f"  {n_atend} atendimentos")
    print(f"  {len(clientes)} clientes")
    print(f"  {n_bairros} bairros")
    print(f"  {n_os} ordens de serviço")
    print("\nAgora rode:  streamlit run home.py")


if __name__ == "__main__":
    main()
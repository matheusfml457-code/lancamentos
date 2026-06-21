# ─────────────────────────────────────────
#  Sistema de Lançamentos
#  Interface: Streamlit
#  Banco:     SQLite (lancamentos.db)
# ─────────────────────────────────────────

import sqlite3
import streamlit as st
import pandas as pd
import difflib
import unicodedata
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

st.set_page_config(
    page_title="Lançamentos",
    page_icon="💰",
    layout="centered",
)

st.markdown("""
<style>
    .stApp {
        background-color: #1A1A1A !important;
        color: #EDEDED !important;
    }
    .stApp p, .stApp span, .stApp label,
    .stApp h1, .stApp h2, .stApp h3,
    .stApp div { color: #EDEDED !important; }

    /* Cabeçalho do mês */
    .mes-header {
        background: #2C2C2C;
        border: 1px solid #3A3A3A;
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        font-size: 15px;
        font-weight: 600;
        color: #FF8C42 !important;
        margin-bottom: 0;
    }

    /* Tabela de lançamentos */
    .tabela-wrapper {
        background: #232323;
        border: 1px solid #3A3A3A;
        border-top: none;
        border-radius: 0 0 8px 8px;
        overflow: hidden;
        margin-bottom: 4px;
    }

    /* Container nativo (st.container border=True) usado para a lista de lançamentos */
    .lista-lancamentos div[data-testid="stVerticalBlockBorderWrapper"] {
        margin-top: -1px !important;
    }
    .lista-lancamentos div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background: #232323 !important;
        border: 1px solid #3A3A3A !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 6px 10px !important;
    }
    .lista-lancamentos div[data-testid="stVerticalBlock"] {
        gap: 0.15rem !important;
    }

    /* Bloco de checkboxes "Recebi" — remove espaçamento extra do Streamlit */
    div[class*="st-key-receber_"] {
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }
    div[class*="st-key-receber_"] div[data-testid="stVerticalBlock"] {
        gap: 0.1rem !important;
    }
    div[class*="st-key-receber_"] label[data-testid="stWidgetLabel"],
    div[class*="st-key-receber_"] div[data-testid="stCheckbox"] {
        margin: 0 !important;
        padding: 1px 0 !important;
    }
    .tabela-header {
        display: grid;
        grid-template-columns: 60px 1fr 85px 60px;
        padding: 6px 14px;
        background: #1E1E1E;
        border-bottom: 1px solid #3A3A3A;
        font-size: 10px;
        font-weight: 600;
        color: #8A8A8A !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tabela-linha {
        display: grid;
        grid-template-columns: 60px 1fr 85px 60px;
        padding: 7px 14px;
        border-bottom: 1px solid #2C2C2C;
        align-items: center;
        font-size: 13px;
    }
    .tabela-linha:last-child { border-bottom: none; }
    .tabela-linha:hover { background: #2A2A2A; }

    /* Tabela resumo */
    .resumo-wrapper {
        background: #1E1E1E;
        border: 1px solid #3A3A3A;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 10px;
        margin-bottom: 22px;
    }
    .resumo-header {
        background: #2C2C2C;
        padding: 7px 16px;
        font-size: 10px;
        font-weight: 600;
        color: #FF8C42 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .resumo-linha {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 16px;
        border-bottom: 1px solid #2C2C2C;
        font-size: 13px;
    }
    .resumo-linha:last-child { border-bottom: none; }
    .resumo-linha.destaque {
        background: #2C2C2C;
        font-weight: 600;
    }

    /* Badges - todos em tons de cinza, diferenciados só por contorno/peso */
    .badge-pix {
        background: #333333; color: #D9D9D9 !important;
        border: 1px solid #4A4A4A;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 600;
    }
    .badge-credito {
        background: #3A2A1E; color: #FFB37D !important;
        border: 1px solid #5A4030;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 600;
    }
    .badge-debito {
        background: #333333; color: #BFBFBF !important;
        border: 1px solid #4A4A4A;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 600;
    }
    .badge-receber {
        background: #2C2C2C; color: #9A9A9A !important;
        border: 1px dashed #5A5A5A;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 600;
    }
    .badge-recebido {
        background: #0E3B22; color: #4ADE80 !important;
        border: 1px solid #4ADE80;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 700;
    }
    .badge-salario {
        background: #3A2A1E; color: #FF8C42 !important;
        border: 1px solid #FF8C42;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 700;
    }

    /* Secao titulo */
    .secao-titulo {
        font-size: 12px;
        font-weight: 600;
        color: #8A8A8A !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 22px 0 8px 0;
    }

    /* Próximos meses card */
    .card-proximo {
        background: #232323;
        border: 1px solid #3A3A3A;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 6px;
    }

    .stTextInput input, .stNumberInput input {
        background-color: #232323 !important;
        color: #EDEDED !important;
        border: 1px solid #3A3A3A !important;
    }
    input[type=number]::-webkit-inner-spin-button,
    input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; }
    input[type=number] { -moz-appearance: textfield; }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #FF8C42 !important;
        color: #1A1A1A !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover { background-color: #E67A33 !important; }

    .btn-voltar > button {
        width: auto !important;
        background-color: #232323 !important;
        color: #BFBFBF !important;
        border: 1px solid #3A3A3A !important;
        padding: 4px 14px !important;
        font-size: 13px !important;
        font-weight: 400 !important;
    }

    /* Botões de ação pequenos (editar/excluir) nas linhas da tabela */
    div[class*="st-key-btn_edit_"] .stButton,
    div[class*="st-key-btn_confirm_del_"] .stButton {
        margin: 0 !important;
    }
    div[class*="st-key-btn_edit_"] button,
    div[class*="st-key-btn_confirm_del_"] button {
        background-color: transparent !important;
        border: none !important;
        border-radius: 5px !important;
        width: 26px !important;
        height: 26px !important;
        min-height: 26px !important;
        min-width: 26px !important;
        max-width: 26px !important;
        max-height: 26px !important;
        padding: 0 !important;
        margin: 2px auto 0 auto !important;
        font-size: 14px !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: visible !important;
        box-shadow: none !important;
        filter: none !important;
        -webkit-text-fill-color: initial !important;
    }
    div[class*="st-key-btn_edit_"] button p,
    div[class*="st-key-btn_confirm_del_"] button p {
        font-size: 14px !important;
        line-height: 1 !important;
        margin: 0 !important;
        color: #6B6B6B;
    }
    div[class*="st-key-btn_edit_"] button:hover,
    div[class*="st-key-btn_confirm_del_"] button:hover {
        background-color: #2C2C2C !important;
    }
    div[class*="st-key-btn_edit_"] button:hover p,
    div[class*="st-key-btn_confirm_del_"] button:hover p {
        color: #FF8C42 !important;
    }

    .block-container { padding-top: 1.5rem; }

    /* Reduz o espaçamento padrão (generoso) que o Streamlit insere entre
       elementos consecutivos no fluxo principal da página */
    .block-container > div[data-testid="stVerticalBlock"] {
        gap: 0.25rem !important;
    }
    div[data-testid="stElementContainer"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #232323;
        border-radius: 8px 8px 0 0;
        padding: 6px 16px;
        color: #8A8A8A !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF8C42 !important;
        color: #1A1A1A !important;
    }
    .stTabs [aria-selected="true"] p { color: #1A1A1A !important; }

    /* KPI cards */
    .kpi-card {
        background: #232323;
        border: 1px solid #3A3A3A;
        border-radius: 8px;
        padding: 12px 14px;
        text-align: left;
    }
    .kpi-label {
        font-size: 10px;
        font-weight: 600;
        color: #8A8A8A !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 18px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "lancamentos.db"

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}
MESES_PT_ABREV = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

BADGE_HTML = {
    "Pix":       '<span class="badge-pix">Pix</span>',
    "Credito":   '<span class="badge-credito">Crédito</span>',
    "Debito":    '<span class="badge-debito">Débito</span>',
    "A receber": '<span class="badge-receber">A receber</span>',
    "Salario":   '<span class="badge-salario">Salário</span>',
}

# Tipos de pagamento que representam SAÍDAS de dinheiro do mês
TIPOS_SAIDA = ["Pix", "Credito", "Debito"]
# Tipos de pagamento que representam ENTRADAS de dinheiro
TIPOS_ENTRADA = ["Salario"]


# ══════════════════════════════════════════
#  BANCO DE DADOS
# ══════════════════════════════════════════

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lancamentos (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                data_compra   TEXT    NOT NULL,
                descricao     TEXT    NOT NULL,
                pagamento     TEXT    NOT NULL,
                valor_total   REAL    NOT NULL,
                qtd_parcelas  INTEGER NOT NULL,
                valor_parcela REAL    NOT NULL,
                criado_em     TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS parcelas (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                lancamento_id  INTEGER NOT NULL,
                numero         INTEGER NOT NULL,
                vencimento     TEXT    NOT NULL,
                valor          REAL    NOT NULL,
                recebido       INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (lancamento_id) REFERENCES lancamentos(id)
            )
        """)
        # Compatibilidade: adiciona coluna 'recebido' se ainda não existir
        cols = [r[1] for r in conn.execute("PRAGMA table_info(parcelas)").fetchall()]
        if "recebido" not in cols:
            conn.execute("ALTER TABLE parcelas ADD COLUMN recebido INTEGER NOT NULL DEFAULT 0")

def salvar_lancamento(dados: dict) -> int:
    data_compra = datetime.strptime(dados["data"], "%d/%m/%Y")
    with conectar() as conn:
        cursor = conn.execute("""
            INSERT INTO lancamentos
                (data_compra, descricao, pagamento, valor_total, qtd_parcelas, valor_parcela)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (dados["data"], dados["descricao"], dados["pagamento"],
              dados["valor_total"], dados["qtd_parcelas"], dados["valor_parcela"]))
        lid = cursor.lastrowid

        qtd = dados["qtd_parcelas"]
        valor_base = dados["valor_total"] // qtd if False else None  # placeholder (não usado)

        # Ajusta arredondamento: distribui centavos na última parcela
        valor_parcela = dados["valor_parcela"]
        soma_parcelas = round(valor_parcela * qtd, 2)
        diferenca = round(dados["valor_total"] - soma_parcelas, 2)

        for i in range(qtd):
            venc = data_compra + relativedelta(months=i)
            valor_i = valor_parcela
            if i == qtd - 1:
                valor_i = round(valor_parcela + diferenca, 2)
            conn.execute("""
                INSERT INTO parcelas (lancamento_id, numero, vencimento, valor)
                VALUES (?, ?, ?, ?)
            """, (lid, i + 1, venc.strftime("%Y-%m-%d"), valor_i))
    return lid

def marcar_recebido(parcela_id: int, recebido: bool):
    with conectar() as conn:
        conn.execute("UPDATE parcelas SET recebido = ? WHERE id = ?",
                     (1 if recebido else 0, parcela_id))

def buscar_meses_com_parcelas():
    with conectar() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT strftime('%Y-%m', vencimento) AS ano_mes,
                   COUNT(*) AS total_parcelas, SUM(valor) AS total_valor
            FROM parcelas GROUP BY ano_mes ORDER BY ano_mes
        """).fetchall()
    resultado = []
    for r in rows:
        ano, mes = r["ano_mes"].split("-")
        resultado.append({
            "ano_mes": r["ano_mes"],
            "label": f"{MESES_PT[int(mes)]}/{ano}",
            "total_parcelas": r["total_parcelas"],
            "total_valor": r["total_valor"],
        })
    return resultado

def buscar_parcelas_do_mes(ano_mes: str):
    with conectar() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT p.id, p.lancamento_id, p.numero, p.vencimento, p.valor, p.recebido,
                   l.descricao, l.pagamento, l.qtd_parcelas, l.data_compra
            FROM parcelas p JOIN lancamentos l ON l.id = p.lancamento_id
            WHERE strftime('%Y-%m', p.vencimento) = ?
            ORDER BY l.data_compra ASC, l.id ASC
        """, (ano_mes,)).fetchall()
    return [dict(r) for r in rows]

def normalizar_texto(texto: str) -> str:
    """Remove acentos e baixa a caixa, para comparação tolerante."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII")
    return texto

def similaridade_descricao(busca_norm: str, descricao: str) -> float:
    """
    Retorna um score de 0 a 1 indicando o quanto a descrição combina com o termo buscado.
    1.0 = o termo aparece literalmente dentro da descrição (após normalizar acentos/caixa).
    Caso contrário, usa similaridade aproximada (tolera letras trocadas/faltando) comparando
    tanto a descrição inteira quanto cada palavra dela isoladamente.
    """
    desc_norm = normalizar_texto(descricao)
    if busca_norm in desc_norm:
        return 1.0
    melhor = difflib.SequenceMatcher(None, busca_norm, desc_norm).ratio()
    for palavra in desc_norm.split():
        score = difflib.SequenceMatcher(None, busca_norm, palavra).ratio()
        if score > melhor:
            melhor = score
    return melhor

LIMIAR_BUSCA = 0.65  # quanto menor, mais tolerante a erros de digitação

def buscar_parcelas_por_descricao(termo: str):
    """
    Busca todas as parcelas cujo lançamento tem descrição parecida com o termo.
    Tolerante a acentuação e pequenos erros de digitação (não precisa ser exato).
    """
    termo_norm = normalizar_texto(termo)
    if not termo_norm:
        return []

    with conectar() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT p.id, p.lancamento_id, p.numero, p.vencimento, p.valor, p.recebido,
                   l.descricao, l.pagamento, l.qtd_parcelas, l.data_compra
            FROM parcelas p JOIN lancamentos l ON l.id = p.lancamento_id
        """).fetchall()

    candidatos = []
    for r in rows:
        score = similaridade_descricao(termo_norm, r["descricao"])
        if score >= LIMIAR_BUSCA:
            candidatos.append((score, dict(r)))

    # Ordena por relevância (melhor match primeiro); empates ficam por data mais recente.
    # sort() é estável, então ordenamos primeiro por data e depois por score.
    candidatos.sort(key=lambda x: x[1]["vencimento"], reverse=True)
    candidatos.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in candidatos]

def buscar_lancamento(lancamento_id: int):
    with conectar() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("""
            SELECT id, data_compra, descricao, pagamento, valor_total, qtd_parcelas, valor_parcela
            FROM lancamentos WHERE id = ?
        """, (lancamento_id,)).fetchone()
    return dict(row) if row else None

def excluir_lancamento(lancamento_id: int):
    with conectar() as conn:
        conn.execute("DELETE FROM parcelas WHERE lancamento_id = ?", (lancamento_id,))
        conn.execute("DELETE FROM lancamentos WHERE id = ?", (lancamento_id,))

def atualizar_lancamento(lancamento_id: int, dados: dict):
    """Atualiza um lançamento existente, recriando suas parcelas do zero."""
    data_compra = datetime.strptime(dados["data"], "%d/%m/%Y")
    with conectar() as conn:
        conn.execute("""
            UPDATE lancamentos
            SET data_compra = ?, descricao = ?, pagamento = ?,
                valor_total = ?, qtd_parcelas = ?, valor_parcela = ?
            WHERE id = ?
        """, (dados["data"], dados["descricao"], dados["pagamento"],
              dados["valor_total"], dados["qtd_parcelas"], dados["valor_parcela"],
              lancamento_id))

        # Remove parcelas antigas e recria
        conn.execute("DELETE FROM parcelas WHERE lancamento_id = ?", (lancamento_id,))

        qtd = dados["qtd_parcelas"]
        valor_parcela = dados["valor_parcela"]
        soma_parcelas = round(valor_parcela * qtd, 2)
        diferenca = round(dados["valor_total"] - soma_parcelas, 2)

        for i in range(qtd):
            venc = data_compra + relativedelta(months=i)
            valor_i = valor_parcela
            if i == qtd - 1:
                valor_i = round(valor_parcela + diferenca, 2)
            conn.execute("""
                INSERT INTO parcelas (lancamento_id, numero, vencimento, valor)
                VALUES (?, ?, ?, ?)
            """, (lancamento_id, i + 1, venc.strftime("%Y-%m-%d"), valor_i))

def buscar_lancamentos_do_mes(ano_mes: str):
    """Retorna lançamentos únicos (não parcelas) cujo vencimento de alguma parcela cai no mês."""
    with conectar() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT DISTINCT l.id, l.data_compra, l.descricao, l.pagamento,
                   l.valor_total, l.qtd_parcelas, l.valor_parcela
            FROM lancamentos l JOIN parcelas p ON p.lancamento_id = l.id
            WHERE strftime('%Y-%m', p.vencimento) = ?
            ORDER BY l.data_compra ASC, l.id ASC
        """, (ano_mes,)).fetchall()
    return [dict(r) for r in rows]

def buscar_resumo_mes(parcelas: list) -> dict:
    pix       = sum(p["valor"] for p in parcelas if p["pagamento"] == "Pix")
    credito   = sum(p["valor"] for p in parcelas if p["pagamento"] == "Credito")
    debito    = sum(p["valor"] for p in parcelas if p["pagamento"] == "Debito")
    a_receber = sum(p["valor"] for p in parcelas if p["pagamento"] == "A receber")
    recebido  = sum(p["valor"] for p in parcelas if p["pagamento"] == "A receber" and p["recebido"])
    salario   = sum(p["valor"] for p in parcelas if p["pagamento"] == "Salario")

    saidas    = pix + credito + debito
    entradas  = salario + recebido
    saldo     = entradas - saidas

    return {
        "pix": pix, "credito": credito, "debito": debito,
        "a_receber": a_receber, "recebido": recebido, "salario": salario,
        "saidas": saidas, "entradas": entradas, "saldo": saldo,
    }

def buscar_dados_anuais(ano: int):
    """Retorna totais mensais de entradas e saídas para um ano específico."""
    with conectar() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT strftime('%Y-%m', p.vencimento) AS ano_mes, l.pagamento, p.valor, p.recebido
            FROM parcelas p JOIN lancamentos l ON l.id = p.lancamento_id
            WHERE strftime('%Y', p.vencimento) = ?
        """, (str(ano),)).fetchall()

    dados = {m: {"entradas": 0.0, "saidas": 0.0} for m in range(1, 13)}
    for r in rows:
        mes = int(r["ano_mes"].split("-")[1])
        if r["pagamento"] in TIPOS_SAIDA:
            dados[mes]["saidas"] += r["valor"]
        elif r["pagamento"] == "Salario":
            dados[mes]["entradas"] += r["valor"]
        elif r["pagamento"] == "A receber" and r["recebido"]:
            dados[mes]["entradas"] += r["valor"]

    df = pd.DataFrame([
        {
            "Mês": MESES_PT_ABREV[m],
            "Entradas": round(dados[m]["entradas"], 2),
            "Saídas": round(dados[m]["saidas"], 2),
            "Saldo": round(dados[m]["entradas"] - dados[m]["saidas"], 2),
        }
        for m in range(1, 13)
    ])
    return df

def buscar_anos_disponiveis():
    with conectar() as conn:
        rows = conn.execute("""
            SELECT DISTINCT strftime('%Y', vencimento) AS ano
            FROM parcelas ORDER BY ano
        """).fetchall()
    anos = [int(r[0]) for r in rows]
    if not anos:
        anos = [date.today().year]
    return anos


# ══════════════════════════════════════════
#  ESTADO
# ══════════════════════════════════════════

if "tela" not in st.session_state:
    st.session_state.tela = "inicio"
if "mes_selecionado" not in st.session_state:
    st.session_state.mes_selecionado = None
if "qtd_temp" not in st.session_state:
    st.session_state.qtd_temp = 1
if "proximo_aberto" not in st.session_state:
    st.session_state.proximo_aberto = None

criar_tabelas()

MES_ATUAL     = date.today().strftime("%Y-%m")
MES_ATUAL_NUM = date.today().month
ANO_ATUAL     = date.today().year
LABEL_ATUAL   = f"{MESES_PT[MES_ATUAL_NUM]}/{ANO_ATUAL}"


# ══════════════════════════════════════════
#  COMPONENTES
# ══════════════════════════════════════════

def bloco_mes(label: str, parcelas: list, chave_prefix: str, ano_mes: str = None,
               mostrar_resumo: bool = True, mostrar_ano: bool = False):
    """
    Renderiza o bloco completo de um mês:
    cabeçalho azul + tabela de lançamentos + tabela resumo.
    O check de 'recebido' só aparece em lançamentos 'A receber'.
    mostrar_resumo=False omite a tabela de resumo financeiro (usado na busca,
    onde os lançamentos podem ser de meses diferentes).
    mostrar_ano=True mostra dd/mm/aaaa em vez de dd/mm (também usado na busca).
    """
    resumo = buscar_resumo_mes(parcelas)

    # Cabeçalho
    st.markdown(f'<div class="mes-header">📅 {label}</div>', unsafe_allow_html=True)

    # Cabeçalho das colunas
    st.markdown(f"""
    <div class="tabela-wrapper" style="border-radius: 0;">
        <div class="tabela-header" style="grid-template-columns: 55px 1fr 80px 85px 30px 30px;">
            <span>Data</span>
            <span>Descrição</span>
            <span>Tipo</span>
            <span style="text-align:right">Valor</span>
            <span></span>
            <span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="lista-lancamentos">', unsafe_allow_html=True)
    container_tabela = st.container(border=True)
    with container_tabela:
        for p in parcelas:
            if mostrar_ano:
                data_fmt = datetime.strptime(p["vencimento"], "%Y-%m-%d").strftime("%d/%m/%Y")
            else:
                data_fmt = datetime.strptime(p["data_compra"], "%d/%m/%Y").strftime("%d/%m")
            parcela_txt = f"{p['numero']}/{p['qtd_parcelas']}" if p["qtd_parcelas"] > 1 else "1/1"
            badge     = BADGE_HTML.get(p["pagamento"], p["pagamento"])

            if p["pagamento"] == "A receber":
                if p["recebido"]:
                    valor_html = f'<span style="color:#4ADE80; font-weight:600">R$ {p["valor"]:.2f}</span>'
                    badge = '<span class="badge-recebido">Recebido ✓</span>'
                else:
                    valor_html = f'<span style="color:#9A9A9A; font-weight:600">R$ {p["valor"]:.2f}</span>'
            elif p["pagamento"] == "Salario":
                valor_html = f'<span style="color:#FF8C42; font-weight:700">+ R$ {p["valor"]:.2f}</span>'
            else:
                valor_html = f'<span style="color:#D9D9D9; font-weight:600">R$ {p["valor"]:.2f}</span>'

            desc_html = f'{p["descricao"]} <span style="color:#8A8A8A; font-size:11px">· {parcela_txt}</span>'

            lancamento_id = p["lancamento_id"]
            edit_key = f"edit_{chave_prefix}_{p['id']}"
            confirm_key = f"confirm_del_{chave_prefix}_{p['id']}"

            largura_data = 1.1 if mostrar_ano else 0.7
            col_data, col_desc, col_tipo, col_valor, col_edit, col_del = st.columns(
                [largura_data, 2.6, 1.0, 1.1, 0.35, 0.35], vertical_alignment="top", gap="small"
            )
            with col_data:
                st.markdown(
                    f'<div style="font-size:13px; color:#8A8A8A; padding-top:4px;">{data_fmt}</div>',
                    unsafe_allow_html=True,
                )
            with col_desc:
                st.markdown(
                    f'<div style="font-size:13px; padding-top:4px;">{desc_html}</div>',
                    unsafe_allow_html=True,
                )
            with col_tipo:
                st.markdown(
                    f'<div style="padding-top:2px;">{badge}</div>',
                    unsafe_allow_html=True,
                )
            with col_valor:
                st.markdown(
                    f'<div style="font-size:13px; text-align:right; padding-top:4px;">{valor_html}</div>',
                    unsafe_allow_html=True,
                )
            with col_edit:
                if st.button("✎", key=f"btn_{edit_key}", help="Editar lançamento"):
                    st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                    st.rerun()
            with col_del:
                if st.button("🗑", key=f"btn_{confirm_key}", help="Excluir lançamento"):
                    st.session_state[confirm_key] = not st.session_state.get(confirm_key, False)
                    st.rerun()

            # Confirmação de exclusão
            if st.session_state.get(confirm_key, False):
                st.warning(f"Excluir **{p['descricao']}** permanentemente? Isso remove todas as parcelas deste lançamento.")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Sim, excluir", key=f"yes_{confirm_key}", use_container_width=True):
                        excluir_lancamento(lancamento_id)
                        st.session_state[confirm_key] = False
                        st.rerun()
                with c2:
                    if st.button("Cancelar", key=f"no_{confirm_key}", use_container_width=True):
                        st.session_state[confirm_key] = False
                        st.rerun()

            # Formulário de edição
            if st.session_state.get(edit_key, False):
                lancamento_completo = buscar_lancamento(lancamento_id)
                if lancamento_completo:
                    with st.container():
                        st.markdown(
                            '<div style="background:#1E1E1E; border:1px solid #3A3A3A; '
                            'border-radius:8px; padding:12px 14px; margin:4px 0 10px 0;">',
                            unsafe_allow_html=True,
                        )
                        formulario_edicao_lancamento(lancamento_completo, edit_key)
                        st.markdown('</div>', unsafe_allow_html=True)

            if p is not parcelas[-1]:
                st.markdown(
                    "<hr style='border-color:#2C2C2C; margin:1px 0;'>",
                    unsafe_allow_html=True,
                )

    st.markdown('</div>', unsafe_allow_html=True)

    # Checkboxes para "A receber" — fora do HTML para ter interação
    receber_list = [p for p in parcelas if p["pagamento"] == "A receber"]
    if receber_list:
        container_receber = st.container(key=f"receber_{chave_prefix}")
        with container_receber:
            for p in receber_list:
                marcado = bool(p["recebido"])
                novo = st.checkbox(
                    f"✓  Recebi: {p['descricao']}  (R$ {p['valor']:.2f})",
                    value=marcado,
                    key=f"rec_{chave_prefix}_{p['id']}",
                )
                if novo != marcado:
                    marcar_recebido(p["id"], novo)
                    st.rerun()

    # Tabela resumo
    if mostrar_resumo:
        pendente = resumo["a_receber"] - resumo["recebido"]
        saldo_cor = "#FF8C42" if resumo["saldo"] >= 0 else "#A3A3A3"
        st.markdown(f"""
        <div class="resumo-wrapper">
            <div class="resumo-header">Resumo do mês</div>
            <div class="resumo-linha">
                <span><span class="badge-salario">Salário</span></span>
                <span style="font-weight:600; color:#FF8C42">+ R$ {resumo['salario']:.2f}</span>
            </div>
            <div class="resumo-linha">
                <span><span class="badge-pix">Pix</span></span>
                <span style="font-weight:600">R$ {resumo['pix']:.2f}</span>
            </div>
            <div class="resumo-linha">
                <span><span class="badge-credito">Crédito</span></span>
                <span style="font-weight:600">R$ {resumo['credito']:.2f}</span>
            </div>
            <div class="resumo-linha">
                <span><span class="badge-debito">Débito</span></span>
                <span style="font-weight:600">R$ {resumo['debito']:.2f}</span>
            </div>
            <div class="resumo-linha">
                <span><span class="badge-receber">A receber</span>
                <span style="color:#8A8A8A; font-size:11px; margin-left:6px">
                    (recebido R$ {resumo['recebido']:.2f} · pendente R$ {pendente:.2f})
                </span></span>
                <span style="color:#C9C9C9; font-weight:600">R$ {resumo['a_receber']:.2f}</span>
            </div>
            <div class="resumo-linha destaque">
                <span style="color:#8A8A8A">Total saídas</span>
                <span style="color:#D9D9D9">R$ {resumo['saidas']:.2f}</span>
            </div>
            <div class="resumo-linha destaque">
                <span style="color:#8A8A8A">Total entradas</span>
                <span style="color:#FF8C42">R$ {resumo['entradas']:.2f}</span>
            </div>
            <div class="resumo-linha destaque">
                <span style="color:#EDEDED; font-weight:700">Saldo do mês</span>
                <span style="color:{saldo_cor}; font-weight:700">R$ {resumo['saldo']:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def formulario_edicao_lancamento(l: dict, edit_key: str):
    """Formulário inline para editar um lançamento existente."""
    pref = f"f_{edit_key}"

    data_atual = datetime.strptime(l["data_compra"], "%d/%m/%Y").date()
    nova_data = st.date_input(
        "Data da compra", value=data_atual,
        min_value=date(2026, 1, 1), format="DD/MM/YYYY",
        key=f"{pref}_data",
    )

    nova_desc = st.text_input("Descrição", value=l["descricao"], key=f"{pref}_desc")

    opcoes_pag = ["Pix", "Credito", "Debito", "A receber", "Salario"]
    idx_pag = opcoes_pag.index(l["pagamento"]) if l["pagamento"] in opcoes_pag else 0
    novo_pag = st.radio(
        "Forma de pagamento", opcoes_pag,
        index=idx_pag,
        format_func=lambda x: {"Pix": "Pix", "Credito": "Crédito",
                                "Debito": "Débito", "A receber": "A receber",
                                "Salario": "Salário"}[x],
        horizontal=True, key=f"{pref}_pag",
    )

    novo_valor = st.number_input(
        "Valor total (R$)", min_value=0.01, value=float(l["valor_total"]),
        step=0.01, format="%.2f", key=f"{pref}_valor",
    )

    nova_qtd = 1
    if novo_pag == "Credito":
        nova_qtd = st.number_input(
            "Parcelas", min_value=1, max_value=48,
            value=int(l["qtd_parcelas"]), step=1, key=f"{pref}_qtd",
        )
        nova_qtd = int(nova_qtd)
        if nova_valor and nova_qtd > 1:
            st.caption(f"📌 {nova_qtd}x de R$ {nova_valor / nova_qtd:.2f}")

    col_salvar, col_cancelar = st.columns(2)
    with col_salvar:
        if st.button("Salvar alterações", key=f"{pref}_salvar", use_container_width=True):
            if not nova_desc.strip():
                st.error("Digite uma descrição.")
            elif not novo_valor or novo_valor <= 0:
                st.error("Digite um valor maior que zero.")
            else:
                valor_parcela = round(novo_valor / nova_qtd, 2)
                atualizar_lancamento(l["id"], {
                    "data": nova_data.strftime("%d/%m/%Y"),
                    "descricao": nova_desc.strip(),
                    "pagamento": novo_pag,
                    "valor_total": novo_valor,
                    "qtd_parcelas": nova_qtd,
                    "valor_parcela": valor_parcela,
                })
                st.session_state[edit_key] = False
                st.rerun()
    with col_cancelar:
        if st.button("Cancelar", key=f"{pref}_cancelar", use_container_width=True):
            st.session_state[edit_key] = False
            st.rerun()

def botao_voltar(destino: str):
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    if st.button("← Voltar"):
        st.session_state.tela = destino
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
#  TELA: INÍCIO (Lançamentos)
# ══════════════════════════════════════════

def tela_lancamentos():
    if st.button("+ Novo lançamento", use_container_width=True):
        st.session_state.qtd_temp = 1
        if "qtd_parcelas" in st.session_state:
            del st.session_state["qtd_parcelas"]
        st.session_state.tela = "novo"
        st.rerun()

    termo_busca = st.text_input(
        "Buscar", placeholder="🔍 Buscar por descrição...",
        label_visibility="collapsed", key="termo_busca",
    )

    st.markdown("<hr style='border-color:#3A3A3A; margin:10px 0;'>", unsafe_allow_html=True)
    if termo_busca and termo_busca.strip():
        resultados = buscar_parcelas_por_descricao(termo_busca.strip())
        st.markdown(
            f'<div class="secao-titulo">Resultados para "{termo_busca.strip()}" '
            f'({len(resultados)})</div>',
            unsafe_allow_html=True,
        )
        if resultados:
            bloco_mes("🔍 Busca", resultados, "busca", ano_mes=None,
                      mostrar_resumo=False, mostrar_ano=True)
        else:
            st.info("Nenhum lançamento encontrado com essa descrição.")
        return

    todos_meses = buscar_meses_com_parcelas()
    anteriores  = [m for m in todos_meses if m["ano_mes"] < MES_ATUAL]
    proximos    = [m for m in todos_meses if m["ano_mes"] > MES_ATUAL]
    atual_list  = [m for m in todos_meses if m["ano_mes"] == MES_ATUAL]

    # ── MÊS ATUAL ──
    st.markdown('<div class="secao-titulo">Mês atual</div>', unsafe_allow_html=True)
    if atual_list:
        parcelas_atual = buscar_parcelas_do_mes(MES_ATUAL)
        bloco_mes(LABEL_ATUAL, parcelas_atual, "atual", ano_mes=MES_ATUAL)
    else:
        st.info("Nenhum lançamento este mês ainda.")

    # ── PRÓXIMOS MESES ──
    if proximos:
        st.markdown('<div class="secao-titulo">Próximos meses</div>', unsafe_allow_html=True)

        st.markdown("""
        <style>
        div[data-testid="stButton"].btn-mes > button {
            background-color: #232323 !important;
            color: #EDEDED !important;
            border: 1px solid #3A3A3A !important;
            border-radius: 8px !important;
            text-align: left !important;
            padding: 12px 16px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            margin-bottom: 4px;
        }
        div[data-testid="stButton"].btn-mes > button:hover {
            border-color: #FF8C42 !important;
            background-color: #2A2A2A !important;
        }
        </style>
        """, unsafe_allow_html=True)

        for m in proximos:
            aberto = st.session_state.proximo_aberto == m["ano_mes"]
            icone  = "▼" if aberto else "▶"
            label  = f"{icone}  {m['label']}    R$ {m['total_valor']:.2f}  ·  {m['total_parcelas']} parcela(s)"

            st.markdown('<div class="btn-mes">', unsafe_allow_html=True)
            if st.button(label, key=f"prox_{m['ano_mes']}", use_container_width=True):
                st.session_state.proximo_aberto = None if aberto else m["ano_mes"]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            if aberto:
                parcelas_mes = buscar_parcelas_do_mes(m["ano_mes"])
                bloco_mes(m["label"], parcelas_mes, f"prox_{m['ano_mes']}", ano_mes=m["ano_mes"])

    # ── MESES ANTERIORES ──
    if anteriores:
        st.markdown('<div class="secao-titulo">Meses anteriores</div>', unsafe_allow_html=True)
        for m in reversed(anteriores):
            st.markdown(f"""
            <div class="card-proximo">
                <div style="display:flex; justify-content:space-between; align-items:center">
                    <span style="font-weight:600">{m['label']}</span>
                    <span style="color:#FF8C42; font-weight:700">R$ {m['total_valor']:.2f}</span>
                </div>
                <div style="color:#8A8A8A; font-size:12px; margin-top:3px">
                    {m['total_parcelas']} parcela(s)
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Ver {m['label']}", key=f"ant_{m['ano_mes']}",
                         use_container_width=True):
                st.session_state.mes_selecionado = m
                st.session_state.tela = "detalhe_mes"
                st.rerun()


# ══════════════════════════════════════════
#  TELA: RESUMO ANUAL
# ══════════════════════════════════════════

def tela_resumo_anual():
    anos = buscar_anos_disponiveis()
    ano_padrao = ANO_ATUAL if ANO_ATUAL in anos else anos[-1]
    ano_idx = anos.index(ano_padrao) if ano_padrao in anos else len(anos) - 1

    ano = st.selectbox("Ano", anos, index=ano_idx, label_visibility="collapsed")

    df = buscar_dados_anuais(ano)

    total_entradas = df["Entradas"].sum()
    total_saidas   = df["Saídas"].sum()
    total_saldo    = total_entradas - total_saidas
    saldo_cor      = "#FF8C42" if total_saldo >= 0 else "#A3A3A3"

    def fmt_brl(v):
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # KPIs
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Entradas {ano}</div>
            <div class="kpi-value" style="color:#FF8C42">{fmt_brl(total_entradas)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Saídas {ano}</div>
            <div class="kpi-value" style="color:#D9D9D9">{fmt_brl(total_saidas)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Saldo {ano}</div>
            <div class="kpi-value" style="color:{saldo_cor}">{fmt_brl(total_saldo)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="secao-titulo">Entradas x Saídas por mês</div>', unsafe_allow_html=True)

    import plotly.graph_objects as go

    meses_ordem = df["Mês"].tolist()

    fig1 = go.Figure()
    fig1.add_bar(name="Entradas", x=meses_ordem, y=df["Entradas"], marker_color="#FF8C42")
    fig1.add_bar(name="Saídas", x=meses_ordem, y=df["Saídas"], marker_color="#5A5A5A")
    fig1.update_layout(
        barmode="group",
        height=260,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="#1E1E1E",
        paper_bgcolor="#1E1E1E",
        font_color="#EDEDED",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        xaxis=dict(
            categoryorder="array",
            categoryarray=meses_ordem,
            tickangle=0,
            gridcolor="#2C2C2C",
        ),
        yaxis=dict(gridcolor="#2C2C2C"),
    )
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="secao-titulo">Saldo mensal</div>', unsafe_allow_html=True)

    cores_saldo = ["#FF8C42" if v >= 0 else "#5A5A5A" for v in df["Saldo"]]
    fig2 = go.Figure()
    fig2.add_bar(x=meses_ordem, y=df["Saldo"], marker_color=cores_saldo)
    fig2.update_layout(
        height=200,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="#1E1E1E",
        paper_bgcolor="#1E1E1E",
        font_color="#EDEDED",
        showlegend=False,
        xaxis=dict(
            categoryorder="array",
            categoryarray=meses_ordem,
            tickangle=0,
            gridcolor="#2C2C2C",
        ),
        yaxis=dict(gridcolor="#2C2C2C"),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Tabela resumo mensal — meses na horizontal (colunas), valores na vertical (linhas)
    st.markdown('<div class="secao-titulo">Detalhe mensal</div>', unsafe_allow_html=True)

    meses = df["Mês"].tolist()
    n_meses = len(meses)
    col_width = max(60, int(420 / (n_meses + 1)))

    def linha_tabela(label, valores, cor=None, destaque=False, cor_por_valor=False):
        peso = "font-weight:700;" if destaque else "font-weight:500;"
        bg = "background:#2C2C2C;" if destaque else ""
        celulas = ""
        for v in valores:
            if cor_por_valor:
                cor_cel = "#FF8C42" if v >= 0 else "#A3A3A3"
            else:
                cor_cel = cor or "#EDEDED"
            valor_fmt = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            celulas += (
                f'<td style="padding:6px 8px; text-align:right; color:{cor_cel}; {peso} '
                f'border-bottom:1px solid #2C2C2C; font-size:12px; white-space:nowrap;">'
                f'{valor_fmt}</td>'
            )
        return (
            f'<tr style="{bg}">'
            f'<td style="padding:6px 8px; color:#8A8A8A; font-size:11px; font-weight:600; '
            f'text-transform:uppercase; letter-spacing:0.5px; border-bottom:1px solid #2C2C2C; '
            f'white-space:nowrap; position:sticky; left:0; background:#1E1E1E;">{label}</td>'
            f'{celulas}</tr>'
        )

    header_cells = "".join(
        f'<th style="padding:6px 6px; text-align:right; font-size:11px; font-weight:600; '
        f'color:#8A8A8A; text-transform:uppercase; letter-spacing:0.5px; '
        f'border-bottom:1px solid #3A3A3A; white-space:nowrap; writing-mode:horizontal-tb; '
        f'min-width:48px;">{m}</th>'
        for m in meses
    )

    tabela_html = f"""
    <div class="tabela-wrapper" style="overflow-x:auto; border-radius:8px;">
        <table style="width:100%; border-collapse:collapse;">
            <thead>
                <tr style="background:#1E1E1E;">
                    <th style="padding:6px 8px; border-bottom:1px solid #3A3A3A; position:sticky; left:0; background:#1E1E1E;"></th>
                    {header_cells}
                </tr>
            </thead>
            <tbody>
                {linha_tabela("Entradas", df["Entradas"].tolist(), cor="#FF8C42")}
                {linha_tabela("Saídas", df["Saídas"].tolist(), cor="#D9D9D9")}
                {linha_tabela("Saldo", df["Saldo"].tolist(), destaque=True, cor_por_valor=True)}
            </tbody>
        </table>
    </div>
    """
    st.markdown(tabela_html, unsafe_allow_html=True)


# ══════════════════════════════════════════
#  TELA: NOVO LANÇAMENTO
# ══════════════════════════════════════════

def tela_novo_lancamento():
    botao_voltar("inicio")
    st.title("Novo Lançamento")

    data_val = st.date_input(
        "Data da compra",
        value=date.today() if date.today().year >= 2026 else date(2026, 1, 1),
        min_value=date(2026, 1, 1),
        format="DD/MM/YYYY",
    )

    descricao = st.text_input("Descrição")

    pagamento = st.radio(
        "Forma de pagamento",
        ["Pix", "Credito", "Debito", "A receber", "Salario"],
        format_func=lambda x: {"Pix": "Pix", "Credito": "Crédito",
                                "Debito": "Débito", "A receber": "A receber",
                                "Salario": "Salário"}[x],
        horizontal=True,
    )

    valor_total = st.number_input(
        "Valor total (R$)",
        min_value=0.01,
        value=None,
        step=0.01,
        format="%.2f",
        placeholder="0,00",
    )

    qtd_parcelas = 1
    if pagamento == "Credito":
        if "qtd_parcelas" not in st.session_state:
            st.session_state.qtd_parcelas = st.session_state.qtd_temp

        col_num, _ = st.columns([1, 3])
        with col_num:
            qtd_parcelas = st.number_input(
                "Parcelas", min_value=1, max_value=48,
                step=1, key="qtd_parcelas",
            )
            qtd_parcelas = int(qtd_parcelas)
            st.session_state.qtd_temp = qtd_parcelas

        if valor_total and qtd_parcelas > 1:
            st.caption(f"📌 {qtd_parcelas}x de R$ {valor_total / qtd_parcelas:.2f}")

    st.divider()

    if st.button("Salvar lançamento", use_container_width=True):
        if not descricao.strip():
            st.error("Digite uma descrição.")
            return
        if not valor_total or valor_total <= 0:
            st.error("Digite um valor maior que zero.")
            return

        parcelas_final = qtd_parcelas if pagamento == "Credito" else 1
        valor_parcela  = round(valor_total / parcelas_final, 2)

        salvar_lancamento({
            "data": data_val.strftime("%d/%m/%Y"),
            "descricao": descricao.strip(),
            "pagamento": pagamento,
            "valor_total": valor_total,
            "qtd_parcelas": parcelas_final,
            "valor_parcela": valor_parcela,
        })

        st.session_state.qtd_temp = 1
        if "qtd_parcelas" in st.session_state:
            del st.session_state["qtd_parcelas"]
        st.session_state.tela = "inicio"
        st.rerun()


# ══════════════════════════════════════════
#  TELA: DETALHE MÊS ANTERIOR
# ══════════════════════════════════════════

def tela_detalhe_mes():
    mes = st.session_state.mes_selecionado
    botao_voltar("inicio")
    st.title(mes["label"])
    parcelas = buscar_parcelas_do_mes(mes["ano_mes"])
    bloco_mes(mes["label"], parcelas, f"det_{mes['ano_mes']}", ano_mes=mes["ano_mes"])


# ══════════════════════════════════════════
#  ROTEADOR
# ══════════════════════════════════════════

tela = st.session_state.tela

if tela == "novo":
    tela_novo_lancamento()
elif tela == "detalhe_mes":
    tela_detalhe_mes()
else:
    st.title("💰 Lançamentos")
    aba_lanc, aba_resumo = st.tabs(["📋 Lançamentos", "📊 Resumo Anual"])
    with aba_lanc:
        tela_lancamentos()
    with aba_resumo:
        tela_resumo_anual()

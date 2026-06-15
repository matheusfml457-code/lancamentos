# ─────────────────────────────────────────
#  Sistema de Lançamentos
#  Interface: Streamlit
#  Banco:     SQLite (lancamentos.db)
# ─────────────────────────────────────────

import sqlite3
import streamlit as st
import pandas as pd
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
        background-color: #0F1117 !important;
        color: #E8EAF0 !important;
    }
    .stApp p, .stApp span, .stApp label,
    .stApp h1, .stApp h2, .stApp h3,
    .stApp div { color: #E8EAF0 !important; }

    /* Cabeçalho do mês */
    .mes-header {
        background: #3D5AFE;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        font-size: 15px;
        font-weight: 600;
        color: white !important;
        margin-bottom: 0;
    }

    /* Tabela de lançamentos */
    .tabela-wrapper {
        background: #181B26;
        border: 1px solid #262B3D;
        border-top: none;
        border-radius: 0 0 8px 8px;
        overflow: hidden;
        margin-bottom: 4px;
    }
    .tabela-header {
        display: grid;
        grid-template-columns: 60px 1fr 85px 60px;
        padding: 6px 14px;
        background: #12151F;
        border-bottom: 1px solid #262B3D;
        font-size: 10px;
        font-weight: 600;
        color: #5C6378 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tabela-linha {
        display: grid;
        grid-template-columns: 60px 1fr 85px 60px;
        padding: 7px 14px;
        border-bottom: 1px solid #181B26;
        align-items: center;
        font-size: 13px;
    }
    .tabela-linha:last-child { border-bottom: none; }
    .tabela-linha:hover { background: #1E222F; }

    /* Tabela resumo */
    .resumo-wrapper {
        background: #12151F;
        border: 1px solid #2B3450;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 10px;
        margin-bottom: 22px;
    }
    .resumo-header {
        background: #161B2E;
        padding: 7px 16px;
        font-size: 10px;
        font-weight: 600;
        color: #5C7CFA !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .resumo-linha {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 16px;
        border-bottom: 1px solid #1A2030;
        font-size: 13px;
    }
    .resumo-linha:last-child { border-bottom: none; }
    .resumo-linha.destaque {
        background: #161B2E;
        font-weight: 600;
    }

    /* Badges */
    .badge-pix {
        background: #0D3B30; color: #4ADE9C !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 600;
    }
    .badge-credito {
        background: #4A1D14; color: #FF8A7A !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 600;
    }
    .badge-debito {
        background: #321E5C; color: #BDA6F5 !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 600;
    }
    .badge-receber {
        background: #15314F; color: #7FB6F7 !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 600;
    }
    .badge-recebido {
        background: #0E3B22; color: #6EE7A0 !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 600;
    }
    .badge-salario {
        background: #0B3D2E; color: #38E0A0 !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 700;
    }

    /* Secao titulo */
    .secao-titulo {
        font-size: 12px;
        font-weight: 600;
        color: #5C6378 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 22px 0 8px 0;
    }

    /* Próximos meses card */
    .card-proximo {
        background: #181B26;
        border: 1px solid #262B3D;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 6px;
    }

    .stTextInput input, .stNumberInput input {
        background-color: #181B26 !important;
        color: #E8EAF0 !important;
        border: 1px solid #262B3D !important;
    }
    input[type=number]::-webkit-inner-spin-button,
    input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; }
    input[type=number] { -moz-appearance: textfield; }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #3D5AFE !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button:hover { background-color: #2E45D1 !important; }

    .btn-voltar > button {
        width: auto !important;
        background-color: #181B26 !important;
        color: #8A92AB !important;
        border: 1px solid #262B3D !important;
        padding: 4px 14px !important;
        font-size: 13px !important;
    }
    .btn-parcela > button {
        background-color: #262B3D !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }
    .btn-parcela > button:hover { background-color: #3D5AFE !important; }

    .block-container { padding-top: 1.5rem; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #181B26;
        border-radius: 8px 8px 0 0;
        padding: 6px 16px;
        color: #8A92AB !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3D5AFE !important;
        color: white !important;
    }
    .stTabs [aria-selected="true"] p { color: white !important; }

    /* KPI cards */
    .kpi-card {
        background: #181B26;
        border: 1px solid #262B3D;
        border-radius: 8px;
        padding: 12px 14px;
        text-align: left;
    }
    .kpi-label {
        font-size: 10px;
        font-weight: 600;
        color: #5C6378 !important;
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
            SELECT p.id, p.numero, p.vencimento, p.valor, p.recebido,
                   l.descricao, l.pagamento, l.qtd_parcelas, l.data_compra
            FROM parcelas p JOIN lancamentos l ON l.id = p.lancamento_id
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

def bloco_mes(label: str, parcelas: list, chave_prefix: str):
    """
    Renderiza o bloco completo de um mês:
    cabeçalho azul + tabela de lançamentos + tabela resumo.
    O check de 'recebido' só aparece em lançamentos 'A receber'.
    """
    resumo = buscar_resumo_mes(parcelas)

    # Cabeçalho
    st.markdown(f'<div class="mes-header">📅 {label}</div>', unsafe_allow_html=True)

    # Cabeçalho das colunas
    st.markdown("""
    <div class="tabela-wrapper">
        <div class="tabela-header">
            <span>Data</span>
            <span>Descrição</span>
            <span>Tipo</span>
            <span style="text-align:right">Valor</span>
        </div>
    """, unsafe_allow_html=True)

    # Linhas HTML (sem interação)
    linhas_html = ""
    for p in parcelas:
        data_fmt  = datetime.strptime(p["data_compra"], "%d/%m/%Y").strftime("%d/%m")
        parcela_txt = f"{p['numero']}/{p['qtd_parcelas']}" if p["qtd_parcelas"] > 1 else "1/1"
        badge     = BADGE_HTML.get(p["pagamento"], p["pagamento"])

        if p["pagamento"] == "A receber":
            if p["recebido"]:
                valor_html = f'<span style="color:#6EE7A0; text-align:right; display:block; font-weight:600">R$ {p["valor"]:.2f}</span>'
                badge = '<span class="badge-recebido">Recebido ✓</span>'
            else:
                valor_html = f'<span style="color:#7FB6F7; text-align:right; display:block; font-weight:600">R$ {p["valor"]:.2f}</span>'
        elif p["pagamento"] == "Salario":
            valor_html = f'<span style="color:#38E0A0; text-align:right; display:block; font-weight:700">+ R$ {p["valor"]:.2f}</span>'
        else:
            valor_html = f'<span style="color:#FF8A7A; text-align:right; display:block; font-weight:600">R$ {p["valor"]:.2f}</span>'

        desc_html = f'{p["descricao"]} <span style="color:#5C6378; font-size:11px">· {parcela_txt}</span>'

        linhas_html += f"""
        <div class="tabela-linha">
            <span style="color:#5C6378">{data_fmt}</span>
            <span>{desc_html}</span>
            <span>{badge}</span>
            {valor_html}
        </div>
        """

    st.markdown(linhas_html + "</div>", unsafe_allow_html=True)

    # Checkboxes para "A receber" — fora do HTML para ter interação
    receber_list = [p for p in parcelas if p["pagamento"] == "A receber"]
    if receber_list:
        st.markdown('<div style="margin-top:6px; padding:0 4px">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

    # Tabela resumo
    pendente = resumo["a_receber"] - resumo["recebido"]
    saldo_cor = "#38E0A0" if resumo["saldo"] >= 0 else "#FF8A7A"
    st.markdown(f"""
    <div class="resumo-wrapper">
        <div class="resumo-header">Resumo do mês</div>
        <div class="resumo-linha">
            <span><span class="badge-salario">Salário</span></span>
            <span style="font-weight:600; color:#38E0A0">+ R$ {resumo['salario']:.2f}</span>
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
            <span style="color:#5C6378; font-size:11px; margin-left:6px">
                (recebido R$ {resumo['recebido']:.2f} · pendente R$ {pendente:.2f})
            </span></span>
            <span style="color:#7FB6F7; font-weight:600">R$ {resumo['a_receber']:.2f}</span>
        </div>
        <div class="resumo-linha destaque">
            <span style="color:#8A92AB">Total saídas</span>
            <span style="color:#FF8A7A">R$ {resumo['saidas']:.2f}</span>
        </div>
        <div class="resumo-linha destaque">
            <span style="color:#8A92AB">Total entradas</span>
            <span style="color:#38E0A0">R$ {resumo['entradas']:.2f}</span>
        </div>
        <div class="resumo-linha destaque">
            <span style="color:#E8EAF0; font-weight:700">Saldo do mês</span>
            <span style="color:{saldo_cor}; font-weight:700">R$ {resumo['saldo']:.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        st.session_state.tela = "novo"
        st.rerun()

    st.divider()

    todos_meses = buscar_meses_com_parcelas()
    anteriores  = [m for m in todos_meses if m["ano_mes"] < MES_ATUAL]
    proximos    = [m for m in todos_meses if m["ano_mes"] > MES_ATUAL]
    atual_list  = [m for m in todos_meses if m["ano_mes"] == MES_ATUAL]

    # ── MÊS ATUAL ──
    st.markdown('<div class="secao-titulo">Mês atual</div>', unsafe_allow_html=True)
    if atual_list:
        parcelas_atual = buscar_parcelas_do_mes(MES_ATUAL)
        bloco_mes(LABEL_ATUAL, parcelas_atual, "atual")
    else:
        st.info("Nenhum lançamento este mês ainda.")

    # ── PRÓXIMOS MESES ──
    if proximos:
        st.markdown('<div class="secao-titulo">Próximos meses</div>', unsafe_allow_html=True)

        st.markdown("""
        <style>
        div[data-testid="stButton"].btn-mes > button {
            background-color: #181B26 !important;
            color: #E8EAF0 !important;
            border: 1px solid #262B3D !important;
            border-radius: 8px !important;
            text-align: left !important;
            padding: 12px 16px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            margin-bottom: 4px;
        }
        div[data-testid="stButton"].btn-mes > button:hover {
            border-color: #3D5AFE !important;
            background-color: #1E222F !important;
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
                bloco_mes(m["label"], parcelas_mes, f"prox_{m['ano_mes']}")

    # ── MESES ANTERIORES ──
    if anteriores:
        st.markdown('<div class="secao-titulo">Meses anteriores</div>', unsafe_allow_html=True)
        for m in reversed(anteriores):
            st.markdown(f"""
            <div class="card-proximo">
                <div style="display:flex; justify-content:space-between; align-items:center">
                    <span style="font-weight:600">{m['label']}</span>
                    <span style="color:#8A92AB; font-weight:700">R$ {m['total_valor']:.2f}</span>
                </div>
                <div style="color:#5C6378; font-size:12px; margin-top:3px">
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
    saldo_cor      = "#38E0A0" if total_saldo >= 0 else "#FF8A7A"

    # KPIs
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Entradas {ano}</div>
            <div class="kpi-value" style="color:#38E0A0">R$ {total_entradas:,.2f}</div>
        </div>
        """.replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Saídas {ano}</div>
            <div class="kpi-value" style="color:#FF8A7A">R$ {total_saidas:,.2f}</div>
        </div>
        """.replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Saldo {ano}</div>
            <div class="kpi-value" style="color:{saldo_cor}">R$ {total_saldo:,.2f}</div>
        </div>
        """.replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)

    st.markdown('<div class="secao-titulo">Entradas x Saídas por mês</div>', unsafe_allow_html=True)

    chart_df = df.set_index("Mês")[["Entradas", "Saídas"]]
    st.bar_chart(
        chart_df,
        color=["#38E0A0", "#FF8A7A"],
        use_container_width=True,
        height=280,
    )

    st.markdown('<div class="secao-titulo">Saldo mensal</div>', unsafe_allow_html=True)
    saldo_df = df.set_index("Mês")[["Saldo"]]
    st.bar_chart(
        saldo_df,
        color=["#3D5AFE"],
        use_container_width=True,
        height=220,
    )

    # Tabela resumo mensal
    st.markdown('<div class="secao-titulo">Detalhe mensal</div>', unsafe_allow_html=True)
    tabela_html = """
    <div class="tabela-wrapper">
        <div class="tabela-header" style="grid-template-columns: 1fr 1fr 1fr 1fr;">
            <span>Mês</span>
            <span style="text-align:right">Entradas</span>
            <span style="text-align:right">Saídas</span>
            <span style="text-align:right">Saldo</span>
        </div>
    """
    for _, row in df.iterrows():
        cor_saldo = "#38E0A0" if row["Saldo"] >= 0 else "#FF8A7A"
        tabela_html += f"""
        <div class="tabela-linha" style="grid-template-columns: 1fr 1fr 1fr 1fr;">
            <span>{row['Mês']}</span>
            <span style="text-align:right; color:#38E0A0">R$ {row['Entradas']:.2f}</span>
            <span style="text-align:right; color:#FF8A7A">R$ {row['Saídas']:.2f}</span>
            <span style="text-align:right; color:{cor_saldo}; font-weight:600">R$ {row['Saldo']:.2f}</span>
        </div>
        """
    tabela_html += "</div>"
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
        st.markdown("**Parcelas**")
        col_menos, col_num, col_mais = st.columns([1, 2, 1])
        with col_menos:
            st.markdown('<div class="btn-parcela">', unsafe_allow_html=True)
            if st.button("−", key="btn_menos", use_container_width=True):
                if st.session_state.qtd_temp > 1:
                    st.session_state.qtd_temp -= 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_num:
            novo_val = st.number_input(
                "qtd", min_value=1, max_value=48,
                value=st.session_state.qtd_temp, step=1,
                label_visibility="collapsed",
            )
            if int(novo_val) != st.session_state.qtd_temp:
                st.session_state.qtd_temp = int(novo_val)
        with col_mais:
            st.markdown('<div class="btn-parcela">', unsafe_allow_html=True)
            if st.button("＋", key="btn_mais", use_container_width=True):
                if st.session_state.qtd_temp < 48:
                    st.session_state.qtd_temp += 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        qtd_parcelas = st.session_state.qtd_temp
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
    bloco_mes(mes["label"], parcelas, f"det_{mes['ano_mes']}")


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

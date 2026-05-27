# ─────────────────────────────────────────
#  Sistema de Lançamentos
#  Interface: Streamlit
#  Banco:     SQLite (lancamentos.db)
# ─────────────────────────────────────────

import sqlite3
import streamlit as st
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
        color: #F0F2F6 !important;
    }
    .stApp p, .stApp span, .stApp label,
    .stApp h1, .stApp h2, .stApp h3,
    .stApp div { color: #F0F2F6 !important; }

    .card-lancamento {
        background: #1E2130;
        border: 1px solid #2E3250;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 8px;
    }
    .card-mes {
        background: #1E2130;
        border: 1px solid #2E3250;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
    }
    .card-mes:hover { border-color: #4F6EF7; }
    .total-box {
        background: #4F6EF7;
        color: white !important;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        font-size: 18px;
        font-weight: bold;
    }
    .tabela-geral {
        background: #12182B;
        border: 1px solid #4F6EF7;
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 16px;
        margin-bottom: 8px;
    }
    .tabela-titulo {
        font-size: 13px;
        font-weight: 700;
        color: #4F6EF7 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .secao-titulo {
        font-size: 16px;
        font-weight: 700;
        color: #A0AEC0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 20px 0 8px 0;
    }
    /* Pix: verde */
    .badge-pix {
        background: #064E3B; color: #34D399 !important;
        border-radius: 6px; padding: 2px 8px;
        font-size: 11px; font-weight: 700;
    }
    /* Crédito: vermelho (invertido com débito) */
    .badge-credito {
        background: #7C2D12; color: #FCA5A5 !important;
        border-radius: 6px; padding: 2px 8px;
        font-size: 11px; font-weight: 700;
    }
    /* Débito: roxo (invertido com crédito) */
    .badge-debito {
        background: #4C1D95; color: #C4B5FD !important;
        border-radius: 6px; padding: 2px 8px;
        font-size: 11px; font-weight: 700;
    }
    .badge-receber {
        background: #1E3A5F; color: #93C5FD !important;
        border-radius: 6px; padding: 2px 8px;
        font-size: 11px; font-weight: 700;
    }
    .stTextInput input, .stNumberInput input {
        background-color: #1E2130 !important;
        color: #F0F2F6 !important;
        border: 1px solid #2E3250 !important;
    }
    /* Remove setas do number input */
    input[type=number]::-webkit-inner-spin-button,
    input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; }
    input[type=number] { -moz-appearance: textfield; }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #4F6EF7 !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button:hover { background-color: #3A57D4 !important; }

    /* Botão Voltar menor e discreto */
    .btn-voltar > button {
        width: auto !important;
        background-color: #1E2130 !important;
        color: #A0AEC0 !important;
        border: 1px solid #2E3250 !important;
        padding: 4px 14px !important;
        font-size: 13px !important;
    }
    .btn-voltar > button:hover {
        background-color: #2E3250 !important;
    }

    /* Botões + e - das parcelas */
    .btn-parcela > button {
        background-color: #2E3250 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        padding: 2px 0 !important;
    }
    .btn-parcela > button:hover {
        background-color: #4F6EF7 !important;
    }

    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

DB_PATH = "lancamentos.db"

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

BADGE = {
    "Pix":       '<span class="badge-pix">Pix</span>',
    "Credito":   '<span class="badge-credito">Crédito</span>',
    "Debito":    '<span class="badge-debito">Débito</span>',
    "A receber": '<span class="badge-receber">A receber</span>',
}


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
                FOREIGN KEY (lancamento_id) REFERENCES lancamentos(id)
            )
        """)

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
        for i in range(dados["qtd_parcelas"]):
            venc = data_compra + relativedelta(months=i)
            conn.execute("""
                INSERT INTO parcelas (lancamento_id, numero, vencimento, valor)
                VALUES (?, ?, ?, ?)
            """, (lid, i + 1, venc.strftime("%Y-%m-%d"), dados["valor_parcela"]))
    return lid

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
            SELECT p.numero, p.vencimento, p.valor,
                   l.descricao, l.pagamento, l.qtd_parcelas, l.data_compra
            FROM parcelas p JOIN lancamentos l ON l.id = p.lancamento_id
            WHERE strftime('%Y-%m', p.vencimento) = ?
            ORDER BY l.data_compra ASC, l.id ASC
        """, (ano_mes,)).fetchall()
    return [dict(r) for r in rows]

def buscar_resumo_mes(ano_mes: str) -> dict:
    parcelas  = buscar_parcelas_do_mes(ano_mes)
    pix       = sum(p["valor"] for p in parcelas if p["pagamento"] == "Pix")
    credito   = sum(p["valor"] for p in parcelas if p["pagamento"] == "Credito")
    debito    = sum(p["valor"] for p in parcelas if p["pagamento"] == "Debito")
    a_receber = sum(p["valor"] for p in parcelas if p["pagamento"] == "A receber")
    bruto     = pix + credito + debito
    liquido   = bruto - a_receber
    return {
        "pix": pix, "credito": credito, "debito": debito,
        "a_receber": a_receber, "bruto": bruto, "liquido": liquido,
        "total_parcelas": len(parcelas),
    }


# ══════════════════════════════════════════
#  ESTADO DA NAVEGAÇÃO
# ══════════════════════════════════════════

if "tela" not in st.session_state:
    st.session_state.tela = "inicio"
if "mes_selecionado" not in st.session_state:
    st.session_state.mes_selecionado = None
if "qtd_temp" not in st.session_state:
    st.session_state.qtd_temp = 1

criar_tabelas()

MES_ATUAL     = date.today().strftime("%Y-%m")
MES_ATUAL_NUM = date.today().month
ANO_ATUAL     = date.today().year
LABEL_ATUAL   = f"{MESES_PT[MES_ATUAL_NUM]}/{ANO_ATUAL}"


# ══════════════════════════════════════════
#  COMPONENTES REUTILIZAVEIS
# ══════════════════════════════════════════

def card_lancamento(p: dict):
    parcela_txt = f"{p['numero']}/{p['qtd_parcelas']}" if p["qtd_parcelas"] > 1 else "à vista"
    venc        = datetime.strptime(p["vencimento"], "%Y-%m-%d").strftime("%d/%m/%Y")
    badge       = BADGE.get(p["pagamento"], p["pagamento"])
    cor_valor   = "#93C5FD" if p["pagamento"] == "A receber" else "#22C55E"

    st.markdown(f"""
    <div class="card-lancamento">
        <div style="display:flex; justify-content:space-between; align-items:center">
            <span style="font-weight:600; font-size:14px">{p['descricao']}</span>
            <span style="color:{cor_valor}; font-weight:700; font-size:14px">R$ {p['valor']:.2f}</span>
        </div>
        <div style="margin-top:6px; display:flex; align-items:center; gap:8px; flex-wrap:wrap">
            {badge}
            <span style="color:#6B7280; font-size:12px">Parcela {parcela_txt} · 📅 {venc}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def tabela_geral(resumo: dict):
    st.markdown(f"""
    <div class="tabela-geral">
        <div class="tabela-titulo">Tabela Geral</div>
        <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #1E2D4A">
            <span><span class="badge-pix">Pix</span></span>
            <span style="font-weight:600">R$ {resumo['pix']:.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #1E2D4A">
            <span><span class="badge-credito">Crédito</span></span>
            <span style="font-weight:600">R$ {resumo['credito']:.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #1E2D4A">
            <span><span class="badge-debito">Débito</span></span>
            <span style="font-weight:600">R$ {resumo['debito']:.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #1E2D4A">
            <span><span class="badge-receber">A receber</span></span>
            <span style="color:#93C5FD; font-weight:600">R$ {resumo['a_receber']:.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #1E2D4A">
            <span style="color:#A0AEC0; font-size:13px">Total bruto</span>
            <span style="font-weight:700">R$ {resumo['bruto']:.2f}</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:8px 0 2px 0">
            <span style="color:#22C55E; font-weight:700">Total líquido</span>
            <span style="color:#22C55E; font-weight:700">R$ {resumo['liquido']:.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def botao_voltar(destino: str):
    """Botão voltar menor e discreto no topo."""
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    if st.button("← Voltar"):
        st.session_state.tela = destino
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════
#  TELA: INÍCIO
# ══════════════════════════════════════════

def tela_inicio():
    st.title("💰 Lançamentos")

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
        resumo         = buscar_resumo_mes(MES_ATUAL)
        parcelas_atual = buscar_parcelas_do_mes(MES_ATUAL)

        st.markdown(f"""
        <div class="total-box">
            {LABEL_ATUAL}
            <span style="float:right; font-size:14px; opacity:0.9">R$ {resumo['bruto']:.2f}</span>
        </div>
        """, unsafe_allow_html=True)

        for p in parcelas_atual:
            card_lancamento(p)

        tabela_geral(resumo)
    else:
        st.info("Nenhum lançamento este mês ainda.")

    # ── PRÓXIMOS MESES — apenas um aberto por vez ──
    if proximos:
        st.divider()
        st.markdown('<div class="secao-titulo">Próximos meses</div>', unsafe_allow_html=True)

        # Guarda qual próximo mês está aberto
        if "proximo_aberto" not in st.session_state:
            st.session_state.proximo_aberto = None

        for m in proximos:
            aberto = st.session_state.proximo_aberto == m["ano_mes"]
            label_btn = f"▼  {m['label']}  —  R$ {m['total_valor']:.2f}  ({m['total_parcelas']} parcela(s))" if aberto \
                   else f"▶  {m['label']}  —  R$ {m['total_valor']:.2f}  ({m['total_parcelas']} parcela(s))"

            # Card clicável
            st.markdown(f"""
            <div class="card-mes">
                <div style="display:flex; justify-content:space-between; align-items:center">
                    <span style="font-weight:600; font-size:15px">{m['label']}</span>
                    <span style="color:#4F6EF7; font-weight:700">R$ {m['total_valor']:.2f}</span>
                </div>
                <div style="color:#6B7280; font-size:12px; margin-top:4px">
                    {m['total_parcelas']} parcela(s) agendada(s)
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(label_btn, key=f"prox_{m['ano_mes']}", use_container_width=True):
                # Alterna: se já está aberto fecha, senão abre e fecha o anterior
                st.session_state.proximo_aberto = None if aberto else m["ano_mes"]
                st.rerun()

            if aberto:
                parcelas_mes = buscar_parcelas_do_mes(m["ano_mes"])
                resumo_mes   = buscar_resumo_mes(m["ano_mes"])
                for p in parcelas_mes:
                    card_lancamento(p)
                tabela_geral(resumo_mes)

    # ── MESES ANTERIORES ──
    if anteriores:
        st.divider()
        st.markdown('<div class="secao-titulo">Meses anteriores</div>', unsafe_allow_html=True)

        for m in reversed(anteriores):
            st.markdown(f"""
            <div class="card-mes">
                <div style="display:flex; justify-content:space-between; align-items:center">
                    <span style="font-weight:600; font-size:15px">{m['label']}</span>
                    <span style="color:#A0AEC0; font-weight:700">R$ {m['total_valor']:.2f}</span>
                </div>
                <div style="color:#6B7280; font-size:12px; margin-top:4px">
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
        ["Pix", "Credito", "Debito", "A receber"],
        format_func=lambda x: {"Pix": "Pix", "Credito": "Crédito",
                                "Debito": "Débito", "A receber": "A receber"}[x],
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

    # ── Parcelas com botões + e - simples ──
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
                "qtd",
                min_value=1, max_value=48,
                value=st.session_state.qtd_temp,
                step=1,
                label_visibility="collapsed",
            )
            # Atualiza só se o usuário digitou algo diferente
            if novo_val != st.session_state.qtd_temp:
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
        valor_parcela  = valor_total / parcelas_final

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
#  TELA: DETALHE DO MÊS (anteriores)
# ══════════════════════════════════════════

def tela_detalhe_mes():
    mes = st.session_state.mes_selecionado

    botao_voltar("inicio")
    st.title(mes["label"])

    parcelas = buscar_parcelas_do_mes(mes["ano_mes"])
    resumo   = buscar_resumo_mes(mes["ano_mes"])

    st.markdown(f"""
    <div class="total-box">
        Total do mês: R$ {resumo['bruto']:.2f}
        <span style="float:right; font-size:13px; opacity:0.85">
            {resumo['total_parcelas']} parcela(s)
        </span>
    </div>
    """, unsafe_allow_html=True)

    for p in parcelas:
        card_lancamento(p)

    tabela_geral(resumo)


# ══════════════════════════════════════════
#  ROTEADOR DE TELAS
# ══════════════════════════════════════════

tela = st.session_state.tela

if tela == "inicio":
    tela_inicio()
elif tela == "novo":
    tela_novo_lancamento()
elif tela == "detalhe_mes":
    tela_detalhe_mes()

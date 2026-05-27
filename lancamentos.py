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

    /* Cabeçalho do mês */
    .mes-header {
        background: #4F6EF7;
        border-radius: 10px 10px 0 0;
        padding: 10px 18px;
        font-size: 16px;
        font-weight: 700;
        color: white !important;
        margin-bottom: 0;
    }

    /* Tabela de lançamentos */
    .tabela-wrapper {
        background: #1E2130;
        border: 1px solid #2E3250;
        border-top: none;
        border-radius: 0 0 10px 10px;
        overflow: hidden;
        margin-bottom: 4px;
    }
    .tabela-header {
        display: grid;
        grid-template-columns: 70px 1fr 90px 60px;
        padding: 7px 14px;
        background: #161929;
        border-bottom: 1px solid #2E3250;
        font-size: 11px;
        font-weight: 700;
        color: #6B7280 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tabela-linha {
        display: grid;
        grid-template-columns: 70px 1fr 90px 60px;
        padding: 9px 14px;
        border-bottom: 1px solid #1A1F35;
        align-items: center;
        font-size: 13px;
    }
    .tabela-linha:last-child { border-bottom: none; }
    .tabela-linha:hover { background: #232840; }

    /* Tabela resumo */
    .resumo-wrapper {
        background: #12182B;
        border: 1px solid #4F6EF7;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 12px;
        margin-bottom: 24px;
    }
    .resumo-header {
        background: #1a2540;
        padding: 8px 16px;
        font-size: 11px;
        font-weight: 700;
        color: #4F6EF7 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .resumo-linha {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 16px;
        border-bottom: 1px solid #1E2D4A;
        font-size: 13px;
    }
    .resumo-linha:last-child { border-bottom: none; }
    .resumo-linha.destaque {
        background: #1a2540;
        font-weight: 700;
    }

    /* Badges */
    .badge-pix {
        background: #064E3B; color: #34D399 !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 700;
    }
    .badge-credito {
        background: #7C2D12; color: #FCA5A5 !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 700;
    }
    .badge-debito {
        background: #4C1D95; color: #C4B5FD !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 700;
    }
    .badge-receber {
        background: #1E3A5F; color: #93C5FD !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 700;
    }
    .badge-recebido {
        background: #14532D; color: #86EFAC !important;
        border-radius: 5px; padding: 1px 6px;
        font-size: 11px; font-weight: 700;
    }

    /* Secao titulo */
    .secao-titulo {
        font-size: 13px;
        font-weight: 700;
        color: #6B7280 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 24px 0 8px 0;
    }

    /* Próximos meses card */
    .card-proximo {
        background: #1E2130;
        border: 1px solid #2E3250;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 8px;
        cursor: pointer;
    }

    .stTextInput input, .stNumberInput input {
        background-color: #1E2130 !important;
        color: #F0F2F6 !important;
        border: 1px solid #2E3250 !important;
    }
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

    .btn-voltar > button {
        width: auto !important;
        background-color: #1E2130 !important;
        color: #A0AEC0 !important;
        border: 1px solid #2E3250 !important;
        padding: 4px 14px !important;
        font-size: 13px !important;
    }
    .btn-parcela > button {
        background-color: #2E3250 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
    }
    .btn-parcela > button:hover { background-color: #4F6EF7 !important; }

    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

DB_PATH = "lancamentos.db"

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

BADGE_HTML = {
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
                recebido       INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (lancamento_id) REFERENCES lancamentos(id)
            )
        """)
        # Adiciona coluna recebido se ainda não existir (compatibilidade)
        try:
            conn.execute("ALTER TABLE parcelas ADD COLUMN recebido INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass

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
    bruto     = pix + credito + debito
    liquido   = bruto - recebido
    return {
        "pix": pix, "credito": credito, "debito": debito,
        "a_receber": a_receber, "recebido": recebido,
        "bruto": bruto, "liquido": liquido,
    }


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
                valor_html = f'<span style="color:#86EFAC; text-align:right; display:block; font-weight:700">R$ {p["valor"]:.2f}</span>'
                badge = '<span class="badge-recebido">Recebido ✓</span>'
            else:
                valor_html = f'<span style="color:#93C5FD; text-align:right; display:block; font-weight:700">R$ {p["valor"]:.2f}</span>'
        else:
            valor_html = f'<span style="color:#22C55E; text-align:right; display:block; font-weight:700">R$ {p["valor"]:.2f}</span>'

        desc_html = f'{p["descricao"]} <span style="color:#6B7280; font-size:11px">· {parcela_txt}</span>'

        linhas_html += f"""
        <div class="tabela-linha">
            <span style="color:#6B7280">{data_fmt}</span>
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
    st.markdown(f"""
    <div class="resumo-wrapper">
        <div class="resumo-header">Tabela Geral</div>
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
            <span style="color:#6B7280; font-size:11px; margin-left:6px">
                (recebido R$ {resumo['recebido']:.2f} · pendente R$ {pendente:.2f})
            </span></span>
            <span style="color:#93C5FD; font-weight:600">R$ {resumo['a_receber']:.2f}</span>
        </div>
        <div class="resumo-linha destaque">
            <span style="color:#A0AEC0">Total bruto</span>
            <span>R$ {resumo['bruto']:.2f}</span>
        </div>
        <div class="resumo-linha destaque">
            <span style="color:#22C55E">Total líquido</span>
            <span style="color:#22C55E">R$ {resumo['liquido']:.2f}</span>
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
        parcelas_atual = buscar_parcelas_do_mes(MES_ATUAL)
        bloco_mes(LABEL_ATUAL, parcelas_atual, "atual")
    else:
        st.info("Nenhum lançamento este mês ainda.")

    # ── PRÓXIMOS MESES ──
    if proximos:
        st.markdown('<div class="secao-titulo">Próximos meses</div>', unsafe_allow_html=True)

        # CSS para o botão de mês parecer um card
        st.markdown("""
        <style>
        div[data-testid="stButton"].btn-mes > button {
            background-color: #1E2130 !important;
            color: #F0F2F6 !important;
            border: 1px solid #2E3250 !important;
            border-radius: 10px !important;
            text-align: left !important;
            padding: 14px 18px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            margin-bottom: 4px;
        }
        div[data-testid="stButton"].btn-mes > button:hover {
            border-color: #4F6EF7 !important;
            background-color: #232840 !important;
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
                    <span style="color:#A0AEC0; font-weight:700">R$ {m['total_valor']:.2f}</span>
                </div>
                <div style="color:#6B7280; font-size:12px; margin-top:3px">
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

if tela == "inicio":
    tela_inicio()
elif tela == "novo":
    tela_novo_lancamento()
elif tela == "detalhe_mes":
    tela_detalhe_mes()

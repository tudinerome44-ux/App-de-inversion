import streamlit as st
import pandas as pd
from datetime import datetime


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Tactical Semiconductor Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #9ca3af;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px;
        min-height: 125px;
    }

    .ticker {
        font-size: 1.25rem;
        font-weight: 800;
    }

    .company {
        color: #9ca3af;
        font-size: 0.85rem;
        margin-bottom: 10px;
    }

    .score {
        font-size: 2rem;
        font-weight: 800;
    }

    .buy {
        color: #3fb950;
        font-weight: 800;
    }

    .hold {
        color: #d29922;
        font-weight: 800;
    }

    .sell {
        color: #f85149;
        font-weight: 800;
    }

    .low-risk {
        color: #3fb950;
        font-weight: 700;
    }

    .medium-risk {
        color: #d29922;
        font-weight: 700;
    }

    .high-risk {
        color: #f85149;
        font-weight: 700;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 750;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    .info-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }

    .footer {
        color: #6e7681;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 2rem;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# DATOS BASE
# ============================================================

companies = [
    {
        "ticker": "NVDA",
        "name": "NVIDIA",
        "sector": "AI / GPUs",
        "score": 94,
        "signal": "COMPRAR",
        "risk": "Medio",
        "trend": "Alcista",
        "momentum": 96,
        "fundamental": 94,
        "technical": 93,
        "catalyst": 97,
        "capital": 22,
        "sources": [
            "NVIDIA Investor Relations",
            "Reuters",
            "Yahoo Finance",
            "MarketWatch",
            "CNBC"
        ]
    },
    {
        "ticker": "AVGO",
        "name": "Broadcom",
        "sector": "Semiconductors / AI",
        "score": 91,
        "signal": "COMPRAR",
        "risk": "Medio",
        "trend": "Alcista",
        "momentum": 93,
        "fundamental": 92,
        "technical": 90,
        "catalyst": 94,
        "capital": 18,
        "sources": [
            "Broadcom Investor Relations",
            "Reuters",
            "Yahoo Finance",
            "MarketWatch",
            "CNBC"
        ]
    },
    {
        "ticker": "AMD",
        "name": "Advanced Micro Devices",
        "sector": "AI / CPUs / GPUs",
        "score": 87,
        "signal": "COMPRAR",
        "risk": "Medio",
        "trend": "Alcista",
        "momentum": 90,
        "fundamental": 86,
        "technical": 87,
        "catalyst": 91,
        "capital": 15,
        "sources": [
            "AMD Investor Relations",
            "Reuters",
            "Yahoo Finance",
            "MarketWatch",
            "CNBC"
        ]
    },
    {
        "ticker": "ASML",
        "name": "ASML Holding",
        "sector": "Semiconductor Equipment",
        "score": 86,
        "signal": "COMPRAR",
        "risk": "Medio",
        "trend": "Alcista",
        "momentum": 84,
        "fundamental": 94,
        "technical": 82,
        "catalyst": 89,
        "capital": 12,
        "sources": [
            "ASML Investor Relations",
            "Reuters",
            "Yahoo Finance",
            "MarketWatch",
            "CNBC"
        ]
    },
    {
        "ticker": "LRCX",
        "name": "Lam Research",
        "sector": "Semiconductor Equipment",
        "score": 82,
        "signal": "COMPRAR",
        "risk": "Medio",
        "trend": "Alcista",
        "momentum": 85,
        "fundamental": 83,
        "technical": 81,
        "catalyst": 84,
        "capital": 10,
        "sources": [
            "Lam Research Investor Relations",
            "Reuters",
            "Yahoo Finance",
            "MarketWatch",
            "CNBC"
        ]
    },
    {
        "ticker": "AMAT",
        "name": "Applied Materials",
        "sector": "Semiconductor Equipment",
        "score": 79,
        "signal": "MANTENER",
        "risk": "Medio",
        "trend": "Alcista",
        "momentum": 78,
        "fundamental": 82,
        "technical": 77,
        "catalyst": 80,
        "capital": 8,
        "sources": [
            "Applied Materials Investor Relations",
            "Reuters",
            "Yahoo Finance",
            "MarketWatch",
            "CNBC"
        ]
    },
    {
        "ticker": "KLAC",
        "name": "KLA Corporation",
        "sector": "Semiconductor Equipment",
        "score": 77,
        "signal": "MANTENER",
        "risk": "Medio",
        "trend": "Neutral",
        "momentum": 75,
        "fundamental": 84,
        "technical": 73,
        "catalyst": 76,
        "capital": 7,
        "sources": [
            "KLA Investor Relations",
            "Reuters",
            "Yahoo Finance",
            "MarketWatch",
            "CNBC"
        ]
    },
    {
        "ticker": "CSCO",
        "name": "Cisco Systems",
        "sector": "Networking",
        "score": 68,
        "signal": "MANTENER",
        "risk": "Bajo",
        "trend": "Neutral",
        "momentum": 65,
        "fundamental": 77,
        "technical": 64,
        "catalyst": 66,
        "capital": 5,
        "sources": [
            "Cisco Investor Relations",
            "Reuters",
            "Yahoo Finance",
            "MarketWatch",
            "CNBC"
        ]
    },
    {
        "ticker": "INTC",
        "name": "Intel",
        "sector": "CPUs / Foundry",
        "score": 48,
        "signal": "VENDER",
        "risk": "Alto",
        "trend": "Bajista",
        "momentum": 42,
        "fundamental": 50,
        "technical": 45,
        "catalyst": 55,
        "capital": 3,
        "sources": [
            "Intel Investor Relations",
            "Reuters",
            "Yahoo Finance",
            "MarketWatch",
            "CNBC"
        ]
    }
]

df = pd.DataFrame(companies)


# ============================================================
# FUNCIONES
# ============================================================

def signal_class(signal):
    if signal == "COMPRAR":
        return "buy"
    elif signal == "VENDER":
        return "sell"
    return "hold"


def risk_class(risk):
    if risk == "Bajo":
        return "low-risk"
    elif risk == "Alto":
        return "high-risk"
    return "medium-risk"


def score_label(score):
    if score >= 85:
        return "Muy fuerte"
    elif score >= 75:
        return "Fuerte"
    elif score >= 60:
        return "Moderado"
    else:
        return "Débil"


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    '<div class="title">📈 Tactical Semiconductor Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Sistema táctico de análisis y rotación de capital · V2'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🎛️ Filtros")

selected_companies = st.sidebar.multiselect(
    "Empresa",
    options=list(df["ticker"]),
    default=list(df["ticker"])
)

selected_signals = st.sidebar.multiselect(
    "Señal",
    options=["COMPRAR", "MANTENER", "VENDER"],
    default=["COMPRAR", "MANTENER", "VENDER"]
)

selected_risks = st.sidebar.multiselect(
    "Riesgo",
    options=["Bajo", "Medio", "Alto"],
    default=["Bajo", "Medio", "Alto"]
)

min_score = st.sidebar.slider(
    "Score mínimo",
    min_value=0,
    max_value=100,
    value=0
)

filtered_df = df[
    (df["ticker"].isin(selected_companies))
    & (df["signal"].isin(selected_signals))
    & (df["risk"].isin(selected_risks))
    & (df["score"] >= min_score)
].copy()


# ============================================================
# KPIs
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Empresas analizadas",
        len(filtered_df)
    )

with col2:
    buy_count = len(filtered_df[filtered_df["signal"] == "COMPRAR"])
    st.metric(
        "🟢 Comprar",
        buy_count
    )

with col3:
    hold_count = len(filtered_df[filtered_df["signal"] == "MANTENER"])
    st.metric(
        "🟡 Mantener",
        hold_count
    )

with col4:
    sell_count = len(filtered_df[filtered_df["signal"] == "VENDER"])
    st.metric(
        "🔴 Vender",
        sell_count
    )


# ============================================================
# RANKING
# ============================================================

st.markdown(
    '<div class="section-title">🏆 Ranking táctico</div>',
    unsafe_allow_html=True
)

ranking_df = filtered_df.sort_values(
    by="score",
    ascending=False
).reset_index(drop=True)

ranking_df.index = ranking_df.index + 1

display_df = ranking_df[
    [
        "ticker",
        "name",
        "sector",
        "score",
        "signal",
        "risk",
        "trend",
        "capital"
    ]
].copy()

display_df.columns = [
    "Ticker",
    "Empresa",
    "Sector",
    "Score",
    "Señal",
    "Riesgo",
    "Tendencia",
    "Capital %"
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=False
)


# ============================================================
# TARJETAS
# ============================================================

st.markdown(
    '<div class="section-title">📊 Análisis por empresa</div>',
    unsafe_allow_html=True
)

if filtered_df.empty:

    st.warning("No existen empresas con los filtros seleccionados.")

else:

    for start in range(0, len(filtered_df), 3):

        row = filtered_df.iloc[start:start + 3]

        cols = st.columns(3)

        for col, (_, company) in zip(cols, row.iterrows()):

            signal_css = signal_class(company["signal"])
            risk_css = risk_class(company["risk"])

            with col:

                st.markdown(
                    f"""
                    <div class="metric-card">

                        <div class="ticker">
                            {company["ticker"]}
                        </div>

                        <div class="company">
                            {company["name"]} · {company["sector"]}
                        </div>

                        <div class="score">
                            {company["score"]}/100
                        </div>

                        <div class="{signal_css}">
                            {company["signal"]}
                        </div>

                        <div class="{risk_css}">
                            Riesgo: {company["risk"]}
                        </div>

                        <div>
                            Tendencia: <b>{company["trend"]}</b>
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.progress(
                    company["score"] / 100
                )

                with st.expander("Ver análisis"):

                    c1, c2 = st.columns(2)

                    with c1:
                        st.write(
                            f"**Momentum:** {company['momentum']}/100"
                        )
                        st.write(
                            f"**Fundamental:** {company['fundamental']}/100"
                        )

                    with c2:
                        st.write(
                            f"**Técnico:** {company['technical']}/100"
                        )
                        st.write(
                            f"**Catalizador:** {company['catalyst']}/100"
                        )

                    st.write(
                        f"**Evaluación:** {score_label(company['score'])}"
                    )

                    st.write("**Fuentes consideradas:**")

                    for source in company["sources"]:
                        st.write(f"• {source}")


# ============================================================
# ROTACIÓN DE CAPITAL
# ============================================================

st.markdown(
    '<div class="section-title">🔄 Estrategia de rotación de capital</div>',
    unsafe_allow_html=True
)

rotation_df = filtered_df[
    ["ticker", "score", "signal", "risk", "capital"]
].sort_values(
    by="score",
    ascending=False
).copy()

rotation_df.columns = [
    "Ticker",
    "Score",
    "Señal",
    "Riesgo",
    "Asignación sugerida %"
]

st.dataframe(
    rotation_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "La rotación prioriza empresas con mayor Score táctico y "
    "señal COMPRAR, reduciendo exposición a empresas con señal "
    "VENDER o riesgo elevado."
)


# ============================================================
# REGLAS DE ROTACIÓN
# ============================================================

st.markdown(
    '<div class="section-title">📐 Reglas tácticas</div>',
    unsafe_allow_html=True
)

rules_col1, rules_col2, rules_col3 = st.columns(3)

with rules_col1:

    st.markdown(
        """
        <div class="info-box">

        🟢 <b>COMPRAR</b>

        <br><br>

        Score ≥ 85

        <br>

        Prioridad alta

        <br>

        Entrada de capital

        </div>
        """,
        unsafe_allow_html=True
    )

with rules_col2:

    st.markdown(
        """
        <div class="info-box">

        🟡 <b>MANTENER</b>

        <br><br>

        Score 60–84

        <br>

        Mantener exposición

        <br>

        Vigilar evolución

        </div>
        """,
        unsafe_allow_html=True
    )

with rules_col3:

    st.markdown(
        """
        <div class="info-box">

        🔴 <b>VENDER</b>

        <br><br>

        Score < 60

        <br>

        Reducir exposición

        <br>

        Rotar capital

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FUENTES
# ============================================================

st.markdown(
    '<div class="section-title">📰 Fuentes del sistema</div>',
    unsafe_allow_html=True
)

st.write(
    """
    Actualmente las fuentes son una estructura de referencia.
    En la siguiente etapa se pueden conectar noticias y datos
    actuales para recalcular automáticamente el Score táctico.
    """
)

source_table = pd.DataFrame({
    "Fuente": [
        "Investor Relations",
        "Reuters",
        "Yahoo Finance",
        "MarketWatch",
        "CNBC"
    ],
    "Uso futuro": [
        "Resultados y comunicados oficiales",
        "Noticias y eventos corporativos",
        "Precio y datos de mercado",
        "Información financiera",
        "Noticias y catalizadores"
    ]
})

st.dataframe(
    source_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# ESTADO
# ============================================================

st.markdown(
    '<div class="section-title">⚙️ Estado del sistema</div>',
    unsafe_allow_html=True
)

st.success(
    "Sistema V2 cargado correctamente. "
    "Arquitectura preparada para incorporar datos y noticias actuales."
)

st.caption(
    f"Última actualización de la interfaz: "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Tactical Semiconductor Dashboard · V2 ·
        Prototipo educativo de análisis táctico
    </div>
    """,
    unsafe_allow_html=True
)
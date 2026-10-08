import streamlit as st
import requests
import xml.etree.ElementTree as ET

from urllib.parse import quote
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(
    page_title="Trading Tactical",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# EMPRESAS
# ============================================================
DATA = [
    {
        "name": "Advanced Micro Devices",
        "ticker": "AMD",
        "sector": "Semiconductores / IA",
        "base_score": 78,
        "risk": "Medio",
        "strategy": "Vigilar impulso de semiconductores y posibles rebotes rápidos."
    },
    {
        "name": "NVIDIA",
        "ticker": "NVDA",
        "sector": "IA / GPUs",
        "base_score": 84,
        "risk": "Medio",
        "strategy": "Prioridad táctica por exposición a IA; buscar entradas tras retrocesos."
    },
    {
        "name": "Cisco",
        "ticker": "CSCO",
        "sector": "Networking",
        "base_score": 65,
        "risk": "Bajo",
        "strategy": "Perfil más defensivo; mantener mientras no aparezca un catalizador claro."
    },
    {
        "name": "Lam Research",
        "ticker": "LRCX",
        "sector": "Equipamiento semiconductor",
        "base_score": 78,
        "risk": "Medio",
        "strategy": "Vigilar ciclo de semiconductores y gasto en fabricación."
    },
    {
        "name": "Intel",
        "ticker": "INTC",
        "sector": "CPUs / Foundry",
        "base_score": 52,
        "risk": "Alto",
        "strategy": "Mayor incertidumbre relativa; esperar un catalizador fuerte."
    },
    {
        "name": "Broadcom",
        "ticker": "AVGO",
        "sector": "Semiconductores / IA",
        "base_score": 82,
        "risk": "Medio",
        "strategy": "Interés táctico por IA, semiconductores y networking."
    },
    {
        "name": "Applied Materials",
        "ticker": "AMAT",
        "sector": "Equipamiento semiconductor",
        "base_score": 75,
        "risk": "Medio",
        "strategy": "Exposición al ciclo de equipamiento semiconductor."
    },
    {
        "name": "ASML Holding",
        "ticker": "ASML",
        "sector": "Equipamiento semiconductor",
        "base_score": 81,
        "risk": "Medio",
        "strategy": "Activo estratégico del ecosistema de semiconductores."
    },
    {
        "name": "KLA",
        "ticker": "KLAC",
        "sector": "Control de procesos",
        "base_score": 74,
        "risk": "Medio",
        "strategy": "Exposición a control de procesos y fabricación de chips."
    }
]


# ============================================================
# ESTILOS
# ============================================================
st.markdown(
    """
    <style>

    .main {
        background-color: #0e1117;
    }

    .signal-buy {
        color: #3fb950;
        font-size: 22px;
        font-weight: 800;
    }

    .signal-hold {
        color: #d29922;
        font-size: 22px;
        font-weight: 800;
    }

    .signal-sell {
        color: #f85149;
        font-size: 22px;
        font-weight: 800;
    }

    .score {
        font-size: 32px;
        font-weight: 800;
    }

    .news-source {
        color: #8b949e;
        font-size: 12px;
    }

    .small-text {
        color: #8b949e;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# OBTENER NOTICIAS
# ============================================================
def get_news(ticker):

    query = quote(
        f'"{ticker}" stock OR "{ticker}" company'
    )

    url = (
        "https://news.google.com/rss/search?"
        f"q={query}&"
        "hl=en-US&"
        "gl=US&"
        "ceid=US:en"
    )

    try:

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(response.content)

        articles = []

        for item in root.findall("./channel/item"):

            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")

            source_element = item.find("source")

            if source_element is not None:
                source = source_element.text or "Google News"
            else:
                source = "Google News"

            date = None

            if pub_date:

                try:
                    date = parsedate_to_datetime(pub_date)

                except Exception:
                    date = None

            articles.append(
                {
                    "title": title,
                    "link": link,
                    "source": source,
                    "date": date
                }
            )

        return articles[:5]

    except Exception as error:

        return [
            {
                "title": "No se pudieron obtener las noticias.",
                "link": "",
                "source": str(error),
                "date": None
            }
        ]


# ============================================================
# ANÁLISIS SIMPLE DE SENTIMIENTO
# ============================================================
POSITIVE_WORDS = [
    "growth",
    "grows",
    "increase",
    "increases",
    "increased",
    "profit",
    "profits",
    "revenue",
    "revenues",
    "record",
    "strong",
    "surge",
    "surges",
    "rises",
    "rise",
    "gain",
    "gains",
    "upgrade",
    "bullish",
    "demand",
    "deal",
    "contract",
    "partnership",
    "ai",
    "artificial intelligence",
    "expansion",
    "beat",
    "beats",
    "outperform"
]

NEGATIVE_WORDS = [
    "fall",
    "falls",
    "fell",
    "drop",
    "drops",
    "decline",
    "declines",
    "loss",
    "losses",
    "weak",
    "warning",
    "downgrade",
    "bearish",
    "lawsuit",
    "investigation",
    "restriction",
    "restrictions",
    "ban",
    "bans",
    "delay",
    "delays",
    "cut",
    "cuts",
    "miss",
    "misses",
    "risk",
    "risks",
    "layoffs",
    "layoff",
    "problem",
    "problems"
]


def analyze_news(news):

    positive = 0
    negative = 0

    for article in news:

        title = article["title"].lower()

        for word in POSITIVE_WORDS:

            if word in title:
                positive += 1

        for word in NEGATIVE_WORDS:

            if word in title:
                negative += 1

    total = positive + negative

    if total == 0:

        sentiment_score = 50

    else:

        sentiment_score = (
            50
            + ((positive - negative) / total) * 50
        )

    sentiment_score = max(
        0,
        min(100, sentiment_score)
    )

    return {
        "positive": positive,
        "negative": negative,
        "sentiment": round(sentiment_score)
    }


# ============================================================
# RECENCIA
# ============================================================

def recency_score(news):

    if not news:
        return 50

    now = datetime.now(timezone.utc)

    scores = []

    for article in news:

        date = article.get("date")

        if date is None:
            continue

        if date.tzinfo is None:
            date = date.replace(
                tzinfo=timezone.utc
            )

        hours = (
            now - date
        ).total_seconds() / 3600

        if hours <= 6:
            score = 100

        elif hours <= 24:
            score = 90

        elif hours <= 48:
            score = 80

        elif hours <= 72:
            score = 70

        elif hours <= 120:
            score = 60

        else:
            score = 50

        scores.append(score)

    if not scores:
        return 50

    return round(sum(scores) / len(scores))


# ============================================================
# SCORE TÁCTICO
# ============================================================

def calculate_score(company, news):

    analysis = analyze_news(news)

    sentiment = analysis["sentiment"]

    recent = recency_score(news)

    base = company["base_score"]

    # Riesgo
    risk_adjustment = {
        "Bajo": 5,
        "Medio": 0,
        "Alto": -7
    }

    risk_score = risk_adjustment[
        company["risk"]
    ]

    # Score final
    score = (
        base * 0.40
        + sentiment * 0.35
        + recent * 0.15
        + 50 * 0.10
        + risk_score
    )

    score = max(
        0,
        min(100, round(score))
    )

    return score, analysis, recent


# ============================================================
# PROBABILIDADES
# ============================================================

def calculate_probabilities(score):

    """
    Estas probabilidades son una representación heurística
    de la fuerza de la señal.

    NO representan una probabilidad estadística calibrada
    de que el precio suba o baje.
    """

    if score >= 80:

        buy = 55 + (score - 80) * 1.2
        sell = max(5, 15 - (score - 80) * 0.5)

    elif score >= 60:

        buy = 40 + (score - 60) * 0.75
        sell = 20 - (score - 60) * 0.35

    else:

        buy = 25 + score * 0.25
        sell = 55 - score * 0.35

    buy = max(5, min(90, buy))
    sell = max(5, min(80, sell))

    hold = 100 - buy - sell

    hold = max(5, hold)

    total = buy + hold + sell

    buy = round(buy / total * 100)
    hold = round(hold / total * 100)
    sell = 100 - buy - hold

    return {
        "COMPRAR": buy,
        "MANTENER": hold,
        "VENDER": sell
    }


# ============================================================
# SEÑAL
# ============================================================
def get_signal(score):

    if score >= 80:
        return "COMPRAR"

    if score >= 60:
        return "MANTENER"

    return "VENDER"


# ============================================================
# SESIÓN
# ============================================================

if "news_data" not in st.session_state:
    st.session_state.news_data = {}

if "last_update" not in st.session_state:
    st.session_state.last_update = None


# ============================================================
# ACTUALIZAR TODO
# ============================================================

def update_all_news():

    st.session_state.news_data = {}

    progress = st.progress(0)

    total = len(DATA)

    for i, company in enumerate(DATA):

        ticker = company["ticker"]

        st.session_state.news_data[
            ticker
        ] = get_news(ticker)

        progress.progress(
            (i + 1) / total
        )

    st.session_state.last_update = datetime.now()


# ============================================================
# CABECERA
# ============================================================

st.title("📈 Trading Tactical")

st.caption(
    "Noticias actuales + Score táctico + "
    "señal estimada para 9 empresas"
)


# ============================================================
# FILTROS
# ============================================================

c1, c2, c3 = st.columns(
    [2, 1, 1]
)

with c1:

    search = st.text_input(
        "🔎 Buscar empresa o ticker",
        placeholder="Ej.: NVIDIA o NVDA"
    )

with c2:

    signal_filter = st.selectbox(
        "Señal",
        [
            "Todas",
            "COMPRAR",
            "MANTENER",
            "VENDER"
        ]
    )

with c3:

    st.write("")

    if st.button(
        "🔄 Actualizar noticias",
        use_container_width=True
    ):

        update_all_news()

        st.success(
            "Noticias y análisis actualizados."
        )


# ============================================================
# FILTRAR EMPRESAS
# ============================================================

items = DATA

if search.strip():

    q = search.lower().strip()

    items = [
        company
        for company in items
        if q in company["name"].lower()
        or q in company["ticker"].lower()
    ]


# ============================================================
# MOSTRAR EMPRESAS
# ============================================================

visible_items = []

for company in items:

    ticker = company["ticker"]

    news = st.session_state.news_data.get(
        ticker
    )

    if news is None:

        score = company["base_score"]

        signal = get_signal(score)

    else:

        score, analysis, recent = calculate_score(
            company,
            news
        )

        signal = get_signal(score)

    if (
        signal_filter == "Todas"
        or signal == signal_filter
    ):

        visible_items.append(
            company
        )


st.write(
    f"**Empresas mostradas:** "
    f"{len(visible_items)} / {len(DATA)}"
)


if st.session_state.last_update:

    st.caption(
        "Última actualización: "
        + st.session_state.last_update.strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )


# ============================================================
# TARJETAS
# ============================================================

for company in visible_items:

    name = company["name"]
    ticker = company["ticker"]
    strategy = company["strategy"]
    risk = company["risk"]

    news = st.session_state.news_data.get(
        ticker
    )

    if news is None:

        score = company["base_score"]

        analysis = {
            "positive": 0,
            "negative": 0,
            "sentiment": 50
        }

        recent = 50

        probabilities = {
            "COMPRAR": 0,
            "MANTENER": 100,
            "VENDER": 0
        }

        signal = get_signal(score)

    else:

        score, analysis, recent = calculate_score(
            company,
            news
        )

        probabilities = calculate_probabilities(
            score
        )

        signal = get_signal(score)

    # --------------------------------------------------------
    # EMPRESA
    # --------------------------------------------------------

    with st.container(border=True):

        left, center, right = st.columns(
            [1.1, 2.7, 1.5]
        )

        # ----------------------------------------------------
        # INFORMACIÓN
        # ----------------------------------------------------

        with left:

            st.subheader(ticker)

            st.write(name)

            st.caption(
                company["sector"]
            )

            st.write(
                f"**Riesgo:** {risk}"
            )

            if signal == "COMPRAR":

                st.markdown(
                    '<div class="signal-buy">'
                    '🟢 COMPRAR'
                    '</div>',
                    unsafe_allow_html=True
                )

            elif signal == "VENDER":

                st.markdown(
                    '<div class="signal-sell">'
                    '🔴 VENDER'
                    '</div>',
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    '<div class="signal-hold">'
                    '🟡 MANTENER'
                    '</div>',
                    unsafe_allow_html=True
                )

        # ----------------------------------------------------
        # NOTICIAS
        # ----------------------------------------------------

        with center:

            st.markdown(
                "### 📰 5 noticias actuales"
            )

            if news is None:

                st.info(
                    "Pulsa «Actualizar noticias» "
                    "para cargar las noticias actuales."
                )

            else:

                for i, article in enumerate(
                    news[:5],
                    start=1
                ):

                    title = article["title"]
                    link = article["link"]
                    source = article["source"]
                    date = article["date"]

                    date_text = ""

                    if date:

                        date_text = date.strftime(
                            "%d/%m/%Y %H:%M"
                        )

                    if link:

                        st.markdown(
                            f"**{i}. [{title}]({link})**"
                        )

                    else:

                        st.write(
                            f"**{i}. {title}**"
                        )

                    st.markdown(
                        f"""
                        <span class="news-source">
                        {source}
                        {" · " + date_text if date_text else ""}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

                    if i < len(news[:5]):

                        st.divider()

        # ----------------------------------------------------
        # SCORE
        # ----------------------------------------------------

        with right:

            st.markdown(
                "### 🎯 Score táctico"
            )

            st.markdown(
                f'<div class="score">'
                f'{score}/100'
                f'</div>',
                unsafe_allow_html=True
            )

            st.progress(
                score / 100
            )

            st.write(
                f"**Señal:** {signal}"
            )

            st.write(
                f"**Noticias positivas:** "
                f"{analysis['positive']}"
            )

            st.write(
                f"**Noticias negativas:** "
                f"{analysis['negative']}"
            )

            st.write(
                f"**Sentimiento:** "
                f"{analysis['sentiment']}/100"
            )

            st.write(
                f"**Recencia:** "
                f"{recent}/100"
            )

        # ----------------------------------------------------
        # PROBABILIDADES
        # ----------------------------------------------------

        if news is not None:

            st.divider()

            st.markdown(
                "### 📊 Distribución estimada de la señal"
            )

            p1, p2, p3 = st.columns(3)

            with p1:

                st.metric(
                    "🟢 COMPRAR",
                    f"{probabilities['COMPRAR']}%"
                )

            with p2:

                st.metric(
                    "🟡 MANTENER",
                    f"{probabilities['MANTENER']}%"
                )

            with p3:

                st.metric(
                    "🔴 VENDER",
                    f"{probabilities['VENDER']}%"
                )

            st.caption(
                "Estas probabilidades representan la "
                "confianza heurística del modelo en cada "
                "señal. No son probabilidades estadísticas "
                "calibradas de movimiento del precio."
            )

        # ----------------------------------------------------
        # ESTRATEGIA
        # ----------------------------------------------------

        st.divider()

        st.markdown(
            "### 📌 Estrategia táctica"
        )

        st.write(strategy)


# ============================================================
# METODOLOGÍA
# ============================================================

st.divider()

st.markdown(
    "### 🧠 ¿Cómo se calcula el Score?"
)

st.write(
    """
    El Score táctico combina la valoración base de la empresa,
    el sentimiento detectado en las noticias, la recencia de
    las noticias y un ajuste por riesgo.
    """
)

methodology = {
    "Componente": [
        "Valoración base",
        "Sentimiento de noticias",
        "Recencia de noticias",
        "Componente neutral",
        "Ajuste por riesgo"
    ],
    "Peso aproximado": [
        "40%",
        "35%",
        "15%",
        "10%",
        "Ajuste"
    ]
}

st.dataframe(
    methodology,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# INTERPRETACIÓN
# ============================================================

st.markdown(
    "### 📖 Interpretación"
)

i1, i2, i3 = st.columns(3)

with i1:

    st.success(
        """
        **80–100**

        🟢 COMPRAR

        Señal táctica fuerte.
        """
    )

with i2:

    st.warning(
        """
        **60–79**

        🟡 MANTENER

        Señal intermedia.
        """
    )

with i3:

    st.error(
        """
        **0–59**

        🔴 VENDER

        Señal táctica débil.
        """
    )


# ============================================================
# PIE
# ============================================================

st.divider()

st.caption(
    "Trading Tactical · V3 · Sin JavaScript · "
    "Sin base de datos"
)

st.caption(
    "Las noticias se consultan nuevamente al pulsar "
    "«Actualizar noticias». El modelo no conserva historial."
)

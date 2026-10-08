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
# DATOS BASE DE LAS EMPRESAS
# ============================================================

DATA = [
    {
        "name": "Advanced Micro Devices",
        "ticker": "AMD",
        "sector": "Semiconductors / IA",
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
# OBTENER NOTICIAS ACTUALES
# ============================================================

def get_news(ticker):

    query = quote(f'"{ticker}" stock OR "{ticker}" company')

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

            if source_element is not None and source_element.text:
                source = source_element.text
            else:
                source = "Google News"

            date = None

            if pub_date:
                try:
                    date = parsedate_to_datetime(pub_date)
                except Exception:
                    date = None

            articles.append({
                "title": title,
                "link": link,
                "source": source,
                "date": date
            })

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
# PALABRAS PARA ANALIZAR SENTIMIENTO
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


# ============================================================
# ANÁLISIS DE NOTICIAS
# ============================================================

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
            50 +
            ((positive - negative) / total) * 50
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
# RECENCIA DE LAS NOTICIAS
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

    return round(
        sum(scores) / len(scores)
    )


# ============================================================
# SCORE TÁCTICO
# ============================================================

def calculate_score(company, news):

    analysis = analyze_news(news)

    sentiment = analysis["sentiment"]

    recent = recency_score(news)

    base = company["base_score"]

    risk_adjustment = {
        "Bajo": 5,
        "Medio": 0,
        "Alto": -7
    }

    risk_score = risk_adjustment[
        company["risk"]
    ]

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
# SEÑAL
# ============================================================

def get_signal(score):

    if score >= 80:
        return "COMPRAR"

    if score >= 60:
        return "MANTENER"

    return "VENDER"


# ============================================================
# CONFIANZA DE LA SEÑAL
# ============================================================

def calculate_confidence(score):

    """
    IMPORTANTE:

    Estos porcentajes NO son probabilidades estadísticas.

    Representan la confianza heurística del sistema
    respecto a la señal generada por el Score.

    La señal recomendada siempre tendrá el porcentaje
    más alto.
    """

    # --------------------------------------------------------
    # COMPRAR
    # --------------------------------------------------------

    if score >= 80:

        distance = score - 80

        buy = 55 + (distance * 0.80)

        hold = 30 - (distance * 0.35)

        sell = 15 - (distance * 0.45)

        buy = max(55, min(75, buy))
        hold = max(15, min(30, hold))
        sell = max(5, min(15, sell))

    # --------------------------------------------------------
    # MANTENER
    # --------------------------------------------------------

    elif score >= 60:

        distance = score - 60

        hold = 50 + (distance * 0.25)

        buy = 30 + (distance * 0.15)

        sell = 20 - (distance * 0.40)

        hold = max(50, min(55, hold))
        buy = max(30, min(33, buy))
        sell = max(12, min(20, sell))

    # --------------------------------------------------------
    # VENDER
    # --------------------------------------------------------

    else:

        distance = 59 - score

        sell = 50 + (distance * 0.70)

        hold = 30 - (distance * 0.35)

        buy = 20 - (distance * 0.35)

        sell = max(50, min(75, sell))
        hold = max(15, min(30, hold))
        buy = max(5, min(20, buy))

    # --------------------------------------------------------
    # NORMALIZAR PARA QUE SUME 100
    # --------------------------------------------------------

    total = buy + hold + sell

    buy = round(
        buy / total * 100
    )

    hold = round(
        hold / total * 100
    )

    sell = 100 - buy - hold

    # --------------------------------------------------------
    # CORRECCIÓN DE SEGURIDAD
    # --------------------------------------------------------

    signal = get_signal(score)

    confidence = {
        "COMPRAR": buy,
        "MANTENER": hold,
        "VENDER": sell
    }

    # Nos aseguramos de que la señal principal
    # sea siempre la de mayor confianza.

    if signal == "COMPRAR":

        confidence["COMPRAR"] = max(
            confidence["COMPRAR"],
            confidence["MANTENER"] + 1,
            confidence["VENDER"] + 1
        )

    elif signal == "MANTENER":

        confidence["MANTENER"] = max(
            confidence["MANTENER"],
            confidence["COMPRAR"] + 1,
            confidence["VENDER"] + 1
        )

    else:

        confidence["VENDER"] = max(
            confidence["VENDER"],
            confidence["COMPRAR"] + 1,
            confidence["MANTENER"] + 1
        )

    # Reajustar para que vuelva a sumar 100

    total = sum(confidence.values())

    buy = round(
        confidence["COMPRAR"] / total * 100
    )

    hold = round(
        confidence["MANTENER"] / total * 100
    )

    sell = 100 - buy - hold

    return {
        "COMPRAR": buy,
        "MANTENER": hold,
        "VENDER": sell
    }


# ============================================================
# SESSION STATE
# ============================================================

if "news_data" not in st.session_state:

    st.session_state.news_data = {}


if "last_update" not in st.session_state:

    st.session_state.last_update = None


# ============================================================
# ACTUALIZAR TODAS LAS NOTICIAS
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
# TÍTULO
# ============================================================

st.title("📈 Trading Tactical")

st.caption(
    "Noticias actuales + Score táctico + "
    "señal + confianza heurística"
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
        if (
            q in company["name"].lower()
            or q in company["ticker"].lower()
        )
    ]


# ============================================================
# DETERMINAR EMPRESAS VISIBLES
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

        visible_items.append(company)


st.write(
    f"**Empresas mostradas:** "
    f"{len(visible_items)} / {len(DATA)}"
)


# ============================================================
# FECHA DE ACTUALIZACIÓN
# ============================================================

if st.session_state.last_update:

    st.caption(
        "Última actualización: "
        + st.session_state.last_update.strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )


# ============================================================
# MOSTRAR EMPRESAS
# ============================================================

for company in visible_items:

    name = company["name"]

    ticker = company["ticker"]

    strategy = company["strategy"]

    risk = company["risk"]

    news = st.session_state.news_data.get(
        ticker
    )


    # --------------------------------------------------------
    # SIN NOTICIAS
    # --------------------------------------------------------

    if news is None:

        score = company["base_score"]

        analysis = {
            "positive": 0,
            "negative": 0,
            "sentiment": 50
        }

        recent = 50

        signal = get_signal(score)

        confidence = calculate_confidence(
            score
        )


    # --------------------------------------------------------
    # CON NOTICIAS
    # --------------------------------------------------------

    else:

        score, analysis, recent = calculate_score(
            company,
            news
        )

        signal = get_signal(score)

        confidence = calculate_confidence(
            score
        )


    # ========================================================
    # TARJETA
    # ========================================================

    with st.container(border=True):

        left, center, right = st.columns(
            [1.1, 2.7, 1.5]
        )


        # ====================================================
        # INFORMACIÓN DE EMPRESA
        # ====================================================

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

                st.success(
                    "🟢 COMPRAR"
                )

            elif signal == "VENDER":

                st.error(
                    "🔴 VENDER"
                )

            else:

                st.warning(
                    "🟡 MANTENER"
                )


        # ====================================================
        # NOTICIAS
        # ====================================================

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
                            f"**{i}. "
                            f"[{title}]({link})**"
                        )

                    else:

                        st.write(
                            f"**{i}. {title}**"
                        )


                    if date_text:

                        st.caption(
                            f"{source} · {date_text}"
                        )

                    else:

                        st.caption(
                            source
                        )


                    if i < len(news[:5]):

                        st.divider()


        # ====================================================
        # SCORE
        # ====================================================

        with right:

            st.markdown(
                "### 🎯 Score táctico"
            )

            st.markdown(
                f"# {score}/100"
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


        # ====================================================
        # CONFIANZA
        # ====================================================

        st.divider()

        st.markdown(
            "### 📊 Confianza de la señal"
        )

        st.caption(
            "Interpretación heurística del sistema. "
            "No representa probabilidades estadísticas "
            "reales de subida o bajada."
        )


        p1, p2, p3 = st.columns(3)


        with p1:

            st.metric(
                "🟢 COMPRAR",
                f"{confidence['COMPRAR']}%"
            )


        with p2:

            st.metric(
                "🟡 MANTENER",
                f"{confidence['MANTENER']}%"
            )


        with p3:

            st.metric(
                "🔴 VENDER",
                f"{confidence['VENDER']}%"
            )


        # ====================================================
        # EXPLICACIÓN DE LA SEÑAL
        # ====================================================

        if signal == "COMPRAR":

            st.success(
                f"El sistema recomienda COMPRAR "
                f"porque el Score táctico es "
                f"{score}/100 y se encuentra en el "
                f"rango de 80–100."
            )

        elif signal == "MANTENER":

            st.warning(
                f"El sistema recomienda MANTENER "
                f"porque el Score táctico es "
                f"{score}/100 y se encuentra en el "
                f"rango intermedio de 60–79."
            )

        else:

            st.error(
                f"El sistema recomienda VENDER "
                f"porque el Score táctico es "
                f"{score}/100 y se encuentra "
                f"por debajo de 60."
            )


        # ====================================================
        # ESTRATEGIA
        # ====================================================

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
    "### 🧠 ¿Cómo se calcula el Score táctico?"
)

st.write(
    """
    El Score táctico es un indicador heurístico de 0 a 100
    que resume diferentes factores utilizados por el sistema.
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
    "### 📖 Interpretación del Score"
)


i1, i2, i3 = st.columns(3)


with i1:

    st.success(
        """
        **80–100**

        🟢 **COMPRAR**

        Escenario táctico favorable.
        """)


with i2:

    st.warning(
        """
        **60–79**

        🟡 **MANTENER**

        Escenario táctico intermedio.
        """)


with i3:

    st.error(
        """
        **0–59**

        🔴 **VENDER**

        Escenario táctico débil.
        """
    )


# ============================================================
# LIMITACIONES
# ============================================================

st.divider()

st.markdown(
    "### ⚠️ Importante"
)

st.write(
    """
    El Score y la confianza son indicadores heurísticos.
    No constituyen una predicción estadística del precio,
    recomendación financiera personalizada ni garantía
    de rendimiento.
    """
)


# ============================================================
# PIE
# ============================================================

st.divider()

st.caption(
    "Trading Tactical · V4 · Sin JavaScript · Sin base de datos"
)

st.caption(
    "Las noticias se consultan nuevamente al pulsar "
    "«Actualizar noticias». El sistema no conserva "
    "historial de noticias."
)
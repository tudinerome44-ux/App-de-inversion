import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from email.utils import parsedate_to_datetime
from datetime import datetime


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
    (
        "Advanced Micro Devices",
        "AMD",
        "COMPRAR",
        "Vigilar impulso de semiconductores y posibles rebotes rápidos."
    ),
    (
        "NVIDIA",
        "NVDA",
        "COMPRAR",
        "Prioridad táctica por exposición a IA; buscar entradas tras retrocesos."
    ),
    (
        "Cisco",
        "CSCO",
        "MANTENER",
        "Perfil más defensivo; mantener mientras no aparezca un catalizador claro."
    ),
    (
        "Lam Research",
        "LRCX",
        "COMPRAR",
        "Vigilar ciclo de semiconductores y gasto en fabricación."
    ),
    (
        "Intel",
        "INTC",
        "MANTENER",
        "Mayor incertidumbre relativa; esperar catalizador fuerte."
    ),
    (
        "Broadcom",
        "AVGO",
        "COMPRAR",
        "Interés táctico por IA, semiconductores y networking."
    ),
    (
        "Applied Materials",
        "AMAT",
        "COMPRAR",
        "Exposición al ciclo de equipamiento semiconductor."
    ),
    (
        "ASML Holding",
        "ASML",
        "COMPRAR",
        "Activo estratégico del ecosistema de semiconductores."
    ),
    (
        "KLA",
        "KLAC",
        "COMPRAR",
        "Exposición a control de procesos y fabricación de chips."
    ),
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

    .news-card {
        padding: 8px 0;
        border-bottom: 1px solid #30363d;
    }

    .news-title {
        font-size: 15px;
        font-weight: 600;
    }

    .news-source {
        color: #8b949e;
        font-size: 12px;
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

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# FUNCIONES
# ============================================================
def get_news(ticker):
    """
    Busca noticias actuales utilizando Google News RSS.
    No requiere API key.
    """

    query = quote(
        f"{ticker} stock OR {ticker} semiconductor"
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

        news = []

        for item in root.findall("./channel/item")[:5]:

            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")

            source_element = item.find("source")

            if source_element is not None:
                source = source_element.text or "Google News"
            else:
                source = "Google News"

            formatted_date = ""

            if pub_date:
                try:
                    dt = parsedate_to_datetime(pub_date)
                    formatted_date = dt.strftime(
                        "%d/%m/%Y %H:%M"
                    )
                except Exception:
                    formatted_date = pub_date

            news.append(
                {
                    "title": title,
                    "link": link,
                    "source": source,
                    "date": formatted_date
                }
            )

        return news

    except Exception as e:

        return [
            {
                "title": "No se pudieron cargar las noticias.",
                "link": "",
                "source": f"Error: {str(e)}",
                "date": ""
            }
        ]

# ============================================================
# CARGA / ACTUALIZACIÓN
# ============================================================
if "news_data" not in st.session_state:
    st.session_state.news_data = {}

if "last_update" not in st.session_state:
    st.session_state.last_update = None


def update_news():

    st.session_state.news_data = {}

    progress = st.progress(0)

    total = len(DATA)

    for index, company in enumerate(DATA):

        name, ticker, action, strategy = company

        st.session_state.news_data[ticker] = get_news(
            ticker
        )

        progress.progress(
            (index + 1) / total
        )

    st.session_state.last_update = datetime.now()

# ============================================================
# CABECERA
# ============================================================
st.title("📈 Trading Tactical")

st.caption(
    "Dashboard táctico de 9 empresas · Noticias actuales · "
    "Sin base de datos · Sin JavaScript"
)


# ============================================================
# CONTROLES
# ============================================================

c1, c2, c3 = st.columns([2, 1, 1])

with c1:

    search = st.text_input(
        "🔎 Buscar empresa o ticker",
        placeholder="Ej.: NVIDIA o NVDA"
    )


with c2:

    filt = st.selectbox(
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

        update_news()

        st.success(
            "Noticias actualizadas."
        )

# ============================================================
# FILTRADO
# ============================================================
items = DATA

if search.strip():

    q = search.lower().strip()

    items = [
        x
        for x in items
        if q in x[0].lower()
        or q in x[1].lower()
    ]


if filt != "Todas":

    items = [
        x
        for x in items
        if x[2] == filt
    ]


st.write(
    f"**Empresas mostradas:** "
    f"{len(items)} / {len(DATA)}"
)


if st.session_state.last_update:

    st.caption(
        "Última actualización: "
        + st.session_state.last_update.strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )

# ============================================================
# EMPRESAS
# ============================================================
for name, ticker, action, strategy in items:

    with st.container(border=True):

        a, b, c = st.columns(
            [1.1, 2.7, 1.5]
        )

        # ----------------------------------------------------
        # INFORMACIÓN EMPRESA
        # ----------------------------------------------------

        with a:

            st.subheader(ticker)

            st.write(name)

            if action == "COMPRAR":

                st.markdown(
                    '<span class="buy">🟢 COMPRAR</span>',
                    unsafe_allow_html=True
                )

            elif action == "VENDER":

                st.markdown(
                    '<span class="sell">🔴 VENDER</span>',
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    '<span class="hold">🟡 MANTENER</span>',
                    unsafe_allow_html=True
                )


        # ----------------------------------------------------
        # NOTICIAS
        # ----------------------------------------------------

        with b:

            st.markdown(
                "### 📰 5 noticias actuales"
            )

            news = st.session_state.news_data.get(
                ticker
            )

            if news is None:

                st.info(
                    "Pulsa «🔄 Actualizar noticias» "
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

                    if link:

                        st.markdown(
                            f"""
                            **{i}. [{title}]({link})**

                            <span class="news-source">
                            {source}
                            {" · " + date if date else ""}
                            </span>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.write(
                            f"{i}. {title}"
                        )

                    st.divider()


        # ----------------------------------------------------
        # ESTRATEGIA
        # ----------------------------------------------------

        with c:

            st.markdown(
                "### 🎯 Estrategia táctica"
            )

            st.write(strategy)

            st.markdown(
                "### 📊 Estado"
            )

            if action == "COMPRAR":

                st.success(
                    "Prioridad táctica"
                )

            elif action == "VENDER":

                st.error(
                    "Reducir exposición"
                )

            else:

                st.warning(
                    "Mantener vigilancia"
                )

# ============================================================
# PIE
# ============================================================
st.divider()

st.caption(
    "Las noticias se consultan al presionar "
    "«Actualizar noticias». No se almacenan en una base de datos."
)

st.caption(
    "Siguiente etapa: utilizar las noticias actuales "
    "para calcular automáticamente el Score táctico 0–100."
)

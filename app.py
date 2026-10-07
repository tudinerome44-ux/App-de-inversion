import streamlit as st

st.set_page_config(page_title='Trading Tactical — Prueba', page_icon='📈', layout='wide')

DATA = [
('Advanced Micro Devices','AMD','COMPRAR','Vigilar impulso de semiconductores y posibles rebotes rápidos.', 'https://finance.yahoo.com/quote/AMD/'),
('NVIDIA','NVDA','COMPRAR','Prioridad táctica por exposición a IA; buscar entradas tras retrocesos.', 'https://finance.yahoo.com/quote/NVDA/'),
('Cisco','CSCO','MANTENER','Perfil más defensivo; mantener mientras no aparezca un catalizador claro.', 'https://finance.yahoo.com/quote/CSCO/'),
('Lam Research','LRCX','COMPRAR','Vigilar ciclo de semiconductores y gasto en fabricación.', 'https://finance.yahoo.com/quote/LRCX/'),
('Intel','INTC','MANTENER','Mayor incertidumbre relativa; esperar catalizador fuerte.', 'https://finance.yahoo.com/quote/INTC/'),
('Broadcom','AVGO','COMPRAR','Interés táctico por IA, semiconductores y networking.', 'https://finance.yahoo.com/quote/AVGO/'),
('Applied Materials','AMAT','COMPRAR','Exposición al ciclo de equipamiento semiconductor.', 'https://finance.yahoo.com/quote/AMAT/'),
('ASML Holding','ASML','COMPRAR','Activo estratégico del ecosistema de semiconductores.', 'https://finance.yahoo.com/quote/ASML/'),
('KLA','KLAC','COMPRAR','Exposición a control de procesos y fabricación de chips.', 'https://finance.yahoo.com/quote/KLAC/'),
]

st.title('📈 Trading Tactical — versión de prueba')
st.caption('Interfaz Streamlit para las 9 empresas. Esta versión NO consulta noticias en Internet todavía.')

c1,c2,c3 = st.columns([2,1,1])
with c1: search = st.text_input('🔎 Buscar empresa o ticker', placeholder='Ej.: NVIDIA o NVDA')
with c2: filt = st.selectbox('Señal',['Todas','COMPRAR','MANTENER','VENDER'])
with c3:
    if st.button('🔄 Actualizar interfaz', use_container_width=True): st.rerun()

items = DATA
if search.strip():
    q=search.lower().strip(); items=[x for x in items if q in x[0].lower() or q in x[1].lower()]
if filt!='Todas': items=[x for x in items if x[2]==filt]
st.write(f'**Empresas mostradas:** {len(items)} / {len(DATA)}')

for name,ticker,action,strategy,baseurl in items:
    with st.container(border=True):
        a,b,c=st.columns([1.1,2.4,1.4])
        with a:
            st.subheader(ticker)
            st.write(name)
            st.write('**Precio:** Dato de prueba')
            st.write('**Movimiento:** —')
            st.write(f'**{action}**')
        with b:
            st.markdown('**📰 5 noticias / referencias**')
            for i in range(1,6):
                st.markdown(f'{i}. [Referencia {i} de {ticker}]({baseurl})')
        with c:
            st.markdown('**🎯 Estrategia táctica**')
            st.write(strategy)
            st.info('Modo prueba: no son noticias en tiempo real.')

st.divider()
st.caption('Siguiente etapa: conectar la interfaz a una búsqueda de noticias actuales, sin base de datos ni historial persistente.')

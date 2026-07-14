import streamlit as st
import yfinance as yf
import pandas as pd

def calcular_rsi(precios, periodo=14):
    delta = precios.diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    
    avg_ganancia = ganancia.rolling(window=periodo).mean()
    avg_perdida = perdida.rolling(window=periodo).mean()
    
    rs = avg_ganancia / avg_perdida
    rsi = 100 - (100 / (1 + rs))
    return rsi

st.title("Mini Dashboard Financiero")

# Selector de múltiples acciones
tickers = st.multiselect("Elige una o más acciones para comparar", ["AAPL", "TSLA", "AMZN", "GOLD"], default=["AAPL"])

if tickers:
    precios = pd.DataFrame()
    
    for t in tickers:
        data = yf.download(t, period="2y")
        data.columns = data.columns.get_level_values(0)
        precios[t] = data["Close"]
    
    st.subheader("Comparación de precios históricos")
    st.line_chart(precios)
    
    st.subheader("Detalle por acción")
    ticker_detalle = st.selectbox("Elige una acción para ver medias móviles y volatilidad", tickers)
    data_detalle = yf.download(ticker_detalle, period="2y")
    data_detalle.columns = data_detalle.columns.get_level_values(0)

    data_detalle["MA7"] = data_detalle["Close"].rolling(window=7).mean()
    data_detalle["MA30"] = data_detalle["Close"].rolling(window=30).mean()

    st.line_chart(data_detalle[["Close", "MA7", "MA30"]])

    data_detalle["Daily_Return"] = data_detalle["Close"].pct_change()
    volatilidad = data_detalle["Daily_Return"].std() * (252 ** 0.5)

    st.metric(label=f"Volatilidad anualizada de {ticker_detalle}", value=f"{volatilidad:.2%}")

    # RSI
    data_detalle["RSI"] = calcular_rsi(data_detalle["Close"])

    st.subheader(f"RSI de {ticker_detalle} (14 días)")
    st.line_chart(data_detalle["RSI"])

    rsi_actual = data_detalle["RSI"].iloc[-1]
    if rsi_actual > 70:
        st.warning(f"RSI actual: {rsi_actual:.1f} — posible sobrecompra")
    elif rsi_actual < 30:
        st.warning(f"RSI actual: {rsi_actual:.1f} — posible sobreventa")
    else:
        st.info(f"RSI actual: {rsi_actual:.1f} — en rango neutral")
        st.subheader("De los mercados a tu bolsillo")
    st.write("Conecta lo que pasa en los mercados con decisiones financieras reales de un joven.")

    ingreso_mensual = st.number_input("Ingreso mensual hipotético (USD)", min_value=0, value=500, step=50)
    tasa_interes_anual = st.slider("Tasa de interés anual de una deuda (%, ej. tarjeta o BNPL)", 0.0, 60.0, 24.0)
    monto_deuda = st.number_input("Monto de la deuda (USD)", min_value=0, value=200, step=25)

    interes_anual = monto_deuda * (tasa_interes_anual / 100)
    interes_mensual = interes_anual / 12
    porcentaje_ingreso = (interes_mensual / ingreso_mensual * 100) if ingreso_mensual > 0 else 0

    st.metric("Interés que pagarías al año", f"${interes_anual:.2f}")
    st.metric("Interés mensual como % de tu ingreso", f"{porcentaje_ingreso:.1f}%")

    if porcentaje_ingreso > 10:
        st.warning("Esta deuda representa una parte significativa de tu ingreso mensual — vale la pena repensar el plan de pago.")
    else:
        st.info("Esta deuda es manejable respecto a tu ingreso mensual, pero sigue siendo importante pagarla a tiempo.")
else:
    st.warning("Elige al menos una acción para ver el gráfico.")
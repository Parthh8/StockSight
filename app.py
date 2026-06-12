import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="StockSight",
    layout="wide"
)

st.title("📈 StockSight - Real Time Stock Dashboard")

# ==========================
# SIDEBAR
# ==========================

st.sidebar.header("Stock Selection")

stocks = st.sidebar.multiselect(
    "Select Stocks",
    ["AAPL", "MSFT", "GOOG", "NVDA", "TSLA",
     "RELIANCE.NS", "TCS.NS", "INFY.NS"],
    default=["AAPL"]
)

period = st.sidebar.selectbox(
    "Select Period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3
)

if len(stocks) == 0:
    st.warning("Please select at least one stock.")
    st.stop()

stock = stocks[0]

st.sidebar.markdown("### Selected Stocks")
st.sidebar.write(", ".join(stocks))

# ==========================
# DOWNLOAD DATA
# ==========================

data = yf.download(
    stock,
    period=period,
    auto_adjust=True,
    progress=False
)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# ==========================
# MAIN DASHBOARD
# ==========================

if not data.empty:

    st.subheader(f"{stock} Stock Data")

    # ==========================
    # COMPANY OVERVIEW
    # ==========================

    try:
        ticker = yf.Ticker(stock)
        info = ticker.info

        st.subheader("🏢 Company Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Sector",
            info.get("sector", "N/A")
        )

        col2.metric(
            "Country",
            info.get("country", "N/A")
        )

        market_cap = info.get("marketCap", 0)

        if market_cap:
            market_cap_display = f"${market_cap/1_000_000_000:.1f}B"
        else:
            market_cap_display = "N/A"

        col3.metric(
            "Market Cap",
            market_cap_display
        )

        with st.expander("📖 Business Summary"):
            st.write(
                info.get(
                    "longBusinessSummary",
                    "No information available."
                )
            )

    except:
        st.warning("Company information unavailable.")

    # ==========================
    # STOCK METRICS
    # ==========================

    latest_price = float(data["Close"].iloc[-1])
    highest_price = float(data["High"].max())
    lowest_price = float(data["Low"].min())

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Current Price",
        f"${latest_price:.2f}"
    )

    col2.metric(
        "Highest Price",
        f"${highest_price:.2f}"
    )

    col3.metric(
        "Lowest Price",
        f"${lowest_price:.2f}"
    )

    # ==========================
    # MOVING AVERAGES
    # ==========================

    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()

    # ==========================
    # CANDLESTICK CHART
    # ==========================

    st.subheader("📈 Stock Price Chart")

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Price"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA20"],
            mode="lines",
            name="MA20"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA50"],
            mode="lines",
            name="MA50"
        )
    )

    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ==========================
    # RSI INDICATOR
    # ==========================

    delta = data["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    data["RSI"] = 100 - (100 / (1 + rs))

    st.subheader("📉 RSI Indicator")

    st.line_chart(data["RSI"])

    st.caption(
        "RSI > 70 = Overbought | RSI < 30 = Oversold"
    )

    # ==========================
    # MACD INDICATOR
    # ==========================

    exp12 = data["Close"].ewm(span=12, adjust=False).mean()
    exp26 = data["Close"].ewm(span=26, adjust=False).mean()

    data["MACD"] = exp12 - exp26
    data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

    st.subheader("📊 MACD Indicator")

    macd_fig = go.Figure()

    macd_fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MACD"],
            mode="lines",
            name="MACD"
        )
    )

    macd_fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Signal"],
            mode="lines",
            name="Signal"
        )
    )

    macd_fig.update_layout(
        height=400
    )

    st.plotly_chart(
        macd_fig,
        use_container_width=True
    )

    # ==========================
    # VOLUME CHART
    # ==========================

    st.subheader("📊 Trading Volume")

    volume_fig = go.Figure()

    volume_fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"]
        )
    )

    volume_fig.update_layout(
        height=400
    )

    st.plotly_chart(
        volume_fig,
        use_container_width=True
    )

    # ==========================
    # HISTORICAL DATA
    # ==========================

    st.subheader("📋 Historical Data")

    st.dataframe(data)

    # ==========================
    # DOWNLOAD CSV
    # ==========================

    csv = data.to_csv().encode("utf-8")

    st.download_button(
        label="📥 Download Stock Data",
        data=csv,
        file_name=f"{stock}_data.csv",
        mime="text/csv"
    )

    # ==========================
    # STOCK COMPARISON
    # ==========================

    st.subheader("📊 Stock Comparison")

    comparison_df = pd.DataFrame()

    for s in stocks:

        temp = yf.download(
            s,
            period=period,
            auto_adjust=True,
            progress=False
        )

        if isinstance(temp.columns, pd.MultiIndex):
            temp.columns = temp.columns.get_level_values(0)

        comparison_df[s] = temp["Close"]

    st.line_chart(comparison_df)

else:
    st.error("No data found")
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np


# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="StockSight",
    layout="wide"
)

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

h1 {
    text-align: center;
}

div[data-testid="metric-container"] {
    background-color: #262730;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #404040;
}

</style>
""", unsafe_allow_html=True)

st.title("📈 StockSight")

st.caption(
    "Real-Time Stock Analysis Dashboard with Technical Indicators"
)

# ==========================
# SIDEBAR
# ==========================

st.sidebar.header("Stock Selection")

st.sidebar.info(
    """
    StockSight v2.0

    Features:
    • RSI
    • MACD
    • Bollinger Bands
    • Portfolio Tracker
    """
)

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
    # BOLLINGER BANDS
    # ==========================

    data["STD"] = data["Close"].rolling(20).std()

    data["Upper Band"] = data["MA20"] + (data["STD"] * 2)
    data["Lower Band"] = data["MA20"] - (data["STD"] * 2)

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

    fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["Upper Band"],
        mode="lines",
        name="Upper Band"
    )
)

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Lower Band"],
            mode="lines",
            name="Lower Band"
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
    # PORTFOLIO TRACKER
    # ==========================

    st.subheader("💼 Portfolio Tracker")

    shares = st.number_input(
        "Enter Number of Shares",
        min_value=0,
        value=10,
        step=1
    )

    portfolio_value = latest_price * shares

    st.metric(
        "Portfolio Value",
        f"${portfolio_value:,.2f}"
    )

    st.subheader("📊 Performance Statistics")

    daily_return = data["Close"].pct_change().mean() * 100

    volatility = data["Close"].pct_change().std() * 100

    high_52 = data["High"].max()

    low_52 = data["Low"].min()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Avg Daily Return", f"{daily_return:.2f}%")
    c2.metric("Volatility", f"{volatility:.2f}%")
    c3.metric("Period High", f"${high_52:.2f}")
    c4.metric("Period Low", f"${low_52:.2f}")

    st.subheader("🤖 AI Trend Prediction")

    df = data.copy()

    df["Day"] = np.arange(len(df))

    X = df[["Day"]]

    y = df["Close"]

    model = LinearRegression()

    model.fit(X, y)

    next_day = [[len(df)]]

    prediction = model.predict(next_day)[0]

    st.metric(
        "Predicted Next Close",
        f"${prediction:.2f}"
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
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="StockSight",
    layout="wide"
)

st.title("📈 StockSight - Real Time Stock Dashboard")

# Sidebar
st.sidebar.header("Stock Selection")

stocks = st.sidebar.multiselect(
    "Select Stocks",
    ["AAPL", "MSFT", "GOOG", "NVDA", "TSLA", "RELIANCE.NS", "TCS.NS", "INFY.NS"],
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

data = yf.download(
    stock,
    period=period,
    auto_adjust=True,
    progress=False
)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

st.sidebar.markdown("### Selected Stocks")
st.sidebar.write(", ".join(stocks))

if not data.empty:

    st.subheader(f"{stock} Stock Data")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

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

    # Moving averages
    data["MA20"] = data["Close"].rolling(window=20).mean()
    data["MA50"] = data["Close"].rolling(window=50).mean()

    # Candlestick Chart
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
            name="20 Day MA"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA50"],
            mode="lines",
            name="50 Day MA"
        )
    )

    fig.update_layout(
        height=700,
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Volume Chart
    st.subheader("📊 Trading Volume")

    volume_fig = go.Figure()

    volume_fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"],
            name="Volume"
        )
    )

    volume_fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Volume"
    )

    st.plotly_chart(volume_fig)

    st.subheader("📋 Historical Data")

    st.dataframe(data)

    # ==========================
    # STOCK COMPARISON SECTION
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
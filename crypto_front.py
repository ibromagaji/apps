import streamlit as st
import requests

FASTAPI_URL = "http://crypto.fastapps.duckdns.org"


st.set_page_config(
    page_title="Crypto Tracker Dashboard",
    page_icon="🪙",
    layout="wide"
)

# Keep selected coins across reruns
if "selected_coins" not in st.session_state:
    st.session_state.selected_coins = {}
if "search_results" not in st.session_state:
    st.session_state.search_results = []

st.title("🪙 Real-Time Crypto Performance Tracker")
st.caption("Search for any coin, build your watchlist, then fetch live market data.")
st.markdown("---")

#SEARCH
search_col, button_col = st.columns([4, 1])
with search_col:
    query = st.text_input("🔍 Search for a cryptocurrency", placeholder="e.g. bitcoin, doge, sol...", label_visibility="collapsed")
with button_col:
    search_clicked = st.button("Search", use_container_width=True)

if search_clicked and query.strip():
    try:
        resp = requests.get(f"{FASTAPI_URL}/search", params={"q": query.strip()})
        if resp.status_code == 200:
            st.session_state.search_results = resp.json()
            if not st.session_state.search_results:
                st.info(f"No coins found matching '{query}'.")
        else:
            st.error(f"❌ Backend error: {resp.status_code}")
            st.session_state.search_results = []
    except requests.exceptions.ConnectionError:
        st.error(f"🔌 Could not reach your FastAPI backend at `{FASTAPI_URL}`. Is it running?")
        st.session_state.search_results = []

#SEARCH RESULTS
if st.session_state.search_results:
    st.subheader("Search Results")
    for coin in st.session_state.search_results:
        coin_id = coin["id"]
        already_added = coin_id in st.session_state.selected_coins

        row = st.columns([3, 1, 1])
        row[0].write(f"**{coin['name']}** ({coin['symbol']}) · Rank #{coin['rank']}")
        if already_added:
            row[1].write("✅ Added")
        else:
            if row[1].button("➕ Add", key=f"add_{coin_id}"):
                st.session_state.selected_coins[coin_id] = {"name": coin["name"], "symbol": coin["symbol"]}
                st.rerun()
    st.markdown("---")

#YOUR WATCHLIST
st.subheader("📋 Your Watchlist")
if not st.session_state.selected_coins:
    st.info("No coins selected yet. Use the search box above to find and add some.")
else:
    for coin_id, info in list(st.session_state.selected_coins.items()):
        row = st.columns([4, 1])
        row[0].write(f"**{info['name']}** ({info['symbol']})")
        if row[1].button("❌ Remove", key=f"remove_{coin_id}"):
            del st.session_state.selected_coins[coin_id]
            st.rerun()

st.markdown("---")

#TIMEFRAME + FETCH
timeframe_options = {
    "1 Hour": "1h",
    "24 Hours": "24h",
    "7 Days": "7d",
    "30 Days": "30d",
    "1 Year": "1y"
}
tf_col, fetch_col = st.columns([3, 1])
with tf_col:
    selected_tf_display = st.selectbox("Performance Timeframe", options=list(timeframe_options.keys()))
    timeframe_value = timeframe_options[selected_tf_display]
with fetch_col:
    st.write("")
    fetch_clicked = st.button("🚀 Fetch Market Data", type="primary", use_container_width=True)

#FETCH + DISPLAY
if fetch_clicked:
    if not st.session_state.selected_coins:
        st.warning("⚠️ Add at least one coin to your watchlist first.")
    else:
        payload = {
            "cryptos": list(st.session_state.selected_coins.keys()),
            "timeframe": timeframe_value
        }

        with st.spinner("Querying backend and parsing market tickers..."):
            try:
                response = requests.post(f"{FASTAPI_URL}/crypto", json=payload)

                if response.status_code == 200:
                    crypto_data_list = response.json()

                    if not crypto_data_list:
                        st.info("No matching ticker data returned.")
                    else:
                        st.subheader(f"📈 Market Metrics (Change over: {selected_tf_display})")
                        st.write("")

                        for coin in crypto_data_list:
                            name = coin.get("name", "Unknown")
                            symbol = coin.get("symbol", "")
                            rank = coin.get("rank", "N/A")
                            price = coin.get("price", "0.00")
                            market_cap = coin.get("market_cap", "0")
                            change = coin.get("change", 0.0)

                            with st.container():
                                col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])

                                with col1:
                                    st.markdown(f"### **{name}** (`{symbol}`)")
                                    st.markdown(f"🏆 **Global Rank:** #{rank}")

                                with col2:
                                    st.metric(label="Current Price (USD)", value=f"${price}")

                                with col3:
                                    st.metric(label="Market Cap", value=market_cap)

                                with col4:
                                    st.metric(
                                        label=f"Change ({timeframe_value})",
                                        value=f"{change:+.2f}%"
                                    )

                            st.markdown("---")
                else:
                    st.error(f"Backend error status code: {response.status_code}")
                    try:
                        st.json(response.json())
                    except Exception:
                        pass

            except requests.exceptions.ConnectionError:
                st.error(f"Could not reach your FastAPI backend at `{FASTAPI_URL}`. Is it running?")

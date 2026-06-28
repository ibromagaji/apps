import streamlit as st
import requests

# Set page configuration
st.set_page_config(
    page_title="Crypto Tracker Dashboard",
    page_icon="🪙",
    layout="wide"
)

# --- SIDEBAR: CONFIGURATION & INPUTS ---
st.sidebar.header("⚙️ Backend Configuration")
# Input field to drop your localhost link seamlessly
base_url = st.sidebar.text_input("FastAPI Base URL", value="http://127.0.0.1:8000").strip("/")

st.sidebar.markdown("---")
st.sidebar.header("📊 Selection Matrix")

# Pre-defined list of popular Coinpaprika IDs (users can multi-select)
available_cryptos = {
    "Bitcoin (btc-bitcoin)": "btc-bitcoin",
    "Ethereum (eth-ethereum)": "eth-ethereum",
    "Solana (sol-solana)": "sol-solana",
    "Ripple (xrp-xrp)": "xrp-xrp",
    "Cardano (ada-cardano)": "ada-cardano",
    "Dogecoin (doge-dogecoin)": "doge-dogecoin",
    "BNB (bnb-binance-coin)": "bnb-binance-coin"
}

selected_display_names = st.sidebar.multiselect(
    "Select Cryptocurrencies:",
    options=list(available_cryptos.keys()),
    default=["Bitcoin (btc-bitcoin)", "Ethereum (eth-ethereum)"]
)

# Map selected names back to Coinpaprika string IDs expected by your FastAPI validation
crypto_ids = [available_cryptos[name] for name in selected_display_names]

# Timeframe dropdown matched to your pydantic validation list
timeframe_options = {
    "1 Hour": "1h",
    "24 Hours": "24h",
    "7 Days": "7d",
    "30 Days": "30d",
    "1 Year": "1y"
}
selected_tf_display = st.sidebar.selectbox("Select Performance Timeframe:", options=list(timeframe_options.keys()))
timeframe_value = timeframe_options[selected_tf_display]

# --- MAIN DASHBOARD INTERFACE ---
st.title("🪙 Real-Time Crypto Performance Tracker")
st.caption("Streamlit execution interface hitting your local FastAPI analytical engine.")
st.markdown("---")

# Trigger button
if st.sidebar.button("🚀 Fetch Market Data", type="primary"):
    if not crypto_ids:
        st.warning("⚠️ Please select at least one cryptocurrency from the sidebar list.")
    else:
        # Prepare JSON payload matching your Pydantic "frontend_data" model schema
        payload = {
            "cryptos": crypto_ids,
            "timeframe": timeframe_value
        }
        
        with st.spinner("Querying backend and parsing market tickers..."):
            try:
                # Making a POST request to your '/crypto' endpoint
                response = requests.post(f"{base_url}/crypto", json=payload)
                
                if response.status_code == 200:
                    crypto_data_list = response.json()
                    
                    if not crypto_data_list:
                        st.info("No matching token ticker information returned from your endpoint data loop.")
                    else:
                        st.subheader(f"📈 Market Metrics Overview (Changes based on: {selected_tf_display})")
                        st.write("")
                        
                        # Loop through and present each token inside clean metric blocks
                        for coin in crypto_data_list:
                            # Parse parameters safely
                            name = coin.get("name", "Unknown")
                            symbol = coin.get("symbol", "")
                            rank = coin.get("rank", "N/A")
                            price = coin.get("price", "0.00")
                            market_cap = coin.get("market_cap", "0")
                            change = coin.get("change", 0.0)
                            
                            # Layout individual coin data blocks elegantly
                            with st.container():
                                col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1])
                                
                                with col1:
                                    st.markdown(f"### **{name}** (`{symbol}`)")
                                    st.markdown(f"🏆 **Global Rank:** #{rank}")
                                
                                with col2:
                                    st.metric(label="Current Price (USD)", value=f"${price}")
                                    
                                with col3:
                                    st.metric(label="Market Capitalization", value=market_cap)
                                    
                                with col4:
                                    # Color color coordination depending on price direction
                                    st.metric(
                                        label=f"Change ({timeframe_value})", 
                                        value=f"{change:+.2f}%",
                                        delta=f"{change:.2f}%" if change >= 0 else f"{change:.2f}%"
                                    )
                                    
                            st.markdown("---")
                            
                else:
                    st.error(f"❌ Backend error status code returned: {response.status_code}")
                    st.json(response.json())
                    
            except requests.exceptions.ConnectionError:
                st.error("🔌 **Connection Error:** Could not contact your FastAPI local instance server. Verify it's spinning on that exact port link.")
else:
    st.info("💡 Adjust the metrics selection matrix options on your left sidebar pane and hit 'Fetch Market Data'.")
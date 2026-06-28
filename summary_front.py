import streamlit as st
import requests

# Page setup for a modern layout
st.set_page_config(
    page_title="Multi-LLM Hub Gateway",
    page_icon="🤖",
    layout="wide"
)

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header("⚙️ Server Configuration")
base_url = st.sidebar.text_input("FastAPI Base URL", value="http://127.0.0.1:8000").strip("/")

st.sidebar.markdown("---")
st.sidebar.header("🧠 Engine Control")

# 1. Feature selection (Determines persona/endpoint family)
app_mode = st.sidebar.selectbox(
    "Select App Persona:",
    options=["News Summarizer (SummarizePro)", "AI Assistant (Orion)"]
)

# 2. Dynamic Provider Selector requested
llm_provider = st.sidebar.selectbox(
    "Choose LLM Provider Provider:",
    options=["OpenAI", "Claude", "Gemini"]
)

st.sidebar.markdown("---")
# Informative contextual sidebar summary
st.sidebar.caption(
    f"Target Endpoint Vector:\n"
    f"`/{llm_provider.lower() if app_mode.startswith('News') else llm_provider.lower() + '-assistant'}`"
)

# --- MAIN PAGE INTERFACE ---
st.title("🤖 Multi-Provider LLM Orchestrator")
st.caption("A unified Streamlit testing canvas routed directly to your FastAPI LLM integrations.")
st.markdown("---")

# Dynamic UI adjustments based on selected Persona
if app_mode == "News Summarizer (SummarizePro)":
    st.header("📝 Smart Text Summarization Engine")
    st.info("💡 **SummarizePro Tip:** You can ask for a specific style at the end of your prompt (e.g., *'Explain like I'm 12'*, *'Executive summary'*, or *'One paragraph'*).")
    input_label = "Paste your long text, article, document transcript, or news content below:"
    placeholder_text = "Paste text to compress here..."
    button_text = "Generate Concise Summary"
else:
    st.header("✨ Orion AI Assistant Workspace")
    input_label = "What problem or query would you like Orion to solve?"
    placeholder_text = "Ask anything technical, creative, or multi-step..."
    button_text = "Consult AI Assistant"

# Standard prompt box text area input
user_prompt = st.text_area(input_label, height=250, placeholder=placeholder_text)

# Routing computation logic when the action button executes
if st.button(button_text, type="primary"):
    if not user_prompt.strip():
        st.warning("⚠️ Please provide text or an engineering/creative prompt input before running inference.")
    else:
        # Determine endpoint path string based on selection states
        provider_key = llm_provider.lower()
        endpoint_path = f"/{provider_key}" if app_mode.startswith("News") else f"/{provider_key}-assistant"
        full_inference_url = f"{base_url}{endpoint_path}"
        
        # Setup query parameters (FastAPI expects prompt: str as a query string parameter)
        params = {"prompt": user_prompt}
        
        with st.spinner(f"Routing request to {llm_provider} backend instance..."):
            try:
                # Making a POST call to your selected FastAPI endpoint vector
                response = requests.post(full_inference_url, params=params)
                
                if response.status_code == 200:
                    try:
                        result_data = response.json()
                        
                        # Handle parsing checks depending on what raw object your backend returns
                        if isinstance(result_data, dict):
                            # Fallback check if full json content blocks are passed out directly
                            if "choices" in result_data:
                                response_output = result_data["choices"][0]["message"]["content"]
                            elif "content" in result_data and isinstance(result_data["content"], list):
                                response_output = result_data["content"][0]["text"]
                            else:
                                response_output = str(result_data)
                        else:
                            response_output = result_data
                            
                        # Presenting inference generation
                        st.subheader("📊 Generation Output")
                        st.markdown(response_output)
                        
                    except Exception as parse_error:
                        st.error(f"Failed to parse backend data response format. Raw Response: {response.text}")
                else:
                    st.error(f"❌ Server Error: Received status code {response.status_code}")
                    if response.text:
                        st.code(response.text, language="json")
                        
            except requests.exceptions.ConnectionError:
                st.error("🔌 **Target Connection Offline:** Could not access your local FastAPI instance. Verify your uvicorn worker is active and matching the sidebar base URL configuration.")
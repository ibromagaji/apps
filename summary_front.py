import streamlit as st
import requests


#FASTAPI_URL = "http://summary.fastapps.duckdns.org"
FASTAPI_URL = "https://lqwultkobazz6x5s6gtvnm23ri0dxisc.lambda-url.us-east-1.on.aws"


st.set_page_config(page_title="LLM Hub", page_icon="🤖", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"/"assistant", "content": str}]

# --- Header row: title + new chat ---
title_col, clear_col = st.columns([5, 1])
with title_col:
    st.title("🤖 LLM Hub")
with clear_col:
    st.write("")
    if st.button("🗑️ New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Inline persona + provider switcher (like switching models mid-chat) ---
mode_col, provider_col = st.columns(2)
with mode_col:
    persona = st.selectbox(
        "Persona", ["Summarizer", "Assistant"],
        label_visibility="collapsed"
    )
with provider_col:
    provider = st.selectbox(
        "Model", ["Claude", "OpenAI", "Gemini"],
        label_visibility="collapsed"
    )

st.divider()

# --- Render existing conversation ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input ---
placeholder = "Paste text to summarize..." if persona == "Summarizer" else "Ask Orion anything..."
prompt = st.chat_input(placeholder)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    endpoint = f"/{provider.lower()}" if persona == "Summarizer" else f"/{provider.lower()}-assistant"
    url = f"{FASTAPI_URL}{endpoint}"

    with st.chat_message("assistant"):
        with st.spinner(f"{provider} is thinking..."):
            try:
                resp = requests.post(url, params={"prompt": prompt}, timeout=60)
                if resp.status_code == 200:
                    text = resp.json().get("response", "*(empty response)*")
                else:
                    try:
                        detail = resp.json().get("detail", resp.text)
                    except Exception:
                        detail = resp.text
                    text = f"⚠️ {provider} backend error ({resp.status_code}): {detail}"
            except requests.exceptions.ConnectionError:
                text = f"🔌 Could not reach the backend at `{FASTAPI_URL}`. Is it running?"

        st.markdown(text)

    st.session_state.messages.append({"role": "assistant", "content": text})
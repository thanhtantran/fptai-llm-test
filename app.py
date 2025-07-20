import os, json, requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FPT_API_KEY")
BASE_URL = "https://mkp-api.fptcloud.com/chat/completions"

MODELS = [
    "FPT.AI-KIE-v1.7",
    "FPT.AI-Table-Parsing-v1.1",
    "FPT.AI-VITs"
]

st.set_page_config(page_title="FPT.AI Chat Demo", page_icon="🤖")
st.title("🤖 FPT.AI LLM Chat Demo")
st.caption("Thử 3 models của FPT bằng cách lựa chọn ở đây.")

with st.sidebar:
    model_choice = st.selectbox("Model", MODELS, index=0)
    st.caption("Select a model and start chatting.")

# --- Chat state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input ---
prompt = st.chat_input("Nhập vào câu hỏi của bạn …")
if prompt:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Build payload ---
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": model_choice,
        "messages": [
            {"role": "system", "content": "Bạn là trợ lý toàn năng, bạn hãy trả lời câu hỏi bằng ngôn ngữ của người dùng hỏi."},
            *st.session_state.messages
        ],
        "stream": True
    }

    # --- Streaming answer ---
    with st.chat_message("assistant"):
        answer_box = st.empty()
        full_response = ""
        try:
            r = requests.post(BASE_URL, headers=headers, json=payload, stream=True, timeout=60)
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        full_response += delta
                        answer_box.markdown(full_response)
                    except Exception:
                        continue
        except Exception as e:
            st.error(f"API error: {e}")
            full_response = "**Error contacting the model**"

        # Save assistant message
        st.session_state.messages.append({"role": "assistant", "content": full_response})

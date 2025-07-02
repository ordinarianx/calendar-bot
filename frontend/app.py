import os
import streamlit as st
import httpx
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="🗓️ Calendar Bot", page_icon="🤖")
st.title("🤖 Your Calendar Assistant")
st.markdown("Type a request and I’ll handle your Google Calendar for you.")

# Initialize chat history in session state
if "history" not in st.session_state:
    st.session_state.history = []

# Display chat history and slot buttons
for idx, msg in enumerate(st.session_state.history):
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
        for slot in msg.get("slots", []):
            start = slot['start'][11:16]
            end = slot['end'][11:16]
            label = f"Book {start}–{end}"
            if st.button(label, key=f"slot-{idx}-{start}"):
                details = f"Title: Meeting; Start: {slot['start']}; Duration: 30"
                with st.spinner("Booking event..."):
                    booking_resp = httpx.post(
                        f"{FASTAPI_URL}/run",
                        json={"prompt": f"Book: {details}"},
                        timeout=10
                    )
                    booking = booking_resp.json().get("content", "")
                st.success(booking)

# Prompt input
user_msg = st.chat_input("Ask me to check availability or book an event...")
if user_msg:
    # Append user message and display immediately
    st.session_state.history.append({"role": "user", "content": user_msg})
    st.chat_message("user").write(user_msg)

    # Build conversation history for context
    MAX_HISTORY = 10
    history = ""
    for msg in st.session_state.history[-MAX_HISTORY:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"
    prompt = f"{history}Assistant:"

    # Call agent and display response in real time
    with st.spinner("Thinking..."):
        try:
            resp = httpx.post(
                f"{FASTAPI_URL}/run",
                json={"prompt": prompt},
                timeout=30
            )
            data = resp.json()
            content = data.get("content", "")
            slots = data.get("slots", [])
        except Exception as e:
            content = f"Error: {e}"
            slots = []
    st.session_state.history.append({"role": "assistant", "content": content, "slots": slots})
    st.chat_message("assistant").write(content)
    for slot in slots:
        start = slot['start'][11:16]
        end = slot['end'][11:16]
        label = f"Book {start}–{end}"
        if st.button(label, key=f"slot-latest-{start}"):
            details = f"Title: Meeting; Start: {slot['start']}; Duration: 30"
            with st.spinner("Booking event..."):
                booking_resp = httpx.post(
                    f"{FASTAPI_URL}/run",
                    json={"prompt": f"Book: {details}"},
                    timeout=10
                )
                booking = booking_resp.json().get("content", "")
            st.success(booking)

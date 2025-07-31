import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

# Load secrets
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")
MODEL = os.getenv("MODEL")

def get_career_advice(messages):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"API error: {e}")
        return "Sorry, kuch galat ho gaya. Dobara try karo."

st.set_page_config(page_title="Career Chatbot", page_icon="🎓", layout="centered")
st.title("🎓 Career Path Chatbot")
st.write("Apni details do aur career advice pao.")

with st.form("user_form"):
    name = st.text_input("Tumhara Naam")
    academic_interest = st.text_area("Academic Interests")
    career_goals = st.text_area("Career Goals")
    skills = st.text_area("Skills (technical, communication, etc.)")
    submitted = st.form_submit_button("Start")

if submitted:
    if not name.strip():
        st.error("Naam zaroori hai.")
    else:
        system_prompt = {
            "role": "system",
            "content": (
                f"You are friendly career helper. Name: {name}\n"
                f"Interests: {academic_interest}\n"
                f"Goals: {career_goals}\n"
                f"Skills: {skills}\n"
                f"Give warm welcome and suggestions."
            )
        }
        st.session_state.messages = [system_prompt]
        with st.spinner("Advice le rahe hain..."):
            reply = get_career_advice(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").markdown(reply)

if "messages" in st.session_state:
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Aur poochna hai?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Soch rahe hain..."):
            response = get_career_advice(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("user").markdown(prompt)
        st.chat_message("assistant").markdown(response)

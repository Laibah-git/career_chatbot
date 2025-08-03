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
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"API error: {e}")
        return "Sorry, something went wrong. Please try again."

st.set_page_config(page_title="Career Chatbot", page_icon="🎓", layout="centered")
st.title("🎓 Career Path Chatbot")
st.markdown("**Created by Laiba Hassan**")
st.write("Enter your details and get career advice.")

# Form to collect user info
with st.form("user_form"):
    name = st.text_input("Your Name").strip()
    # clean common prefixes
    if name.lower().startswith("i am "):
        name = name[5:]
    elif name.lower().startswith("my name is "):
        name = name[11:]

    academic_interest = st.text_area("Academic Interests")
    career_goals = st.text_area("Career Goals")
    skills = st.text_area("Skills (technical, communication, etc.)")
    submitted = st.form_submit_button("Start")

if submitted:
    if not name:
        st.error("Name is required.")
    else:
        system_prompt = {
            "role": "system",
            "content": (
                "You are a friendly career counselling chatbot. "
                f"The user's name is {name}. "
                f"They have these interests: {academic_interest}. "
                f"Their goals are: {career_goals}. "
                f"They have these skills: {skills}. "
                "Never say 'I am <name>' or repeat the user's name as if you are them. "
                "Always start your first message with: 'Hey, I’m your career counselling chatbot. How can I help you today?' "
                "Then give warm, actionable advice based on their details."
            )
        }
        st.session_state.messages = [system_prompt]
        with st.spinner("Fetching advice..."):
            reply = get_career_advice(st.session_state.messages)

        # Guarantee intro at start if model didn’t include it
        intro = "Hey, I’m your career counselling chatbot. How can I help you today?"
        if not reply.lower().startswith("hey, i’m your career counselling chatbot"):
            reply = intro + "\n\n" + reply

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").markdown(reply)

if "messages" in st.session_state:
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Ask another question?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            response = get_career_advice(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("user").markdown(prompt)
        st.chat_message("assistant").markdown(response)

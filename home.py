
import streamlit as st
import os
from dotenv import load_dotenv
import time
from PIL import Image
from openai_utils import create_thread, get_answer 

load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
max_tokens = os.getenv('OPENAI_MAX_TOKENS', 250)

time_delay = os.getenv('OPENAI_TIME_DELAY', 0.1)


im = Image.open("imgs/icev_logo.png")
logo = Image.open("imgs/logo2.png")
st.set_page_config(page_title="Chat Bot iCEV", 
                   page_icon=im, 
                   layout="wide")


def main_page():
    col1, col2 = st.columns([.1, .9])
    col1.image(logo, width=180) 
    col2.header('iCEV Chatbot', divider=True)
    
    if not 'messages' in st.session_state:
        st.session_state.messages = []
    
    if not 'thread' in st.session_state:
        st.session_state.thread = create_thread()
    
    messages = st.session_state['messages']
    
    if len(messages) == 0:
        messages = [
            {
                "role": "assistant",
                "content": "Olá! Sou Athena, o Chatbot do iCEV. Qual é seu nome e como posso te ajudar?"
            }
        ]
    
    for msg in messages:
        chat = st.chat_message(msg['role'])
        chat.markdown(msg['content'])
        
    prompt = st.chat_input("Pergunte algo, meu caro!")
    
    if prompt:
        new_message = {
            "role": "user",
            "content": prompt
        }
        chat = st.chat_message(new_message['role'])
        chat.markdown(new_message['content'])
        messages.append(new_message)
        
        chat = st.chat_message('assistant')
        full_response, thread = get_answer(prompt, chat)
        
        new_message = {'role': 'assistant',
                         'content': full_response}
        messages.append(new_message)
        st.session_state['messages'] = messages
        st.session_state['thread'] = thread

main_page()
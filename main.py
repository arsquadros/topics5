from app.experts.agent_churn.churn_agent import churn_agent
from app.utils import utils

import os
import pdfkit
import re

from dotenv import load_dotenv

import streamlit as st
from streamlit_chat import message


def get_pdf_file_content(pdf_file_path) -> (bytes | str):
    if os.path.exists(pdf_file_path):
        with open(pdf_file_path, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
    else:
        PDFbyte = ""
    return PDFbyte


pdf_bytes = bytes([0])
config = {"configurable": {"thread_id": "abc123"}}

load_dotenv()

response_container = st.container()
container = st.container()

if "message_counter" not in st.session_state:
    st.session_state["message_counter"] = 0
if "person_messages" not in st.session_state:
    st.session_state["person_messages"] = []
if "agent_messages" not in st.session_state:
    st.session_state["agent_messages"] = []

if "authentication" not in st.session_state:
    st.session_state["authentication"] = ""
if "email" not in st.session_state:
    st.session_state["email"] = ""
if "password" not in st.session_state:
    st.session_state["password"] = ""

with container:
    with st.form(key="chat_form", clear_on_submit=True):
        # Ajuste nos rótulos exibidos ao usuário
        text = "Digite sua mensagem."
        placeholder = "Digite o texto aqui..."

        user_input = st.text_input(text, placeholder=placeholder, key="input")
        submit_button = st.form_submit_button(label="Enviar")
        
        st.session_state["message_counter"] += 2
        config = {"configurable": {"thread_id": f"thread_{st.session_state['message_counter']}"}}

        if submit_button:

            try:
                if st.session_state["authentication"] == "":
                    input_content = {"messages": [{"role": "user", "content": "Olá, por favor me passe meu e-mail corporativo, a corversa só poderá começar assim que estiver autenticado."}]}
                    st.session_state["authentication"] = "asking_email"
                elif st.session_state["authentication"] == "asking_email":
                    st.session_state["email"] = user_input if utils.validate_email(user_input) else ""

                    if st.session_state["email"] == "":
                        input_content = {"messages": [{"role": "user", "content": "E-mail inválido. Por favor verifique o e-mail e envie-o novamente."}]}
                    else:
                        st.session_state["authentication"] = "asking_password"
                        input_content = {"messages": [{"role": "user", "content": "E-mail validado. Por favor digite sua senha."}]}
                
                elif st.session_state["authentication"] == "asking_password":
                    st.session_state["password"] = user_input if utils.validate_password(st.session_state["email"], user_input) else ""

                    if st.session_state["password"] == "":
                        input_content = {"messages": [{"role": "user", "content": "Senha inválida. Por favor tente novamente."}]}
                    else:
                        st.session_state["authentication"] = "authenticated"
                        input_content = {"messages": [{"role": "user", "content": "Validado com sucesso. Como posso ajudar?"}]}
                elif st.session_state["authentication"] == "authenticated":
                    input_content = {"messages": [{"role": "user", "content": user_input}]}

                result = churn_agent.invoke(input=input_content, config=config)

                st.write(result["messages"][-1].content)
                if "<html>" in result["messages"][-1].content:
                    match = re.search(r"<html>(.*?)</html>", result["messages"][-1].content, re.DOTALL)
                    
                    document = None
                    if match:
                        document = match.group(1)  # Return the content inside the tags
                    
                    if document:
                        pdf_bytes = pdfkit.from_string(document)
                    
                    st.write(document)

                st.session_state.person_messages.append(user_input)
                st.session_state.agent_messages.append(result["messages"][-1].content)
            except Exception as e:
                st.error(f"Erro ao processar a mensagem. Por favor, tente novamente. {e}")
                st.stop()

#if type(pdf_bytes) != str:
st.download_button(
    label="Baixar Relatório",
    data=pdf_bytes,
    file_name="report.pdf", # Optional: Set the download filename
    mime="application/pdf",
)

with response_container:
    if st.session_state["agent_messages"]:
        for i in range(len(st.session_state["agent_messages"])):
            message(
                st.session_state["person_messages"][i], 
                is_user=True, 
                key=f"{i}_user", 
                avatar_style="big-smile"
            )
            message(
                st.session_state["agent_messages"][i],
                key=f"{i}_agent", 
                avatar_style="thumbs"
            )
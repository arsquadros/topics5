from app.supervisor.supervisor import supervisor
from app.experts.agent_churn.churn_agent import churn_agent

import streamlit as st
from streamlit_chat import message

from dotenv import load_dotenv
from uuid import uuid4

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

import os

load_dotenv()

#independent_model = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
independent_model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

load_dotenv()

config = {"configurable": {"thread_id": "abc123"}}

response_container = st.container()
container = st.container()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "person_messages" not in st.session_state:
    st.session_state["person_messages"] = []
if "agent_messages" not in st.session_state:
    st.session_state["agent_messages"] = []
if "email_asked" not in st.session_state:
    st.session_state["email_asked"] = False

with container:
    with st.form(key="chat_form", clear_on_submit=True):
        # Ajuste nos rótulos exibidos ao usuário
        text = "Digite sua mensagem."
        placeholder = "Digite o texto aqui..."

        user_input = st.text_input(text, placeholder=placeholder, key="input")
        submit_button = st.form_submit_button(label="Enviar")
        
        config = {"configurable": {"thread_id": f"{uuid4()}"}}

        if submit_button:
            if not st.session_state["authenticated"] and not st.session_state["email_asked"]:
                try:
                    input_content = {"messages": [{"role": "user", "content": "Usuário não autenticado. Peça pelo e-mail corporativo e para enviar a mensagem novamente depois de autenticado."}]}

                    result = churn_agent.invoke(input_content)

                    st.session_state["email_asked"] = True

                    st.session_state.person_messages.append(user_input)
                    st.session_state.agent_messages.append(result["messages"][-1].content)

                except Exception as e:
                    st.error(f"Erro ao processar a mensagem. Por favor, tente novamente. {e}")
                    st.stop()
            elif not st.session_state["authenticated"] and st.session_state["email_asked"]:
                try:
                    input_content = {"messages": [{"role": "user", "content": f"E-mail: {user_input}"}]}

                    result = churn_agent.invoke(input_content)

                    authentication = independent_model.invoke(f"Responda somente \"True\" se a mensagem é de sucesso, ou somente \"False\" se a mensagem indica uma falha. Mensagem: {result['messages'][-1].content}").content.strip()
                    
                    st.session_state["authenticated"] = True

                    st.session_state.person_messages.append(user_input)
                    st.session_state.agent_messages.append(result["messages"][-1].content)

                except Exception as e:
                    st.error(f"Erro ao processar a mensagem. Por favor, tente novamente. {e}")
                    st.stop()
            else:
                try:
                    input_content = {"messages": [{"role": "user", "content": f"Responda a seguinte requisição: {user_input}"}]}

                    result = churn_agent.invoke(input_content)

                    st.session_state.person_messages.append(user_input)
                    st.session_state.agent_messages.append(result["messages"][-1].content)

                except Exception as e:
                    st.error(f"Erro ao processar a mensagem. Por favor, tente novamente. {e}")
                    st.stop()
            

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

if len(os.listdir("app/tmp")) != 1:
    st.download_button(
        label="Baixar último relatório",
        data=open(f"app/tmp/report.pdf", "rb").read(),
        file_name=f"{uuid4()}.pdf",
        mime="application/pdf"
    )

    os.remove("app/tmp/report.pdf")
    
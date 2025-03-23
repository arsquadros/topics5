# Agente supervisor que gerencia os agentes especialistas
# Esse template é bem simples. Ele é apenas um supervisor direto de 3 agentes especialistas.

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor

from app.experts.agent_churn.churn_agent import churn_agent
from app.supervisor.tools import validate_user_tool

import logging
import os
from dotenv import load_dotenv

logging.basicConfig(filename="app/logs/logs.log", level=logging.INFO)
load_dotenv()

logging.info("Loading OpenAI model...")

#model = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

logging.info("Creating supervisor...")

supervisor = create_supervisor(
    [churn_agent],  # lista de agentes
    model=model,  # modelo de linguagem
    tools=[validate_user_tool()],
    prompt=open("app/supervisor/prompt.yaml", "r").read(),  # prompt em texto a ser passado para o supervisor. Deve ter um texto indicando os agentes disponíveis.
    output_mode="last_message"  # "last_message" ou "full_history"  # "full_history" aumenta muito a quantidade de tokens de input
).compile()

logging.info("Supervisor created successfully!")

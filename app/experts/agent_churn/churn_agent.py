from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

import logging
import os

from app.experts.agent_churn.tools import generate_report_tool, suggest_action_plan_tool, validate_user_tool

from langchain.chains import ConversationalRetrievalChain

from app.vectors.vector_store import init_vector_database

from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os

logging.basicConfig(filename="app/logs/logs.log", level=logging.INFO)

load_dotenv()

logging.info("Loading OpenAI model for churn_agent...")

#model = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
model = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

_r = init_vector_database(
    "app/faiss_store",
    "app/experts/agent_churn/documents/RAG").as_retriever(
            search_type="mmr",
            search_kwargs={"fetch_k": 1, "k": 1, "lambda_mult": 0.3}
        )

_chain = ConversationalRetrievalChain.from_llm(llm=model, retriever=_r, return_source_documents=True)

tools = [
    generate_report_tool(_chain),
    suggest_action_plan_tool(_chain),
    validate_user_tool(_chain)
]

logging.info("Creating churn_agent...")

churn_agent = create_react_agent(
    model=model,  # modelo de linguagem que o agente vai usar
    tools=tools,  # lista de funções que o agente pode executar
    name="churn_expert",  # nome do agente (deve ser único)
    prompt=open("app/experts/agent_churn/prompt.yaml", "r").read()  # prompt que o agente vai usar
)

logging.info("churn_agent created successfully!")

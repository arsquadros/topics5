from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
import pandas as pd

import os

from dotenv import load_dotenv

import logging

logging.basicConfig(filename="app/logs/logs.log", level=logging.INFO)

load_dotenv()

logging.info("Loading OpenAI model for agent...")

class ValidateUserSchema(BaseModel):
    email: str = Field(..., title="E-mail", description="E-mail corporativo a ser validado.")


def validate_user_tool(conversation_chain=None) -> StructuredTool:
    """Valida um e-mail corporativo antes de responder a qualquer mensagem"""

    def _run(email: str) -> str:
        logging.info(f"Function validate_user_tool called with email={email} on agent.")
        try:
            found = False

            df = pd.read_csv("app/supervisor/documents/usuarios_chatbot.csv")
            
            for e in df["E-mail"].tolist():
                if e == email:
                    found = True
                    break
        except Exception as e:
            logging.error(f"ERROR: could not validate email '{email}'. Error '{e}' Returning default answer.")
            found = False
        else:
            logging.info(f"Validação de e-mail: {found}")
        return f"Status: {found}."

    return StructuredTool(
        name="validate_user_tool",
        description="""
        Valida o usuário caso não esteja autenticado para uso. Recebe um e-mail e busca no banco para verificar se existe.
        """,
        args_schema=ValidateUserSchema,
        func=_run
    )

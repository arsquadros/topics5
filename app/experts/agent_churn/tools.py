from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
import pandas as pd
import pdfkit

import os
from uuid import uuid4

from dotenv import load_dotenv

import logging

logging.basicConfig(filename="app/logs/logs.log", level=logging.INFO)

load_dotenv()

logging.info("Loading OpenAI model for agent...")




class GenerateReportTool(BaseModel):
    query: str = Field(..., title="Query", description="Query para se gerar um relatório.")


def generate_report_tool(conversation_chain) -> StructuredTool:
    """Gera um relatório de retenção de clientes a partir de uma query."""

    def _run(query: str) -> str:
        logging.info(f"Function generate_report_tool called with query={query} on agent.")
        result = "Error"
        name = "Error"
        try:
            data = ""
            for i, file in enumerate(["acoes_retencao", "dados_clientes_consultoria", "interacoes_clientes"]):
                print(f"i - file: {i} - {file}")
                data += f"[begin file {i + 1}]\n\n"
                data += open(f"app/experts/agent_churn/documents/{file}.csv", "r").read()
                data += f"\n\n[end file {i + 1}]"
            print("Read all files")
            message = f"""
                Gere um relatório para a query a seguir a partir dos dados que serão passados no final.
                Os dados são em formato CSV, e o relatório deve ser gerado em HTML semântico.
                A resposta deve conter SOMENTE o HTML, pois será colocado diretamente em um gerador de PDFs.
                Evite tabelas com um número muito grande de colunas, pois isso pode quebrar o layout do PDF.
                Não podem haver classes ou ids para estilização. O conteúdo deve ser somente o que estaria dentro da tag <body>, por exemplo:

                [BEGIN EXAMPLE]
                
                <h1>Relatório de Exemplo</h1>
                <p>Este é um parágrafo de exemplo em um relatório gerado como PDF.</p>
                <p>Aqui está mais algum texto para preencher o conteúdo.</p>
                <table>
                    <thead>
                        <tr>
                            <th>Nome</th>
                            <th>Idade</th>
                            <th>Cidade</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>João</td>
                            <td>30</td>
                            <td>São Paulo</td>
                        </tr>
                        <tr>
                            <td>Maria</td>
                            <td>25</td>
                            <td>Rio de Janeiro</td>
                        </tr>
                        <tr>
                            <td>Carlos</td>
                            <td>35</td>
                            <td>Belo Horizonte</td>
                        </tr>
                    </tbody>
                </table>
                <p>Você pode adicionar mais conteúdo e tabelas conforme necessário.</p>
                <footer>
                    Este relatório foi gerado automaticamente.
                </footer>

                [END EXAMPLE]
                
                [BEGIN QUERY]
                {query}
                [END QUERY]

                [BEGIN DATA]
                {data}
                [END DATA]
            """.replace("\t", "")
            result = conversation_chain.invoke({"question": message, "chat_history": []})["answer"]
            result = result.replace("```html\n", "").replace("```", "")
            name = "report.pdf"

            html = open("app/layout/template_layout_report", "r").read().replace("[INSERT]", result)

            res = pdfkit.from_string(html, f"app/tmp/{name}")
            if type(res) == bool:
                name = "Error"
        except Exception as e:
            logging.error(f"ERROR: could generate report for query '{query}'. Error '{e}' Returning default answer.")
        else:
            logging.info(f"Resposta de relatório da query '{query}': {result}")
        return f"Report written in file named: '{name}'." if name != "Error" else f"Report could not be written."

    return StructuredTool(
        name="generate_report_tool",
        description="Gera um relatório de retenção de clientes a partir de uma query.",
        args_schema=GenerateReportTool,
        func=_run
    )

class SuggestActionPlanSchema(BaseModel):
    query: str = Field(..., title="Query", description="Query pedindo plano de ação sob algum contexto.")


def suggest_action_plan_tool(conversation_chain) -> StructuredTool:
    """Sugere um plano de retenção de clientes baseado na query."""

    def _run(query: str) -> str:
        logging.info(f"Function generate_report_tool called with query={query} on agent.")
        result = "Error"
        try:
            data = ""
            for i, file in enumerate(["acoes_retencao", "dados_clientes_consultoria", "interacoes_clientes"]):
                data += f"[begin file {i + 1}]\n\n"
                data += open(f"app/experts/agent_churn/documents/{file}.csv", "r").read()
                data += f"\n\n[end file {i + 1}]"
            message = f"""
                Gere um plano de ação estruturado para a seguinte query e os dados passados no final.
                Acesse os descritores de serviços da empresa se necessário.

                [BEGIN QUERY]
                {query}
                [END QUERY]

                [BEGIN DATA]
                {data}
                [END DATA]
            """.replace("\t", "")
            result = conversation_chain.invoke({"question": message, "chat_history": []})
        except Exception as e:
            logging.error(f"ERROR: could generate report for query '{query}'. Error '{e}' Returning default answer.")
        else:
            logging.info(f"Resposta de relatório da query '{query}': {result}")
        return result

    return StructuredTool(
        name="suggest_action_plan_tool",
        description="Sugere um plano de retenção de clientes baseado na query.",
        args_schema=SuggestActionPlanSchema,
        func=_run
    )

class ValidateUserSchema(BaseModel):
    email: str = Field(..., title="E-mail", description="E-mail corporativo a ser validado.")


def validate_user_tool(conversation_chain=None) -> StructuredTool:
    """Valida um e-mail corporativo antes de responder a qualquer mensagem"""

    def _run(email: str) -> str:
        logging.info(f"Function validate_user_tool called with email={email} on agent.")
        try:
            found = False
            print("Accessing filepath")
            df = pd.read_csv("app/experts/agent_churn/documents/usuarios_chatbot.csv")
            print("Accessed filepath")
            
            for e in df["E-mail"].tolist():
                if e == email:
                    found = True
                    break
            print("Status finding user:", found)
        except Exception as e:
            logging.error(f"ERROR: could not validate email '{email}'. Error '{e}' Returning default answer.")
            print("Error finding user")
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

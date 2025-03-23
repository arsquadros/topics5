import os
import logging

from typing import List

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from app.vectors.loader import load_and_process_pdfs

logging.basicConfig(filename="app/logs/logs.log", level=logging.INFO)


def build_vectorstore(docs: List[Document], store_path: str = "app/faiss_store") -> FAISS:
    embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embedder = HuggingFaceEmbeddings(model_name=embedding_model_name)

    os.makedirs(store_path, exist_ok=True)

    if os.path.isdir(store_path) and os.listdir(store_path):
        logging.info(f"Loading FAISS in '{store_path}'.")
        vectorstore = FAISS.load_local(store_path, embedder)
        logging.info("Successfully loaded FAISS store.")
    else:
        logging.info("FAISS store not found. Creating new store...")
        vectorstore = FAISS.from_documents(docs, embedder)
        logging.info("Novo índice FAISS criado com sucesso.")
        vectorstore.save_local(store_path)
        logging.info(f"FAISS store saved to '{store_path}'.")

    return vectorstore

def init_vector_database(index_path: str, docs_path: str = "app/experts/agent_churn/documents/RAG") -> FAISS:
    if not index_path:
        raise ValueError("'index_path' needs to be a valid path to the FAISS index. Each agent should have its own index.")

    store_path = index_path

    # Certifica-se de que o diretório para PDFs existe
    if not os.path.exists(docs_path):
        logging.warning(f"Directory '{docs_path}' not found. Creating directory...")
        os.makedirs(docs_path, exist_ok=True)
        logging.warning(f"Directory '{docs_path}' should not be empty. Please add PDFs to the directory.")
        return None

    # Certifica-se de que o diretório para o índice FAISS existe
    os.makedirs(store_path, exist_ok=True)

    # Verifica se o índice FAISS existe e o carrega
    if os.path.exists(index_path) and os.listdir(store_path):
        logging.info(f"Loading FAISS in '{store_path}'.")
        vectorstore = FAISS.load_local(
            store_path,
            embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
            allow_dangerous_deserialization=True
        )
        return vectorstore

    # Cria uma nova base vetorial se não existir
    logging.info("Building new FAISS index...")
    try:
        docs = load_and_process_pdfs(docs_path)
        if not docs:
            logging.error(f"No PDFs found in '{docs_path}'. Please add PDFs to the directory.")
            return None

        return build_vectorstore(docs, store_path=store_path)
    except FileNotFoundError as e:
        logging.error(f"Error loading PDFs: {e}")
        return None
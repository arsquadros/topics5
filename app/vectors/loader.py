# pdf_loader.py

import os
import logging
from typing import List, Iterator

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from docling.document_converter import DocumentConverter

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DoclingPDFLoader(BaseLoader):
    """
    Loader para ler um ou mais PDFs e convertê-los em texto
    via Docling, gerando objetos do tipo LCDocument.
    """

    def __init__(self, file_paths: List[str]) -> None:
        self._file_paths = file_paths
        self._converter = DocumentConverter()

    def lazy_load(self) -> Iterator[LCDocument]:
        """
        Faz a leitura de cada arquivo PDF via Docling
        e retorna objetos LCDocument a cada iteração.
        """
        for source in self._file_paths:
            logger.info(f"Processando PDF: {source}")
            dl_doc = self._converter.convert(source).document
            text = dl_doc.export_to_markdown()
            logger.info(f"PDF convertido para texto: {source}")
            yield LCDocument(page_content=text, metadata={"source": source})

def load_and_process_pdfs(directory: str):
    """
    Carrega todos os PDFs do diretório especificado,
    converte em texto usando Docling, e faz o split em chunks.
    """
    logger.info(f"Carregando PDFs do diretório: {directory}")
    pdf_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.pdf')]

    if not pdf_files:
        logger.error("Nenhum arquivo PDF encontrado no diretório.")
        raise FileNotFoundError(f"Nenhum arquivo PDF encontrado no diretório {directory}.")

    logger.info(f"{len(pdf_files)} arquivos PDF encontrados.")
    loader = DoclingPDFLoader(file_paths=pdf_files)
    logger.info("Convertendo PDFs para texto...")
    docs = loader.lazy_load()
    logger.info("Dividindo os documentos em chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    logger.info(f"Divisão concluída. {len(chunks)} chunks gerados.")
    return chunks
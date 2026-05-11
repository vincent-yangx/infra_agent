# tools/faiss_retriever.py

from functools import lru_cache
from typing import Any

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from tools.file_readers import read_text_file


DEFAULT_KB_FILE = "kb_docs.txt"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def load_kb_as_documents(kb_file_name: str = DEFAULT_KB_FILE) -> list[Document]:
    """
    Load the knowledge base text file and split it into chunks.

    Each chunk becomes a LangChain Document with metadata.
    """

    raw_text = read_text_file(kb_file_name)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = text_splitter.split_text(raw_text)

    documents = []
    for idx, chunk in enumerate(chunks):
        clean_chunk = chunk.strip()

        if not clean_chunk:
            continue

        documents.append(
            Document(
                page_content=clean_chunk,
                metadata={
                    "source": kb_file_name,
                    "chunk_id": idx,
                },
            )
        )

    return documents


@lru_cache(maxsize=1)
def build_faiss_vectorstore(
    kb_file_name: str = DEFAULT_KB_FILE,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> FAISS:
    """
    Build a FAISS vector store from the knowledge base.

    The result is cached so the index is not rebuilt on every retrieval call
    within the same Python process.
    """

    documents = load_kb_as_documents(kb_file_name)

    if not documents:
        raise ValueError(f"No valid documents found in knowledge base: {kb_file_name}")

    embeddings = OpenAIEmbeddings(model=embedding_model)

    vectorstore = FAISS.from_documents(
        documents=documents,
        embedding=embeddings,
    )

    return vectorstore


def retrieve_docs_with_scores(
    query: str,
    top_k: int = 3,
    kb_file_name: str = DEFAULT_KB_FILE,
) -> list[dict[str, Any]]:
    """
    Retrieve top-k relevant knowledge base chunks with FAISS similarity search.

    Note:
    FAISS scores returned by LangChain are distance-like scores.
    Lower score usually means more similar.
    """

    if not query or not query.strip():
        raise ValueError("Retrieval query cannot be empty.")

    vectorstore = build_faiss_vectorstore(kb_file_name)

    results = vectorstore.similarity_search_with_score(
        query=query,
        k=top_k,
    )

    retrieved = []

    for doc, score in results:
        retrieved.append(
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", kb_file_name),
                "chunk_id": doc.metadata.get("chunk_id"),
                "score": float(score),
            }
        )

    return retrieved


def retrieve_docs(
    query: str,
    top_k: int = 3,
    kb_file_name: str = DEFAULT_KB_FILE,
) -> list[str]:
    """
    Retrieve top-k relevant knowledge base chunks as formatted strings.

    This is the simpler function that RAG Agent can call directly.
    """

    results = retrieve_docs_with_scores(
        query=query,
        top_k=top_k,
        kb_file_name=kb_file_name,
    )

    formatted_docs = []

    for item in results:
        formatted_docs.append(
            (
                f"[Source: {item['source']} | Chunk: {item['chunk_id']} | "
                f"Score: {item['score']:.4f}]\n"
                f"{item['content']}"
            )
        )

    return formatted_docs
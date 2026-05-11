from dotenv import load_dotenv
load_dotenv(override=True)

from tools.faiss_retriever import retrieve_docs

query = (
    "database query timeout high CPU active locks "
    "monthly finance batch job connection pool pressure"
)

docs = retrieve_docs(query, top_k=3)

for i, doc in enumerate(docs, start=1):
    print(f"\n--- Retrieved Doc {i} ---")
    print(doc)
import os
from langchain_ollama import OllamaEmbeddings
# This is the older version of Chroma to be deprecated, but the only one to work with numpy > 2.0.0 currently
from langchain_community.vectorstores import Chroma
# from langchain_chroma import Chroma

CHROMA_PATH = os.getenv('CHROMA_PATH', './chroma')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'LangFlask')
TEXT_EMBEDDING_MODEL = os.getenv('TEXT_EMBEDDING_MODEL', 'mxbai-embed-large')

def get_vector_db():
    embedding = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL,show_progress=True)

    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
        embedding_function=embedding
    )

    return db
# Need documentation for this file

import os
from langchain_ollama import OllamaEmbeddings
# This is the older version of Chroma to be deprecated, but the only one to work with numpy > 2.0.0 currently
#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

#Directory where the ChromaDB is stored
CHROMA_PATH = os.getenv('CHROMA_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chroma'))
#Names the collection
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'LangFlask')
#Names the chuncked collection
COLLECTION_NAME_CHUNKED = os.getenv('COLLECTION_CHUNKED_NAME', 'Chunked')
#Declares which text embedding model we are going to use
TEXT_EMBEDDING_MODEL = os.getenv('TEXT_EMBEDDING_MODEL', 'shaw/dmeta-embedding-zh')

#This function gets the DB for future use
def get_vector_db():
    embedding = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL)

    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
        embedding_function=embedding
    )

    return db

#This function gets the chunked DB for future use
def get_chunked_db():
    embedding = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL)

    db = Chroma(
        collection_name=COLLECTION_NAME_CHUNKED,
        persist_directory=CHROMA_PATH,
        embedding_function=embedding
    )

    return db
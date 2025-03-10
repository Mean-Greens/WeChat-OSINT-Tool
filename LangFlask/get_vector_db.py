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
    """
    Initializes and returns a Chroma vector database instance.

    This function creates an instance of `Chroma` with the specified collection name and 
    persistence directory. It also initializes the `OllamaEmbeddings` model `shaw/dmeta-embedding-zh` for embedding 
    text data.

    Returns:
        Chroma: A Chroma vector database instance configured with the specified settings.

    Raises:
        Exception: If there is an issue initializing the embedding model or database.
    """
    embedding = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL)

    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
        embedding_function=embedding
    )

    return db

#This function gets the chunked DB for future use
def get_chunked_db():
    """
    Initializes and returns a Chroma vector database instance for chunked data.

    This function sets up a `Chroma` database using the specified collection name 
    for chunked data storage. It also initializes the `OllamaEmbeddings` model `shaw/dmeta-embedding-zh` to 
    generate text embeddings.

    Returns:
        Chroma: A Chroma vector database instance configured for chunked data.

    Raises:
        Exception: If there is an issue initializing the embedding model or database.
    """
    embedding = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL)

    db = Chroma(
        collection_name=COLLECTION_NAME_CHUNKED,
        persist_directory=CHROMA_PATH,
        embedding_function=embedding
    )

    return db
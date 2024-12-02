from langchain.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import BSHTMLLoader
from langchain.embeddings.openai import OpenAIEmbeddings
import os
from getpass import getpass

OPENAI_API_KEY = getpass()

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

embeddings = OpenAIEmbeddings()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
persist_directory = "ChromaDB/db"
db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# -------------------------- Adding spacex_wiki.txt -------------------------- #
loader = BSHTMLLoader("./test.htm")
documents = loader.load()
print(documents)

# loader = TextLoader("this_has_to_work/spacex_wiki.txt", encoding="utf8")
# documents = loader.load()
docs = text_splitter.split_documents(documents)
db.add_documents(docs)

db.persist()

# --------------------------- querying the vectordb -------------------------- #
db = None

db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

retriever = db.as_retriever(search_type="mmr")

query = "What is implosion?"
print(query)
print(retriever.get_relevant_documents(query)[0])
print("\n\n")

query = "Who is elon?"
print(query)
print(retriever.get_relevant_documents(query)[0])
print("\n\n")


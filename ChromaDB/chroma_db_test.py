import os
import ollama
import chromadb

'''
pip install ollama chromadb
'''

# Get the directory path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the 'db' folder to the directory path
db_path = os.path.join(current_dir, 'db')

client = chromadb.PersistentClient(path=db_path)

collection = client.get_or_create_collection(name="test")

if collection.count() == 0:

    documents = [
    "Llamas are members of the camelid family meaning they're pretty closely related to vicuñas and camels",
    "Llamas were first domesticated and used as pack animals 4,000 to 5,000 years ago in the Peruvian highlands",
    "Llamas can grow as much as 6 feet tall though the average llama between 5 feet 6 inches and 5 feet 9 inches tall",
    "Llamas weigh between 280 and 450 pounds and can carry 25 to 30 percent of their body weight",
    "Llamas are vegetarians and have very efficient digestive systems",
    "Llamas live to be about 20 years old, though some only live for 15 years and others live to be 30 years old",
    ]
    
    # store each document in a vector embedding database
    for i, d in enumerate(documents):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
        embedding = response["embedding"]
        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            metadatas=[{"source": f'test{i}'}],
            documents=[d]
        )

#------------------------------------------------------ Find how many articles are in the database ------------------------------------------------------#
# print(collection.count())
# print()

# an example prompt
prompt = "How long do llamas live?"

# generate an embedding for the prompt and retrieve the most relevant doc
response = ollama.embeddings(
  model="mxbai-embed-large",
  prompt=prompt
)
results = collection.query(
  query_embeddings=[response["embedding"]],
  n_results=1
)
data = results['documents']
 
# Add some code to send data to the LLM we chose to parse data with. 

print(data)

# Need documentation for this file

import os
import sys
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_vector_db import get_vector_db, get_chunked_db

LLM_MODEL = os.getenv('LLM_MODEL', 'aya-expanse:32b')

# Function to get the prompt templates for generating alternative questions and answering based on context
def get_prompt():
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to tanslate the given user question below into Traditional Chinese and generate five
        different versions of the given user question in Traditional Chinese to retrieve relevant documents from
        a vector database of WeChat articles written in Chinese. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}""",
    )


    template = """Ignore all previous instructions. You are an AI assistant that specializes in OSINT. You must respond ONLY in English. 

    You MUST answer the question **ONLY** using the information from the provided context. **Do not use outside knowledge.** If the context does not contain relevant information to answer the question, follow these steps:

    1. Clearly state: *"I cannot find any useful information in the provided documents."*
    2. Provide **exactly five** search terms the user could use in a search engine to find relevant answers.

    **Context:**
    {context}

    **Question:** {question}

    **Important Rules:**
    - If the answer is in the context, provide a direct answer using ONLY that information.
    - If the answer is NOT in the context, DO NOT GUESS. DO NOT provide external knowledge.
    - If needed, list **exactly five** search terms for further research.
    """

    #Answer the question based ONLY on the following context:

    prompt = ChatPromptTemplate.from_template(template)

    return QUERY_PROMPT, prompt

# Main function to handle the query process
def query(input):

    if input:
        # Initialize the language model with the specified model name
        llm = ChatOllama(model=LLM_MODEL)
        # Get the vector database instance
        db = get_chunked_db()
        # Get the prompt templates
        QUERY_PROMPT, prompt = get_prompt()

        # Set up the retriever to generate multiple queries using the language model and the query prompt
        retriever = MultiQueryRetriever.from_llm(
            db.as_retriever(), 
            llm,
            prompt=QUERY_PROMPT
        )
        
        output = db.as_retriever(search_kwargs={'k': 5})
        
        translated_input = query_translation(input)
        print(translated_input)
        docs = output.invoke(translated_input)
        
        for doc in docs:
            print(doc.metadata.get('hash'))
            print(doc.metadata.get('title'))

        # quit()

        # all_documents = db._collection.get(include=["metadatas", "documents"])

        # # Print hash and page content for each document
        # for metadata, page_content in zip(all_documents["metadatas"], all_documents["documents"]):
        #     hash_value = metadata.get("hash", "No hash found")
        #     title = metadata.get("title", "NO title")
        #     print(f"Hash: {hash_value}")
        #     print(f"Title: {title}")
        #     print(f"Page Content: {page_content}")
        #     print("-" * 50)  # Separator for readability

        # quit()

        # Define the processing chain to retrieve context, generate the answer, and parse the output
        chain = (
            {"context": output, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        response = chain.invoke(input)
        
        return response

    return None

# Main function to handle the query process
def query_translation(input):

    if input:
        # Initialize the language model with the specified model name
        llm = ChatOllama(model=LLM_MODEL)

        response = llm.invoke(f"translate the following word or phrase for me. I would like it translated to chinese (traditional). The word or phrase is '{input}'. please only return the translation and nothing else")
        
        return response.content

    return None

if __name__ == "__main__":
    print(query_translation("test"))
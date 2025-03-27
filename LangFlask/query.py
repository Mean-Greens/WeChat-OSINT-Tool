# Need documentation for this file

import os
import sys
import datetime
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_vector_db import get_vector_db, get_chunked_db

LLM_MODEL = os.getenv('LLM_MODEL', 'aya-expanse:32b')
#LLM_MODEL = 'deepseek-r1:32b'

# Function to get the prompt templates for generating alternative questions and answering based on context
# This gives the LLM a kind of base behavior to work off of. 
def get_prompt():
    """
    Generates two different prompt templates for language processing tasks.

    Returns:
        tuple: A tuple containing two prompt templates:
            - QUERY_PROMPT (PromptTemplate): A template designed to translate a given 
              user question into Traditional Chinese and generate five different 
              variations of the question. These variations help retrieve relevant 
              documents from a WeChat article vector database.
            - prompt (ChatPromptTemplate): A template designed for OSINT (Open-Source 
              Intelligence) tasks. It ensures responses are provided strictly in English 
              using only the given context. If no relevant information is found in the 
              context, it returns five recommended search terms.

    The function defines two templates:
        1. QUERY_PROMPT: Helps generate multiple variations of a question in 
           Traditional Chinese for better document retrieval.
        2. prompt: An OSINT-focused template that ensures strict adherence to provided 
           context and prevents speculation or external knowledge use.
    """
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

    You MUST answer the question **ONLY** using the information from the provided context. **Do not use outside knowledge.** Provide any information from the context that would be meaningful to an OSINT professional.
    
    If the context does not contain relevant information to answer the question, follow steps 1 and 2:
    1. Clearly state: *"I cannot find any useful information in the provided documents."*
    2. Provide **exactly five** search terms the user could use in a search engine to find relevant answers.

    **Context:**
    {context}

    **Question:** {question}

    **Important Rules:**
    - Answer **ONLY** in English
    - If the answer is in the context, provide an answer using ONLY that information.
    - If the answer is NOT in the context, DO NOT GUESS. DO NOT provide external knowledge.
    """

    #Answer the question based ONLY on the following context:

    prompt = ChatPromptTemplate.from_template(template)

    return QUERY_PROMPT, prompt

# Main function to handle the query process
def query(input):
    """
    Processes a given input query by translating it, retrieving relevant documents 
    from a vector database, and generating a response using a language model.

    Args:
        input (str): The user's query.

    Returns:
        str: The generated response along with retrieved document sources, or None if no input is provided.

    Functionality:
        - Initializes the language model ('aya-expanse:32b') using Ollama.
        - Retrieves a chunked vector database instance.
        - Fetches prompt templates for query processing.
        - Translates the input query into the appropriate language.
        - Retrieves relevant documents using the vector database retriever.
        - Constructs a processing chain to generate a response based on retrieved context.
        - Extracts metadata (title, author, date, hash) from retrieved documents.
        - Returns the AI-generated response along with document sources.

    Note:
        - Uses a global `sources` variable to store and format metadata of retrieved documents.
        - The `print_docs` function formats and prints document metadata.
        - Some commented-out code suggests alternative implementations for retrieval.
    """

    if input:
        # Initialize the language model with the specified model name
        llm = ChatOllama(model=LLM_MODEL)
        # Get the vector database instance
        db = get_chunked_db()
        # Get the prompt templates
        QUERY_PROMPT, prompt = get_prompt()

        # Set up the retriever to generate multiple queries using the language model and the query prompt
        # retriever = MultiQueryRetriever.from_llm(
        #     db.as_retriever(), 
        #     llm,
        #     prompt=QUERY_PROMPT
        # )
        
        output = db.as_retriever(search_kwargs={'k': 5})
        output_full = db.as_retriever(search_kwargs={'k': 15})
        
        translated_input = query_translation(input)
        print(translated_input)
        
        # Define the processing chain to retrieve context, generate the answer, and parse the output
        chain = (
            {"context": output | (lambda docs: print_docs(docs)), "question": RunnablePassthrough()}
            #{"context": output, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )


        global sources
        sources = "\n\nSources:\n\n"

        def print_docs(docs):
            global sources
            for doc in docs:
                sources += ("Article Title: <a href=\"articles/" + doc.metadata.get('hash') +".html\" style=\"text-decoration: underline;\">" + doc.metadata.get('title') + "</a>\n")
                sources += ("   Author: " + doc.metadata.get('author') + "\n")
                sources += ("   Date: " + timeConvert(doc.metadata.get('date')) + "\n")
                sources += ("   Hash: " + doc.metadata.get('hash') + "\n\n")
            return docs

        # context_docs = output.invoke(input)
        output_full_list = output_full.invoke(translated_input)
        
        # for doc in context_docs:
        #     sources += ("Article Title: " + doc.metadata.get('title') + "\n")
        #     sources += ("   Author: " + doc.metadata.get('author') + "\n")
        #     sources += ("   Date: " + timeConvert(doc.metadata.get('date')) + "\n")
        #     sources += ("   Hash: " + doc.metadata.get('hash') + "\n\n")

        response = chain.invoke(translated_input)

        
        return response + sources

    return None


def timeConvert(unix_timestamp): 
    """
    Converts a Unix timestamp to a human-readable datetime string.

    Args:
        unix_timestamp (int or str): The Unix timestamp to convert.

    Returns:
        str: The formatted datetime string in the format 'YYYY-MM-DD HH:MM:S'.

    Functionality:
        - Converts the Unix timestamp into a `datetime` object.
        - Formats the datetime object into a string representation.

    Note:
        - The function assumes the timestamp is in seconds.
        - The input can be an integer or a string that represents an integer.
    """

    # Convert the Unix timestamp to a datetime object 
    dt = datetime.datetime.fromtimestamp(int(unix_timestamp)) 
    # Format the datetime object as a string 
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# Main function to handle the query translation process. 
def query_translation(input):
    """
    Translates a given word or phrase into Simplified Chinese using a language model.

    Args:
        input (str): The word or phrase to be translated.

    Returns:
        str: The translated text in Simplified Chinese, or None if no input is provided.

    Functionality:
        - Initializes the language model ('aya-expanse:32b') using Ollama.
        - Sends a prompt to the model requesting a Simplified Chinese translation.
        - Extracts and returns only the translated text from the model's response.

    Note:
        - Ensures the response contains only the translation with no extra text.
    """
    if input:
        # Initialize the language model with the specified model name
        llm = ChatOllama(model=LLM_MODEL)

        response = llm.invoke(f"Translate the following word or phrase for me. I would like it translated to simplified chinese. The word or phrase is '{input}'. Please only return the translation and nothing else")
        
        return response.content

    return None

if __name__ == "__main__":
    print(query_translation("test"))
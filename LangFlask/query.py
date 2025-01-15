import os
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from get_vector_db import get_vector_db

LLM_MODEL = os.getenv('LLM_MODEL', 'aya:35b')

# Function to get the prompt templates for generating alternative questions and answering based on context
def get_prompt():
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}""",
    )

    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
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
        db = get_vector_db()
        # Get the prompt templates
        QUERY_PROMPT, prompt = get_prompt()

        # Set up the retriever to generate multiple queries using the language model and the query prompt
        retriever = MultiQueryRetriever.from_llm(
            db.as_retriever(), 
            llm,
            prompt=QUERY_PROMPT
        )
        
        # output = db.as_retriever(search_kwargs={'k': 1})
        # #output = db.similarity_search_by_vector(k=1)
        # #docs = output.get_relevant_documents(input)
        # docs = output.invoke(input)
        # print(docs[0].metadata)
        # print(docs[0].id)
        # print(docs[0].page_content)
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
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        response = chain.invoke(input)
        
        return response

    return None
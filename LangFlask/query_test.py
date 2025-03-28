import os
import sys
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

from langchain import hub
from typing_extensions import List, TypedDict, Annotated
from langgraph.graph import START, StateGraph
from langchain_core.documents import Document
import json


#DOES NOT NEED TO BE DOCUMENTED, JUST FOR TESTING PURPOSES

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from get_vector_db import get_vector_db, get_chunked_db

LLM_MODEL = os.getenv('LLM_MODEL', 'aya-expanse:32b')
db = get_chunked_db()
llm = ChatOllama(model=LLM_MODEL)

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")



# Desired schema for response
class AnswerWithSources(TypedDict):
    """An answer to the question, with sources."""

    answer: str
    sources: Annotated[
        List[str],
        ...,
        "List of sources (author + year) used to answer the question",
    ]


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: AnswerWithSources


# Define application steps
def retrieve(state: State):
    """
    Retrieves documents relevant to a given question using similarity search.

    Args:
        state (State): A dictionary-like object containing a "question" key 
                       with the user's query as the value.

    Returns:
        dict: A dictionary containing the retrieved documents under the "context" key.

    Functionality:
        - Performs a similarity search on the database (`db`) using the provided question.
        - Returns the retrieved documents as context for further processing.
    """
    retrieved_docs = db.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    """
    Processes a query by combining document content and generating a structured response.

    Args:
        state (State): A dictionary-like object containing "question" and "context" keys.
                       The "context" key contains a list of documents retrieved from a database.

    Returns:
        dict: A dictionary containing the structured answer under the "answer" key.

    Functionality:
        - Combines the page content from the documents in the "context" into a single string.
        - Passes the question and combined context to the prompt for processing.
        - Uses a structured language model to generate an answer with sources.
        - Returns the answer in a structured format.

    Note:
        - Assumes `llm` is a predefined language model instance and `AnswerWithSources` is 
          a predefined structure for handling responses.
    """
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    structured_llm = llm.with_structured_output(AnswerWithSources)
    response = structured_llm.invoke(messages)
    return {"answer": response}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

result = graph.invoke({"question": "What are some good places to visit in China?"})
print(json.dumps(result["answer"], indent=2))

print(f'Context: {result["context"]}\n\n')
print(f'Answer: {result["answer"]}')
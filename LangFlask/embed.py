# Need documentation for this file

import os
from datetime import datetime
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import BSHTMLLoader
from MGHTMLLoader import MGHTMLLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from get_vector_db import get_vector_db

TEMP_FOLDER = os.getenv('TEMP_FOLDER', './_temp')

#The functions of this page behave as follows: A document is found and needs to be added to the database. 
#This document is then saved in a temporary folder on the computer, but not the database, "save_file(file)"
#The document then needs to be chunked for better use by the LLM, "load_and_split_file()"
#The document is then saved in the DB, "embed()"

# Function to check if the uploaded file is allowed (only PDF files)
def allowed_file(filename):
    """
    Check if a given filename has an allowed extension.

    This function verifies whether the filename contains a period ('.') and 
    has an extension that is in the allowed set of extensions.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file has an allowed extension, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'html'}

# Function to save the uploaded file to the temporary folder
def save_file(file):
    """
    Save the uploaded file with a secure filename and return the file path.

    This function generates a unique filename using a timestamp, ensures 
    the filename is secure, and saves the file to a temporary folder.

    Args:
        file (FileStorage): The uploaded file object.

    Returns:
        str: The file path where the uploaded file is saved.
    """
    ct = datetime.now()
    ts = ct.timestamp()
    filename = str(ts) + "_" + secure_filename(file.filename)
    file_path = os.path.join(TEMP_FOLDER, filename)
    file.save(file_path)

    return file_path

# Function to load and split the data from the PDF file
def load_and_split_file(file_path, title, author, description, time_stamp, hash):
    """
    Load an HTML file, split its content into chunks, and return the processed data.

    This function uses `MGHTMLLoader` to read the HTML file, then splits the 
    document into smaller chunks using `RecursiveCharacterTextSplitter`.

    Args:
        file_path (str): The path to the HTML file to be processed.

    Returns:
        list: A list of document chunks obtained after splitting the content.
    """
    #loader = BSHTMLLoader(file_path=file_path)
    loader = MGHTMLLoader(file_path=file_path, open_encoding="utf-8", title="urmom", author="urmom2", description="urmom3", time_stamp="urmoom")
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)

    return chunks

# Function to load and split the data from directory
def load_and_split_dir(file_path):
    """
    Load and process HTML files from a directory, then split their content into chunks.

    This function uses `DirectoryLoader` with `BSHTMLLoader` to read all HTML files 
    in the specified directory. It then splits the loaded documents into smaller 
    chunks using `RecursiveCharacterTextSplitter`.

    Args:
        file_path (str): The path to the directory containing HTML files.

    Returns:
        list: A list of document chunks obtained after splitting the content.
    """
    loader = DirectoryLoader(file_path=file_path, loader_cls=BSHTMLLoader, use_multithreading=True)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)

    return chunks

# Main function to handle the embedding process
def embed(file_path):
    """
    Load, process, and store a file's content in a vector database.

    This function loads and splits the file into chunks using `load_and_split_file()`, 
    adds the processed chunks to a vector database using `get_vector_db()`, and 
    persists the database for future use.

    Args:
        file_path (str): The path to the file to be processed.

    Returns:
        bool: True if the process completes successfully.
    """
        #if file.filename != '' and file and allowed_file(file.filename):
        #file_path = save_file(file)
    chunks = load_and_split_file(file_path)
    db = get_vector_db()
    db.add_documents(chunks)
    db.persist()
    #os.remove(file_path)

    return True

    #return False
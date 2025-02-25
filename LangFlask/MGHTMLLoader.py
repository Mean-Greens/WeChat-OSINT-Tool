import importlib.util
import logging
from pathlib import Path
import sys
from typing import Dict, Iterator, Union
import unicodedata
from bs4 import BeautifulSoup
import os
import argparse

from langchain_core.documents import Document

from langchain_community.document_loaders.base import BaseLoader

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Demo import *
import json

logger = logging.getLogger(__name__)


class MGHTMLLoader(BaseLoader):
    """
    __ModuleName__ document loader integration

    Setup:
        Install ``langchain-community`` and ``bs4``.

        .. code-block:: bash

            pip install -U langchain-community bs4

    Instantiate:
        .. code-block:: python

            from langchain_community.document_loaders import BSHTMLLoader

            loader = BSHTMLLoader(
                file_path="./example_data/fake-content.html",
            )

    Lazy load:
        .. code-block:: python

            docs = []
            docs_lazy = loader.lazy_load()

            # async variant:
            # docs_lazy = await loader.alazy_load()

            for doc in docs_lazy:
                docs.append(doc)
            print(docs[0].page_content[:100])
            print(docs[0].metadata)

        .. code-block:: python


            Test Title


            My First Heading
            My first paragraph.



            {'source': './example_data/fake-content.html', 'title': 'Test Title'}

    Async load:
        .. code-block:: python

            docs = await loader.aload()
            print(docs[0].page_content[:100])
            print(docs[0].metadata)

        .. code-block:: python



            Test Title


            My First Heading
            My first paragraph.



            {'source': './example_data/fake-content.html', 'title': 'Test Title'}

    """  # noqa: E501

    def __init__(
        self,
        file_path: Union[str, Path],
        link: str = "",
        title: str = "",
        author: str = "",
        time_stamp: str = "",
        description: str = "",
        hash: str = "",
        open_encoding: Union[str, None] = None,
        bs_kwargs: Union[dict, None] = None,
        get_text_separator: str = "",
    ) -> None:
        """initialize with path, and optionally, file encoding to use, and any kwargs
        to pass to the BeautifulSoup object.

        Args:
            file_path: The path to the file to load.
            open_encoding: The encoding to use when opening the file.
            bs_kwargs: Any kwargs to pass to the BeautifulSoup object.
            get_text_separator: The separator to use when calling get_text on the soup.
        """
        try:
            import bs4  # noqa:F401
        except ImportError:
            raise ImportError(
                "beautifulsoup4 package not found, please install it with "
                "`pip install beautifulsoup4`"
            )

        self.file_path = file_path
        self.link = link
        self.title = title
        self.author = author
        self.time_stamp = time_stamp
        self.description = description
        self.hash = hash
        self.open_encoding = open_encoding
        if bs_kwargs is None:
            if not importlib.util.find_spec("lxml"):
                raise ImportError(
                    "By default BSHTMLLoader uses the 'lxml' package. Please either "
                    "install it with `pip install -U lxml` or pass in init arg "
                    "`bs_kwargs={'features': '...'}` to overwrite the default "
                    "BeautifulSoup kwargs."
                )
            bs_kwargs = {"features": "lxml"}
        self.bs_kwargs = bs_kwargs
        self.get_text_separator = get_text_separator

    def lazy_load(self) -> Iterator[Document]:
        """Load HTML document into document objects."""
        from bs4 import BeautifulSoup

        with open(self.file_path, "r", encoding=self.open_encoding) as f:
            soup = BeautifulSoup(f, **self.bs_kwargs)

        text = soup.get_text(self.get_text_separator)

        # if soup.title:
        #     title = str(soup.title.string)
        # else:
        #     title = ""

        metadata: Dict[str, Union[str, None]] = {
            "source": self.link,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "date": self.time_stamp,
            "hash": self.hash
        }
        yield Document(page_content=text, metadata=metadata)

@timer
def reload_database(folder_path):
    documents = []

    # Walk through the directory structure
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".html"):
                file_path = os.path.join(root, file_name)
                soup = BeautifulSoup(open(file_path, "r", encoding="utf-8"), "html.parser")
                
                # Get a string of the html to save to folder of html files
                website = str(soup)

                # Strip the text out of the html and normalize it
                body = soup.body
                body_text = body.get_text(strip=True)
                normalized_text = unicodedata.normalize("NFKD", body_text)
                normalized_text = ' '.join(normalized_text.split())

                # Get the metadata
                metadata_folder = os.path.join(os.path.dirname(__file__), "metadata")
                metadata_file_path = os.path.join(metadata_folder, "metadata_deduplicated.json")

                with open(metadata_file_path, "r", encoding="utf-8") as metadata_file:
                    metadata = json.load(metadata_file)

                for data in metadata:
                    if data["key"] == "hash" and data["string_value"] == file_name.replace(".html", ""):
                        id = data["id"]
                        break

                data_matching_hash = []
                for data in metadata:
                    if data["id"] == id:
                        data_matching_hash.append(data)

                source = ""
                title = ""
                description = ""
                author = ""
                date = ""
                keyword = ""

                for data in data_matching_hash:
                    if data["key"] == "source":
                        source = data["string_value"]
                    elif data["key"] == "title":
                        title = data["string_value"]
                    elif data["key"] == "description":
                        description = data["string_value"]
                    elif data["key"] == "author":
                        author = data["string_value"]
                    elif data["key"] == "date":
                        date = data["string_value"]
                    elif data["key"] == "keyword":
                        keyword = data["string_value"]

                # rehash the article
                web_hash = hashlib.sha256(normalized_text.encode('utf-8')).hexdigest()

                metadata: Dict[str, Union[str, None]] = {
                "source": source,
                "title": title,
                "description": description,
                "author": author,
                "date": date,
                "hash": web_hash,
                "keyword": keyword
                }

                # Create document objects for the website and the normalized text to store in the database
                doc = [Document(page_content=website, metadata=metadata), Document(page_content=normalized_text, metadata=metadata)]
            
                # The store_websites function is a function that stores the websites in the database and takes a list of document objects
                documents.append(doc)

    # store the websites in the database
    store_websites(documents)
    return

def deduplicate_metadata(file_name="metadata.json"):
    '''
    Output the metadata from the sqlite database to a JSON file.
    This function then filters out duplicate metadata items based on the hash key.
    '''
    metadata_folder = os.path.join(os.path.dirname(__file__), "metadata")
    metadata_file_path = os.path.join(metadata_folder, file_name)

    with open(metadata_file_path, "r", encoding="utf-8") as metadata_file:
        metadata = json.load(metadata_file)

    unique_hash_ids = []
    seen_hashes = set()

    for data in metadata:
        if data["key"] == "hash" and data["string_value"] not in seen_hashes:
            unique_hash_ids.append(data["id"])
            seen_hashes.add(data["string_value"])

    # Filter out items that do not have an id in unique_hash_ids
    deduplicated_metadata = [data for data in metadata if data["id"] in unique_hash_ids]

    # Save the deduplicated metadata to a new JSON file
    deduplicated_metadata_file_path = os.path.join(metadata_folder, "metadata_deduplicated.json")
    with open(deduplicated_metadata_file_path, "w", encoding="utf-8") as deduplicated_metadata_file:
        json.dump(deduplicated_metadata, deduplicated_metadata_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='A script that takes a mode and a filename as arguments.')

    # Add arguments
    parser.add_argument('mode', type=int, choices=[1, 2], help='Mode number (1 or 2)')
    parser.add_argument('filename', type=str, help='Name of the file')

    # Parse and validate the arguments
    args = parser.parse_args()

    # Use the arguments
    if args.mode == 1:
        # Reload the database
        reload_database(os.path.join(os.path.dirname(__file__), "html"))
    elif args.mode == 2:
        # Deduplicate the metadata
        deduplicate_metadata(args.filename)
    else:
        print("Invalid mode number. Please enter 1 or 2.")
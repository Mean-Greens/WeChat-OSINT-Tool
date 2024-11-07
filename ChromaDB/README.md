## Setup Chroma DB for vector embeddings
1. Install Microsoft C++ build tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/ (Only for Windows)
2. `pip install chromadb`
3. Pull ollama model for creating vector embeddings `ollama pull mxbai-embed-large`
4. create folder db

## Read full text of documents
1. `cd db`
2. `sqlite3 chroma.sqlite3`
3. `select * from embedding_fulltext_search;`

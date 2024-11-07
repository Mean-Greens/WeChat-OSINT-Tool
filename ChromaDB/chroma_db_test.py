import chromadb

client = chromadb.PersistentClient(path='./db')

collection = client.get_or_create_collection(name="test")

if collection.count() == 0:
    collection.add(
        documents=[
            "This is a document about machine learning",
            "This is another document about data science",
            "A third document about artificial intelligence"
        ],
        metadatas=[
            {"source": "test1"},
            {"source": "test2"},
            {"source": "test3"}
        ],
        ids=[
            "id1",
            "id2",
            "id3"
        ]
    )

print(collection.count())
print(client.list_collections())
print()

results = collection.query(
    query_texts=[
        "This is a query about machine learning and data science"
    ],
    n_results=2
)

print(results)

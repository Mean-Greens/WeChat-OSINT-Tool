from embed import embed
from query import query
from get_vector_db import get_vector_db
import os
from dotenv import load_dotenv

load_dotenv()

str = input("Enter a query, 1 to upload file, or quit to exit: \n")
while str != "quit":
    if str == "1":
        file_path = input("Enter a file path: \n")
        embed(file_path)
    else:
        response = query(str)
        print(response)
 
    str = input("Enter a query or quit to exit: \n")

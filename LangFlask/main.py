from embed import embed
from query import query
from get_vector_db import get_vector_db
import os
from dotenv import load_dotenv

load_dotenv()

str = input("Enter a query or quit to exit: \n")
while str != "quit":
    response = query(str)
    print(response)
    str = input("Enter a query or quit to exit: \n")

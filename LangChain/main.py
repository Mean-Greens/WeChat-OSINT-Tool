from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage

chat_model = ChatOllama(model="gemma2:2b")

#user_input = input("Enter your prompt: ")

messages = [
    SystemMessage(content="You are a helpful asssistant.")
]

while True: 
    user_input = input("How can I help: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    messages.append(HumanMessage(content=user_input))
    response = chat_model.invoke(messages)
    print(f"Assistant: {response.content}")
    
#response = chat_model.invoke(messages)
#print(f"{response.content}")
#print("Hello, world")
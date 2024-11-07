from Sogou_Search_Scraper import *
from llm_axe import *

def main():
    # Example showing how to use an online agent
    # The online agent will use the internet to try and best answer the user prompt
    prompt = "跟我说说中国国家主席吧"
    llm = OllamaChat(model="gemma2:2b")
    # searcher = OnlineAgent(llm)
    # resp = searcher.search(prompt)
    # print(resp)

    
    # You may provide the OnlineAgent with a custom searcher
    # The searcher must take in a search query and return a list of string URLS
    # example hard coded searcher:
    searcher = OnlineAgent(llm, custom_searcher=sogou_searcher)
    resp = searcher.search(prompt)
    print(resp)




if __name__ == "__main__":
    main()
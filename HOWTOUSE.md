# How to Use

This tool is an OSINT tool meant to make Chinese Web data more accessible by using webscraping and an LLM. This tool implements a user's custom word list to target specific topics of interest. The workflow operates as follows:

1. User enters a word into the wordlist on the page "Word List."
2. The program takes that word and will search the Chinese Browser Sogou and a preset schedule.
3. The progarm saves the articles in the Postgres database the user set up. 
4. A list of saved article hashes can be view on the "Articles" page. 
5. When a user submits a query on the "Query LLM" page, the LLM with referece scraped articles to generate a relevant, translated response. This allows English users to contextualize and begin to understand Chinese web data. 

NOTE: The response of the LLM in this tool is directly tied to the articles it is able to scrape. Because of this, questions asked outside of the context of words in the word list will create mixed results and may not yeild useful infromation. 
Below are a set of simple instructions to use each page on this tool.

### Query LLM

This page contains the main functionality of the tool and is 


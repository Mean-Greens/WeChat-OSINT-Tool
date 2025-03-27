# How to Use

This is an OSINT tool meant to make Chinese Web data more accessible by using webscraping and an LLM. This tool implements a user's custom word list to target specific topics of interest. The workflow operates as follows:

1. User enters a word into the wordlist on the page "Word List."
2. The program takes that word and will search the Chinese Browser Sogou on a preset schedule.
3. The progarm saves the articles in the Chroma database the user set up. 
4. A list of saved articles can be viewed on the "Articles" page. 
5. When a user submits a query on the "Query LLM" page, the LLM will referece scraped articles to generate a relevant, translated response. This allows English users to contextualize and begin to understand Chinese web data. 

NOTE: The response of the LLM in this tool is directly tied to the articles it is able to scrape. Because of this, questions asked outside of the context of words in the word list will create mixed results and may not yeild useful infromation. 

Below are a set of simple instructions to use each page on this tool.

### Query LLM

This page contains the main functionality of the tool and is where the user interacts directly with the LLM. The LLM in this program is not a chat bot and has no memory of previous prompts. Because of this, each response is unique and does not reference any previous conversation. 

In the response the LLM will give the user, the top 5 most revelvant artciles will be displayed for the user's reference. The user can click on the provided title of the article to see the webpage the article referenced (Many of these pages are in Chinese, but the user is welcome to view them if they like, most browsers can translate them with some varying degree of accuracy).

### Word List

This is where the user imputs words to influence the topics the LLM can reference. The user can add or subtract words from this list as they wish. The scraper will search for every word in this list every 15 to 25 minutes for new relevant articles. Duplicates should not be stored. Beside every word there is a a count of how many articles are in the database are related to that article (Note: this shows the articles that were scraped from wechat with that word, not necessarily purely what words are related to the article). By clicking on the word you can also see the articles just related to that word.

### Articles

There is very little the user can do with the articles page. This is where a list of the hashes of found articles can be viewed. Users can visit each of these pages by clicking on the hashes if they wish. 


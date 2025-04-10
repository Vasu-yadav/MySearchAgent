import bs4 as beautifulsoup
import requests
import trafilatura
from google import genai
import dotenv
import os


dotenv.load_dotenv()
api_key=os.getenv('GOOGLE_API_KEY')

client = genai.Client(api_key=api_key)

def search_or_not(user_query):
    PROMPT = f"""
    You are a specialized Yes/No decision agent. Your sole purpose is to determine whether a given user query requires an internet search to provide accurate, relevant, and up-to-date information.
        Respond ONLY with "Yes" or "No":
        - "Yes" if the query:
        * Requires current data or recent information
        * Needs real-time facts or statistics
        * Involves current events, news, or trends
        * Requires checking latest prices, availability, or status
        * Needs verification of time-sensitive information
        * asks date and time
        * Involves specific product details or comparisons
        * Requires confirmation of recent changes or updates
        * Involves specific location-based information

        - "No" if the query:
        * Is a basic conversational exchange
        * Involves general knowledge or historical facts
        * Anything that is not a basic conversational exchange
        * Is a personal opinion or preference
        * Is a hypothetical or philosophical question
        * Is a request for advice or recommendations
        * Is a question that can be answered with existing knowledge
        * Is a request for definitions or explanations
        * Is a question that does not require real-time data
        * Is a request for clarification or elaboration
        * Is a question that does not require an internet search

        Do not provide explanations or additional context. Only respond with "Yes" or "No".

        USER QUERY: {user_query}
    """

    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=PROMPT,
)

    content = response.text
    print(f'SEARCH OR NOT: {content}')

    if 'yes' in content.lower():
        return True
    else:
        return False
    

def query_generator(user_query):
    PROMPT = f"""
    You are a specialized search query optimization agent. Your sole purpose is to transform user queries into effective Google search queries that will yield the most relevant results.

        Your task is to:
        1. Analyze the user's original query
        2. Extract key concepts and important terms
        3. Format them into an optimized search query
        4. Include relevant operators when beneficial (site:, filetype:, etc.)

        Rules:
        - Respond ONLY with the search query string
        - Do not include explanations or additional text
        - Remove unnecessary words (articles, pronouns, etc.)
        - Include quotation marks for exact phrases when needed
        - Add relevant synonyms with OR operator when appropriate
        - Focus on specific, factual terms

        Examples:
        User: "What's the current price of a Tesla Model 3 in California?"
        Response: tesla model 3 price california 2024

        User: "How do I make authentic Italian pasta from scratch?"
        Response: "authentic Italian pasta recipe" homemade traditional

        Do not provide any commentary - output only the optimized search query.

        USER QUERY: {user_query}
    """
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=PROMPT,
)

    content = response.text
    print(f'QUERY GENERATOR: {content}')

    return content

def searxng_search(query):
    import requests
    from bs4 import BeautifulSoup

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    # Query the local searxng instance. Adjust parameters as needed.
    url = 'http://localhost:4000/search'
    params = {
        'q': query,
        'language': 'auto',
        'safesearch': '0',
        'theme': 'simple'
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    # Use a CSS selector to get all articles with class "result"
    articles = soup.select('article.result')
    for i, article in enumerate(articles, start=1):
        if i > 5:
            break
        # Get the URL from the <a> with class "url_header"
        link_tag = article.find('a', class_='url_header')
        if not link_tag:
            continue
        link = link_tag.get('href', 'No URL found')
        
        # Get the snippet from the <p> with class "content"
        snippet_tag = article.find('p', class_='content')
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else 'No description available'
        
        results.append({
            'id': i,
            'link': link,
            'search_description': snippet
        })
    
    return results

def best_search_results(s_results, query, user_prompt):
    PROMPT = f"""
    You are a specialized search result selection agent. Your sole purpose is to analyze search results and select the most relevant one for answering a user's query.

        For each request, you will receive:
        - SEARCH_RESULTS: A list of search result objects [0-9]
        - USER_PROMPT: The original user question
        - SEARCH_QUERY: The query used to generate these results

        Your task:
        1. Analyze all search results
        2. Consider factors like:
            * Relevance to the user prompt
            * Source credibility
            * Information freshness
            * Content completeness
        3. Select the index (0-9) of the single best result

        Rules:
        - Respond ONLY with a single integer (0-4)
        - Do not include any explanation or commentary
        - Choose the result an expert would click first
        - Focus on authoritative and comprehensive sources

        Examples:
        Input: [results], "What's Tesla's stock price?", "tesla stock price NASDAQ"
        Response: 0

        Input: [results], "How to make sourdough bread?", "sourdough bread recipe tutorial"
        Response: 2

        SEARCH_RESULTS: {s_results} 
        USER_PROMPT: {user_prompt} 
        SEARCH_QUERY: {query}
    """
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=PROMPT,
)

    content = response.text
    print(f'BEST SEARCH RESULT: {content}')

    return content

def scrape_webpage(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded,include_links=True, deduplicate=True)
    except Exception as e:
        return None
    
def contains_data_needed(search_content, query, user_prompt):
    PROMPT = f"""
    You are a specialized data verification agent. Your sole purpose is to analyze PAGE_TEXT and determine whether it contains the necessary and reliable data to answer the USER_PROMPT."
        
        For each request, you will receive:
        - PAGE_TEXT: The complete text from the best search result, retrieved using SEARCH_QUERY.
        - USER_PROMPT: The original prompt sent to the actual web search-enabled AI assistant.
        - SEARCH_QUERY: The query used to retrieve PAGE_TEXT."
        
        Your task:
        1. Evaluate the PAGE_TEXT in the context of the USER_PROMPT.
        2. Verify that the PAGE_TEXT includes reliable and sufficient data for generating a correct and intelligent response.
        3. Output exactly one token: "True" if the PAGE_TEXT meets the criteria, or "False" otherwise."
        
        Rules:
        - Do not include any commentary or additional information.
        - Respond with a single token: either "True" or "False".
        - Base your evaluation solely on the information provided in PAGE_TEXT.

        PAGE_TEXT: {search_content}
        USER_PROMPT: {user_prompt}
        SEARCH_QUERY: {query}
    """
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=PROMPT,
)

    content = response.text

    print(f'CONTAINS DATA NEEDED: {content}')

    if 'true' in content.lower():
        return True
    else:
        return False
    
def ai_search(user_query):
    context = None
    print("GENERATING SEARCH QUERY...")
    search_query = query_generator(user_query)

    if search_query[0] == '"':
        search_query = search_query[1:-1]

    search_results = searxng_search(search_query)
    print(f"SEARCH RESULTS: {search_results}")
    context_found = False

    while not context_found and len(search_results) > 0:
        best_result = best_search_results(search_results, search_query, user_query)
        
        # Convert the result to an integer and handle invalid responses
        try:
            best_result = int(best_result)
        except ValueError:
            print(f"Invalid result '{best_result}' returned. Removing the first result as fallback.")
            search_results.pop(0)  # Remove the first result as a fallback
            continue

        # Validate the index returned by best_search_results
        if not (0 <= best_result < len(search_results)):
            print(f"Invalid index {best_result} returned. Removing the first result as fallback.")
            search_results.pop(0)  # Remove the first result as a fallback
            continue
        
        try:
            page_link = search_results[best_result]['link']
        except IndexError:
            print('FAILED TO SELECT BEST SEARCH RESULT, TRYING AGAIN...')
            search_results.pop(best_result)  # Remove the invalid result
            continue
        
        page_content = scrape_webpage(page_link)
        
        if page_content and contains_data_needed(page_content, search_query, user_query):
            context_found = True
            return page_content
        else:   
            search_results.pop(best_result)  # Remove the result if it doesn't contain needed data
            continue

    return None

def generateResponse(user_query, context):
    PROMPT = f"""
    You are a specialized response generation agent. Your task is to generate a comprehensive and intelligent response to the user's query using the provided context.

        USER QUERY: {user_query}
        CONTEXT: {context}

        Generate a detailed and informative response based on the context.
    """
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=PROMPT,
)

    print(f"Response: {response.text}")

def main():
    while True: 
        user_query = input("Enter your query: ")
        if user_query.lower() == 'exit':
            break
        if search_or_not(user_query):
            context = ai_search(user_query)
            if context:
                print(f"Context found: {context}")
                generateResponse(user_query, context)
            else:
                print("No relevant context found.")
        else:
            print("No search needed for this query.")
            response = client.models.generate_content(
                model="gemini-2.0-flash", contents=user_query,
            )
            print(f"Response: {response.text}")


if __name__ == "__main__":
    main()

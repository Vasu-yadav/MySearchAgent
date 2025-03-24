import ollama
import utils.sys_msgs as sys_msgs
import bs4 as beautifulsoup
import requests
import trafilatura

assistant_convo = [sys_msgs.assistant_msg]

def search_or_not():
    sys_msg = sys_msgs.INTERNET_SEARCH_CLASSIFIER_SYSTEM_MSG

    response = ollama.chat(
        model='gemma3:4b-it-fp16',
        messages=[{'role':'system','content':sys_msg}, assistant_convo[-1]]
    )

    content = response['message']['content']
    print(f'SEARCH OR NOT: {content}')

    if 'yes' in content.lower():
        return True
    else:
        return False
    

def query_generator():
    sys_msg = sys_msgs.SEARCH_QUERY_GENERATOR_SYSTEM_MSG

    query_msg = f'CREATE A SEARCH QUERY FOR THIS PROMPT: \n {assistant_convo[-1]}'

    response = ollama.chat(
        model='gemma3:4b-it-fp16',
        messages=[{'role':'system','content':sys_msg}, {'role': 'user', 'content': query_msg}]
    )

    content = response['message']['content']
    print(f'QUERY GENERATOR: {content}')

    return content

def duckduckgo_search(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.'
    }
    url = f'https://duckduckgo.com/html/?q={query}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = beautifulsoup.BeautifulSoup(response.text, 'html.parser')
    results = []
    for i, result in enumerate(soup.find_all('div', class_ = 'result'), start=1):
        if i > 10:
            break
        title = result.find('a', class_='result__a')
        if not title:
            continue

        link = title['href']
        snippet_tag = result.find('a', class_='result__snippet')
        snippet = snippet_tag.text.strip() if snippet_tag else 'No description available'

        results.append({
            'id': i,
            'link': link,
            'search_description': snippet
        })
    return results

def best_search_results(s_results, query):
    sys_msg = sys_msgs.BEST_SEARCH_RESULT_SYSTEM_MSG
    best_msg = f'SEARCH_RESULTS: {s_results} \nUSER_PROMPT: {assistant_convo[-1]} \nSEARCH_QUERY: {query}'

    for _ in range(2):
        try:
            response = ollama.chat(
                model='gemma3:4b-it-fp16',
                messages=[{'role':'system','content':sys_msg}, {'role': 'user', 'content': best_msg}]
            )
            print(f'Best Search result Index: {response['message']['content']}')
            return int(response['message']['content'])
        except:
            continue   
    return 0

def scrape_webpage(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded, include_formatting=True,include_links=True)
    except Exception as e:
        return None
    
def contains_data_needed(search_content, query):
    sys_msg = sys_msgs.CONTAINS_DATA_MSG
    needed_prompt = f'PAGE_TEXT: {search_content} \nUSER_PROMPT: {assistant_convo[-1]} \nSEARCH_QUERY:{query}'
    
    response = ollama.chat(
        model='gemma3:4b-it-fp16',
        messages=[{'role':'system','content':sys_msg}, {'role': 'user', 'content': needed_prompt}]
    )

    content = response['message']['content']

    print(f'CONTAINS DATA NEEDED: {content}')

    if 'true' in content.lower():
        return True
    else:
        return False
    
def ai_search():
    context = None
    print("GENERATING SEARCH QUERY...")
    search_query = query_generator()

    if search_query[0] == '"':
        search_query = search_query[1:-1]

    search_results = duckduckgo_search(search_query)
    context_found = False

    while not context_found and len(search_results) > 0:
        best_result = best_search_results(search_results, search_query)
        print(len(search_results))
        try:
            page_link = search_results[best_result]['link']
        except:
            print('FAILED TO SELECT BEST SEARCH RESULT, TRYING AGAIN...')
            continue

        page_text = scrape_webpage(page_link)
        print(f"PAGE TEXT: {page_text}\n")
        search_results.pop(best_result)

        if page_text and contains_data_needed(search_content=page_text, query=search_query):
            context = page_text
            context_found = True

    return context

def stream_assistant_response():
    global assistant_convo
    response = ollama.chat(model='gemma3:4b-it-fp16', messages=assistant_convo, stream = True)
    complete_response = ''
    print('Assistant:')

    for chunk in response:
        print(chunk['message']['content'], end='',flush=True)
        complete_response += chunk['message']['content']
    assistant_convo.append({'role': 'assistant','content':complete_response})
    print('\n\n')

def main():
    global assistant_convo
    
    while True:
        user_input = input('You:')
        assistant_convo.append({'role': 'user', 'content': user_input})
        if user_input.lower() == 'exit':
            break
        if search_or_not():
            context = ai_search()
            assistant_convo = assistant_convo[:-1]

            if context:
                prompt = f'SEARCH RESULT: {context} \n\nUSER PROMPT: {user_input}'
            else:
                prompt = (
                    f'USER PROMPT: In{user_input} \n\nFAILED SEARCH: \nThe'
                    'AI search model was unable to extract any reliable data. Explain that '
                    'and ask if the user would like you to search again or respond '
                    'without web search context. Do not respond if a search was needed '
                    'and you are getting this message with anything but the above request'
                    'of how the user would like to proceed.'
                )
            assistant_convo.append({'role': 'user', 'content': user_input})
            
        stream_assistant_response()

if __name__ == '__main__':
    main()
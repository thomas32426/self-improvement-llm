from duckduckgo_search import DDGS
import json
# beautiful soup

def web_search(search_query, max_results=5):
    if(max_results > 10):
        max_results = 10

    c = {}
    count = 1

    with DDGS() as ddgs:
        for r in ddgs.text(search_query, region='wt-wt', safesearch='off', timelimit='y', max_results=max_results):
            c[str(count)] = r
            count += 1

    return json.dumps(c)


if __name__ == "__main__":
    b = web_search('pineapples', 3)
    print(b)
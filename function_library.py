from duckduckgo_search import DDGS
import json
import subprocess
import tempfile
import autopep8
import re


def web_search(search_query: str, max_results: int=5):
    """ Search the web using Duck Duck Go. """
    if(max_results > 10):
        max_results = 10

    c = {}
    count = 1

    with DDGS() as ddgs:
        for r in ddgs.text(search_query, region='wt-wt', safesearch='off', timelimit='y', max_results=max_results):
            c[str(count)] = r
            count += 1

    return json.dumps(c)


def execute_code(code: str, timeout: int) -> str:
    """ Execute a Python script. """
    if extract_python_code(code):
        code = extract_python_code(code)

    first_lint_result = lint_code(code)

    if first_lint_result:
        code = autopep8.fix_code(code)

        second_lint_result = lint_code(code)

        if second_lint_result:
            return f"Linting errors:\n{first_lint_result}\n" + f"Post-autopep8 errors:\n{second_lint_result}"
    try:
        # Execute the code using a subprocess with a timeout
        result = subprocess.run(
            ["python3", "-c", code],
            timeout=timeout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Combine stdout and stderr for the full output
        output = result.stdout + result.stderr
        return output

    except subprocess.TimeoutExpired:
        return "Execution timed out!"

    except Exception as e:
        return f"An error occurred: {e}"


def extract_python_code(s: str) -> str:
    match = re.search(r'```python(.*?)```', s, re.DOTALL)
    return match.group(1).strip() if match else False


def lint_code(code: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tf:
        tf.write(code.encode())
        tf.flush()
        result = subprocess.run(
            ["flake8", tf.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    return result.stdout + result.stderr


if __name__ == "__main__":
    print("Web Search:")
    search_results = web_search('pineapples', 3)
    print(search_results, end='\n\n\n')

    print("Execute Code:")
    code = """
    import time
    time.sleep(2)
    print("Hello after 2 seconds!", end='')
    """
    print(execute_code(code, 3))
    print(execute_code(code, 1))
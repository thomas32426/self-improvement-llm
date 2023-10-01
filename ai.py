import openai
import os
import json
import logging
from typing import List, Dict

from function_registry import FunctionRegistry

openai.api_base = "https://api.openai.com/v1"
openai.api_key = os.environ.get("OPENAI_API_KEY", "sk-foo")


def chat(messages: Dict, functions:Dict=None):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo-16k-0613",
        messages = messages,
        functions = functions,
        function_call = "auto",
        temperature = 0.0,
    )
    return response["choices"][0]["message"].to_dict()

def message_step(user_message, messages: List, functions: FunctionRegistry):
    messages.append({"role": "user", "content": user_message})
    logging.info(json.dumps(messages[-1]))

    response = chat(messages, functions.get_function_descriptions())
    count = 0
    while response.get("function_call") is not None:
        function_name = response.get("function_call")["name"]
        function_args = json.loads(response.get("function_call")["arguments"])
        function_content = functions.execute_function(function_name, function_args)
        messages.append({"role": "function", "name": function_name, "content": function_content})
        logging.info(json.dumps(messages[-1]))

        response = chat(messages, functions.get_function_descriptions())
        count += 1

    return messages[-1]


if __name__ == "__main__":
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(filename='logs/conversation.log', level=logging.INFO, format='%(asctime)s - %(message)s')
    messages = [{"role": "system", "content": "You are a helpful assistant"}]
    logging.info(json.dumps(messages[0]))
    functions = FunctionRegistry("functions.json")

    print("You are now chatting with the AI. Type 'quit' to exit.")
    
    # Start the interactive chat loop with the AI
    while True:
        user_input = input("User: ").strip()
        if user_input.lower() == 'quit':
            break
        try:
            responses = message_step(user_input, messages, functions)
            for response in responses:
                print("AI:", response)
        except Exception as e:
            print("An error occurred: ", str(e))


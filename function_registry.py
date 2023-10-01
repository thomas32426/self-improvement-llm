import json


class FunctionRegistry:
    def __init__(self, json_file: str):
        """
        A registry to handle the functions available to the assistant.

        This class reads function descriptions from a JSON file, allowing the
        registration of actual function implementations to be called by the
        assistant. It also provides methods to access the function descriptions
        and to execute specific functions.

        Attributes:
            functions (list): A list of dictionaries containing the details of the functions.
            function_descriptions (list, optional): A cached list of function descriptions without implementations.
            token_length (int, optional): Cached token length of the function descriptions.

        Args:
            json_file (str): Path to the JSON file containing the function descriptions.
        """
        with open(json_file, 'r') as file:
            self.functions = json.load(file)
        self.function_descriptions = None
        self.token_length = None

    def register_function(self, name: str, func):
        """
        Register a function implementation by its name.

        This method associates a given function implementation with the name provided
        in the 'functions' list. If the name does not exist in the functions list,
        an error will be raised.

        Args:
            name (str): The name of the function as defined in the functions list.
            func: The actual implementation of the function to be registered.

        Raises:
            ValueError: If the name provided does not exist in the functions list.
        """
        for function in self.functions:
            if function['name'] == name:
                function['func'] = func
                return

        raise ValueError(f"Function with name '{name}' not found in the registry.")

    def get_function_descriptions(self):
        """
        Retrieve descriptions for all registered functions.

        This method constructs and caches a list of dictionaries containing
        the names, descriptions, and parameters of the registered functions.
        If called multiple times, the cached value is returned.

        Returns:
            List[Dict]: A list of dictionaries, each containing information about
            a registered function, including its name, description, and parameters.
        """
        if self.function_descriptions is None:
            self.function_descriptions = [
                {
                    "name": f["name"],
                    "description": f["description"],
                    "parameters": f["parameters"],
                } for f in self.functions
            ]
        return self.function_descriptions

    def get_token_length(self, encoding):
        """
        Retrieve the token length of the function descriptions.

        This method calculates and caches the token length of the JSON-serialized
        function descriptions using the specified encoding. If called multiple times,
        the cached value is returned.

        Args:
            encoding (function): A function that encodes a string into tokens (e.g., a tokenizer from tiktoken).

        Returns:
            int: The token length of the function descriptions.
        """
        if self.token_length is None:
            self.token_length = len(encoding.encode(json.dumps(self.get_function_descriptions())))
        return self.token_length

    def execute_function(self, name: str, arguments: dict):
        """
        Execute a registered function by its name with the given arguments.

        This method looks up a function by its name in the registered functions and
        executes it with the provided arguments.

        Args:
            name (str): The name of the function to execute.
            arguments (dict): A dictionary containing the arguments to be passed to the function.

        Returns:
            Any: The result of executing the function, or an error message if the function is not found.
        """
        func = next((f["func"] for f in self.functions if f["name"] == name), None)
        if func:
            return func(**arguments)
        else:
            return f"Function {name} not found."
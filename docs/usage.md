# COCOLLAMA

In your terminal just run `cocollama` when installed with pip in a venv or global env. 

It will be launched with your local ollama. 

to chat with your model just run `chat <your_query>` in the ollama cli. 

 Run `chat <query> $(cmd)` to run a cmd and put the output as context inside your query.

You can easily change the way your query is formatted in the `extract_command` method from `OllamaShell`.

Default model is set to `gemma3:1b`.
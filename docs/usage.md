# COCOLLAMA

In your terminal just run `cocollama` when installed with pip in a venv or global env. 

It will be launched with your local ollama. 

to chat with your model just run `chat <your_query>` in the ollama cli. 

 Run `chat <query> $(cmd)` to run a cmd and put the output as context inside your query.

You can easily change the way your query is formatted in the `extract_command` method from `OllamaShell`.

Default model is set to `gemma3:1b`. Be sure you have it loaded or use `pull gemma3:1b`. 

I you need help for a command type `help <cmd>`. 

It is better to run with [uv](https://docs.astral.sh/uv/) with `uv pip install .`. 

I hope you enjoy this side project (made with the useful help of [Claude](https://claude.ai)).
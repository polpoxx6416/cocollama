Cocollama is a nice CLI to use commands while chatting with an LLM hosted on Ollama. 

Just run cocollama after pip installing it `pip install -e .`

Then run `cocollama` to start the cli. Then run `chat <query> $(cmd)` to run a cmd and put its output inside your query.

You can easily change the way your query is formatted in the `extract_command` method from `OllamaShell`.

Default model is set to `gemma3:1b`.
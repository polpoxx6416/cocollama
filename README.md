# Cocollama

Cocollama is a nice CLI to use commands while chatting with an LLM hosted on Ollama. 


## Installation

```shell
git clone https://github.com/polpoxx6416/cocollama.git
cd cocollama
pip install .
```

## Usage

Be sure you have [ollama](https://ollama.com) installed on your computer and `gemma3:1b` loaded. 

Run `cocollama` to start the cli. Then run `chat <query> $(cmd)` to run a cmd and put its output inside your query.

If you want a specific model : `pull <model_name>`. 

You can easily change the way your query is formatted in the `extract_command` method from `OllamaShell`.

Default model is set to `gemma3:1b`.

## Improvements

- Take history as context
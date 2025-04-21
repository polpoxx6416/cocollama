import sys
from argparse import ArgumentParser

from .cocollama import OllamaShell


def main():
    """Command-line interface for Cocollama.
    
    Provides an interactive shell for communicating with Ollama LLM servers.
    Handles argument parsing and initializes the shell session.
    
    Arguments can be passed through command line:
        --model: The Ollama model to use (defaults to "gemma3:1b")
        --host: Ollama server host (defaults to "localhost")
        --port: Ollama server port (defaults to "11434")
    
    Returns:
        None
    
    Raises:
        KeyboardInterrupt: Handled gracefully for shell exit
    """
    parser = ArgumentParser(description="Ollama CLI - Interactive shell for Ollama LLM server")
    parser.add_argument("--model", type=str, default="gemma3:1b", 
                        help="Ollama model to use (default: gemma3:1b)")
    parser.add_argument("--host", type=str, default="localhost", 
                        help="Ollama host (default: localhost)")
    parser.add_argument("--port", type=str, default="11434", 
                        help="Ollama port (default: 11434)")
    
    args = parser.parse_args()
    
    try:
        OllamaShell(model=args.model, host=args.host, port=args.port).cmdloop()
    except KeyboardInterrupt:
        print("\nExiting Ollama CLI")
        sys.exit(0)


if __name__ == '__main__':
    main()
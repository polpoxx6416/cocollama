import cmd
import json
import os
import re
import subprocess
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urljoin

import requests


class OllamaShell(cmd.Cmd):
    """Interactive shell for communicating with Ollama LLM server."""

    def __init__(
        self, model: str = "gemma3:1b", host: str = "localhost", port: str = "11434"
    ):
        super().__init__()
        self.model = model
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}"
        self.intro = f"Ollama CLI - Connected to {self.base_url} - Using {model}"
        self.prompt = "cocollama> "
        self.last_response = ""
        self.check_connection()

    def check_connection(self) -> None:
        """Verify connection to Ollama server."""
        try:
            response = requests.get(url=urljoin(self.base_url, "/api/tags"), timeout=5)
            response.raise_for_status()
        except (
            requests.ConnectionError,
            requests.RequestException,
            requests.Timeout,
        ) as e:
            print(f"Error: {e}\nMake sure ollama is running on {self.base_url}")
            raise SystemExit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise SystemExit(1)

    def do_chat(self, arg: str) -> None:
        """Send a message to the model: chat <your message>"""
        if not arg:
            print("Please provide a message")
            return

        try:
            processed_arg = self.process_commands(arg)

            data = {
                "model": self.model,
                "prompt": processed_arg,
                "stream": True,
            }

            # print(f"\n[Prompt]: {processed_arg}\n[Response]:")
            self._stream_response(data)

        except KeyboardInterrupt:
            print("\nPrompt interrupted")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def _stream_response(self, data: Dict[str, Any]) -> None:
        """Stream response from Ollama API."""
        headers = {"Content-Type": "application/json"}
        api_endpoint = urljoin(self.base_url, "/api/generate")

        with requests.post(
            url=api_endpoint, headers=headers, json=data, stream=True
        ) as response:
            response.raise_for_status()
            self.last_response = ""

            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    json_chunk = json.loads(line.decode("utf-8"))
                    if not json_chunk.get("done", True):
                        chunk_content = json_chunk.get("response", "")
                        print(chunk_content, end="", flush=True)
                        self.last_response += chunk_content
                except json.JSONDecodeError:
                    print(f"\nError decoding response: {line.decode('utf-8')}")

            print("\n")

    def extract_commands(self, text: str) -> List[str]:
        """Extract shell commands from input text using $() syntax."""
        pattern = r"\$\((.*?)\)"
        return re.findall(pattern=pattern, string=text)

    def process_commands(self, text: str) -> str:
        """Process and execute embedded shell commands in the input text."""
        commands = self.extract_commands(text)
        if not commands:
            return text

        print(f"Found commands to execute: {', '.join(commands)}")
        response = input("Do you want to run these commands? (y/n): ").lower().strip()
        if response != "y":
            print("Commands not executed.")
            return text

        results = {}
        for cmd in commands:
            try:
                print(f"Executing: {cmd}")
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,  # Prevent hanging on long-running commands
                )

                cmd_id = cmd.replace(" ", "_")
                if result.returncode == 0:
                    results[cmd] = (
                        f"<{cmd_id}_output>_{result.stdout.strip()}_</{cmd_id}_output>"
                    )
                else:
                    results[cmd] = (
                        f"<{cmd_id}_error>_{result.stderr.strip()}_</{cmd_id}_error>"
                    )
            except subprocess.TimeoutExpired:
                results[cmd] = (
                    f"<{cmd_id}_error>_Command timed out after 30 seconds_</{cmd_id}_error>"
                )
            except Exception as e:
                results[cmd] = f"<{cmd_id}_error>_Exception: {str(e)}_</{cmd_id}_error>"

        # Replace all command placeholders with their results
        processed_text = text
        for cmd in commands:
            processed_text = processed_text.replace(f"$({cmd})", results.get(cmd, ""))

        return processed_text

    def do_model(self, arg: str) -> None:
        """Change the current model: model <model_name>"""
        if not arg:
            print(f"Current model: {self.model}")
            return

        try:
            # Verify the model exists
            with requests.get(url=urljoin(self.base_url, "/api/tags")) as response:
                response.raise_for_status()
                result = response.json()
                available_models = [model["name"] for model in result.get("models", [])]

                if arg not in available_models:
                    print(f"Model '{arg}' not found. Available models:")
                    for model in available_models:
                        print(f"  {model}")
                    return

            # Set the new model
            self.model = arg
            print(f"Model changed to: {self.model}")
        except Exception as e:
            print(f"Error changing model: {e}")

    def do_list(self, arg: str) -> None:
        """List all available models"""
        try:
            with requests.get(url=urljoin(self.base_url, "/api/tags")) as response:
                response.raise_for_status()
                result = response.json()

                if not result.get("models"):
                    print("No models found")
                    return

                print("Available models:")
                for model in result["models"]:
                    modified_date = (
                        datetime.fromisoformat(
                            model.get("modified_at", "unknown date").replace(
                                "Z", "+00:00"
                            )
                        ).date()
                        if model.get("modified_at")
                        else "unknown date"
                    )
                    print(f"{model['name']:<15} - {modified_date}")
        except Exception as e:
            print(f"Error listing models: {e}")

    def do_save(self, arg: str) -> None:
        """Save last response to file: save <filename>"""
        if not arg:
            print("Please provide a filename")
            return

        if not self.last_response:
            print("No response to save")
            return

        try:
            with open(arg, "w", encoding="utf-8") as f:
                f.write(self.last_response)
            print(f"Response saved to {arg}")
        except Exception as e:
            print(f"Error saving response: {e}")

    def do_clear(self, arg: str) -> None:
        """Clear the screen"""
        os.system("cls" if os.name == "nt" else "clear")

    def do_exit(self, arg: str) -> bool:
        """Exit the program"""
        print("Goodbye!")
        return True

    def do_pull(self, arg: str) -> None:
        """Pull model from Ollama: pull <model_name>"""
        if not arg:
            print(f"Current model: {self.model}")
            return

        data = {"model": arg, "stream": True}
        url = urljoin(self.base_url, "/api/pull")

        try:
            with requests.post(url=url, json=data, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        update = json.loads(line)
                        status = update.get("status")
                        if status:
                            print(status)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
        except json.JSONDecodeError:
            print("Error parsing response")
        except Exception as e:
            print(f"Exception: {e}")

    def do_remove(self, arg: str) -> None:
        f"""Remove model from {self.host}: remove <model_name>"""
        if not arg:
            print(f"Current model: {self.model}")
            return

        url = urljoin(self.base_url, "/api/delete")
        data = {"model": arg}

        try:
            with requests.delete(url=url, json=data) as response:
                response.raise_for_status()
                result = response.json()
                print(result)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
        except json.JSONDecodeError:
            print("Error parsing response")
        except Exception as e:
            print(f"Exception: {e}")

    # Command aliases
    do_quit = do_exit
    do_ls = do_list

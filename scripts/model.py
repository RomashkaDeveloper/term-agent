import json
import requests
import subprocess

from typing import *
from scripts.config import Config
from scripts import __platform__, __shell__, __config_file__, __character__, __user__

class ChatManager(Config):
    def __init__(self, fast_start: bool = False, do_nothing: bool = False)  -> None:
        super().__init__()
        self.config = self.load_config(__config_file__)
        self.chats = self.config['chats']
        self.api_key = self.config['api_key']
        self.character_name = __character__ if not self.config["character_name"] else self.config["character_name"]
        self.user_name = __user__ if not self.config["user_name"] else self.config["user_name"]
        self.instruction = self.config['instruction'].format(character=self.character_name, user=self.user_name) if not self.config["custom_system_prompt"] else self.config["custom_system_prompt"]
        self.platform = __platform__
        self.shell = __shell__

        if do_nothing:
            return

        if fast_start:
            self.messages = self.fast_run()
        else:
            self.messages = self.choose_chat()

    def fast_run(self) -> List[Tuple[str, str]]:
        messages = [
            {
                "role": "system",
                "content": self.instruction
            }, {
                "role": "system",
                "content": f"User's shell: {self.shell}, user's system: {self.platform}"
            }
        ]

        return messages
        
    def choose_chat(self) -> List[Tuple[str, str]]:
        print("0. Start a new chat")

        if self.chats:
            for index, chat in enumerate(self.chats, start=1):
                if chat['character'] == self.character_name:
                    print(f"{index}. {chat['title']}")

        chat_index = int(input("Choose a number of a chat: ")) - 1
        if chat_index == -1:
            messages = [
                {
                    "role": "system",
                    "content": self.instruction
                }, {
                    "role": "system",
                    "content": f"User's shell: {self.shell}, user's system: {self.platform}"
                }
            ]
        else:
            messages = self.chats[chat_index]['messages']

        return messages

    def save(self) -> None:
        title = input('Type the title to save: ')
        existing_chat_index = next((index for index, chat in enumerate(self.config.get('chats', [])) 
                                    if chat['title'] == title and chat['character'] == self.character_name), None)

        if existing_chat_index is not None:
            # Update existing chat
            self.config['chats'][existing_chat_index]['messages'] = self.messages
            print(f"The conversation '{title}' has been updated successfully!")
        else:
            # Create new chat
            new_chat = {"title": title, "character": self.character_name, "messages": self.messages}
            self.config['chats'] = self.config.get("chats", []) + [new_chat]
            print(f"A new conversation '{title}' has been saved successfully!")

        self.save_config(CONFIG_FILE=__config_file__, config=self.config)

    def load(self) -> None:
        self.messages = self.choose_chat()

    def execute_command(self, command: str) -> str:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Ошибка выполнения команды {command}. Код ошибки: {result.returncode}")
                print(f"Сообщение об ошибке: {result.stderr}")
                return f"Error: {result.stderr}"
            
            output = result.stdout.strip()

            if output:
                print(output)
                return output
            else:
                return "Success"

        except FileNotFoundError:
            return f"Ошибка: команда {command} не найдена"
        except Exception as e:
            return f"Произошла непредвиденная ошибка: {e}"

class Model(ChatManager):
    # MODEL = "deepseek/deepseek-chat-v3-0324:free"
    MODEL = "deepseek/deepseek-chat-v3.1:free"
    # MODEL = "moonshotai/kimi-k2:free"
    # MODEL: str = "mistralai/mistral-small-3.1-24b-instruct:free"
    
    def __init__(self, fast_start: bool = False, do_nothing: bool = False) -> None:
        super().__init__(fast_start, do_nothing)
    
    def get_response(self, user_input: str) -> Generator[str, None, None]:
        if user_input:
            self.messages.append({"role": "user", "content": user_input})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.MODEL,
            "messages": self.messages,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "execute_command",
                        "description": "Execute a command in the user's shell",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "A command to execute in the user's shell"
                                }
                            },
                            "required": ["command"]
                        }
                    }
                }
            ],
            "stream": True,
            "max_new_tokens": 200,
            "temperature": 0.8
        }

        with requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True
        ) as response:
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return

            full_response: List[str] = []
            current_tool_call: Optional[Dict] = None

            for chunk in response.iter_lines():
                if not chunk:
                    continue

                chunk_str = chunk.decode("utf-8").replace('data: ', '').strip()
                if not chunk_str or chunk_str == "[DONE]":
                    continue

                try:
                    chunk_json = json.loads(chunk_str)
                    delta = chunk_json["choices"][0]["delta"]

                    # Собираем текстовый ответ
                    if "content" in delta and delta["content"] is not None:
                        full_response.append(delta["content"])
                        yield delta["content"]

                    # Собираем вызов функции
                    if "tool_calls" in delta:
                        for tool_call in delta["tool_calls"]:
                            if "function" in tool_call:
                                if not current_tool_call:
                                    current_tool_call = {
                                        "id": tool_call.get("id"),
                                        "type": "function",
                                        "function": {
                                            "name": tool_call["function"].get("name", ""),
                                            "arguments": ""
                                        }
                                    }
                                if "arguments" in tool_call["function"]:
                                    current_tool_call["function"]["arguments"] += tool_call["function"]["arguments"]

                except json.JSONDecodeError:
                    continue

            # Если есть вызов функции — обрабатываем его
            if current_tool_call:
                try:
                    arguments = json.loads(current_tool_call["function"]["arguments"])
                    command = arguments.get("command", "")
                    print(f"Executing command: {command}")
                    result = self.execute_command(command)

                    if full_response:
                        ai_response: str = "".join(full_response)
                        self.messages.append({"role": "assistant", "content": ai_response})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": current_tool_call["id"],
                        "content": result,
                    })

                    # Рекурсивно вызываем get_response, чтобы модель продолжила диалог
                    yield from self.get_response("")

                except json.JSONDecodeError as e:
                    print(f"Error parsing tool arguments: {e}")
                    self.messages.pop()
            elif full_response:
                ai_response: str = "".join(full_response)
                self.messages.append({"role": "assistant", "content": ai_response})
            else:
                print("No valid response or tool call!")
                self.messages.pop()

        print()
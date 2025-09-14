# import json
# import requests

# from typing import Generator, Dict, Any, List, Optional

# messages = [{
#     "role": "user",
#     "content": "Привет, а что ты умеешь?"
# }]
# # response = requests.post(
# #     url="https://openrouter.ai/api/v1/chat/completions",
# #     headers={
# #         "Authorization": "Bearer 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",
# #         "Content-Type": "application/json",
# #     },
# #     data=json.dumps({
# #         "model": "mistralai/mistral-small-3.1-24b-instruct:free",
# #         "messages": [
# #             {
# #                 "role": "user",
# #                 "content": "Вызови функцию execute_command, параметр: dir"
# #             }
# #         ],
# #         "tools": [
# #             {
# #                 "type": "function",
# #                 "function": {
# #                     "name": "execute_command",
# #                     "description": "Execute a command in the user's shell",
# #                     "parameters": {
# #                         "type": "object",
# #                         "properties": {
# #                             "command": {
# #                                 "type": "string",
# #                                 "description": "A command to execute in the user's shell"
# #                             }
# #                         },
# #                         "required": ["command"]
# #                     }

# #                 }
# #             }
# #         ],
# #         "stream": True
# #     })
# # )



# # # Красивый вывод JSON-ответа
# # if response.status_code == 200:
# #     try:
# #         response_json = response.json()
# #         print(json.dumps(response_json, indent=4, ensure_ascii=False))
# #     except json.JSONDecodeError as e:
# #         print(f"Ошибка декодирования JSON: {e}")
# #         print(f"Сырой ответ: {response.text}")
# # else:
# #     print(f"Ошибка: {response.status_code}")
# #     print(f"Сырой ответ: {response.text}")

# def execute_command(command: str) -> str:
#     import subprocess
#     try:
#         result = subprocess.run(
#             command,
#             shell=True,
#             check=True,
#             capture_output=True,
#             text=True
#         )
#         return result.stdout
#     except subprocess.CalledProcessError as e:
#         return f"Error: {e.stderr}"

# headers = {
#     "Authorization": f"Bearer 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",
#     "Content-Type": "application/json"
# }

# data = {
#     "model": "mistralai/mistral-small-3.1-24b-instruct:free",
#     "messages": messages,
#     "tools": [
#         {
#             "type": "function",
#             "function": {
#                 "name": "execute_command",
#                 "description": "Execute a command in the user's shell",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "command": {
#                             "type": "string",
#                             "description": "A command to execute in the user's shell"
#                         }
#                     },
#                     "required": ["command"]
#                 }

#             }
#         }
#     ],
#     "stream": True,
#     "max_new_tokens": 200,
#     "temperature": 0.8
# }

# with requests.post(
#     url="https://openrouter.ai/api/v1/chat/completions",
#     headers=headers,
#     json=data,
#     stream=True
# ) as response:
#     if response.status_code != 200:
#         print(f"Error: {response.status_code}")
#         exit()

#     full_response = []
#     current_tool_calls: List[Dict] = []
#     current_tool_call: Optional[Dict] = None

#     for chunk in response.iter_lines():
#         if not chunk:
#             continue

#         chunk_str = chunk.decode("utf-8").replace('data: ', '').strip()
#         if not chunk_str or chunk_str == "[DONE]":
#             continue

#         try:
#             chunk_json = json.loads(chunk_str)
#             delta = chunk_json["choices"][0]["delta"]

#             # Собираем текстовый ответ
#             if "content" in delta and delta["content"] is not None:
#                 full_response.append(delta["content"])
#                 print(delta["content"], end="")

#             # Собираем вызов функции
#             if "tool_calls" in delta:
#                 for tool_call in delta["tool_calls"]:
#                     if "function" in tool_call:
#                         if not current_tool_call:
#                             current_tool_call = {
#                                 "id": tool_call.get("id"),
#                                 "type": "function",
#                                 "function": {
#                                     "name": tool_call["function"].get("name", ""),
#                                     "arguments": ""
#                                 }
#                             }
#                         if "arguments" in tool_call["function"]:
#                             current_tool_call["function"]["arguments"] += tool_call["function"]["arguments"]

#         except json.JSONDecodeError:
#             continue

#     if current_tool_call:
#         try:
#             arguments = json.loads(current_tool_call["function"]["arguments"])
#             command = arguments.get("command", "")
#             print(f"Executing command: {command}")
#             result = execute_command(command)

#             # Добавляем вызов и результат в сообщения
#             messages.append({
#                 "role": "assistant",
#                 "content": None,
#                 "tool_calls": [current_tool_call]
#             })
#             messages.append({
#                 "role": "tool",
#                 "content": json.dumps({"result": result}),
#                 "tool_call_id": current_tool_call["id"]
#             })

#         except json.JSONDecodeError as e:
#             print(f"Error parsing tool arguments: {e}")
#             messages.pop()
#     elif full_response:
#         ai_response = "".join(full_response)
#         messages.append({"role": "assistant", "content": ai_response})
#     else:
#         print("No valid response or tool call!")
#         messages.pop()



# headers = {
#     "Authorization": f"Bearer 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",
#     "Content-Type": "application/json"
# }

# data = {
#     "model": "mistralai/mistral-small-3.1-24b-instruct:free",
#     "messages": messages,
#     "tools": [
#         {
#             "type": "function",
#             "function": {
#                 "name": "execute_command",
#                 "description": "Execute a command in the user's shell",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "command": {
#                             "type": "string",
#                             "description": "A command to execute in the user's shell"
#                         }
#                     },
#                     "required": ["command"]
#                 }

#             }
#         }
#     ],
#     "stream": True,
#     "max_new_tokens": 200,
#     "temperature": 0.8
# }

# with requests.post(
#     url="https://openrouter.ai/api/v1/chat/completions",
#     headers=headers,
#     json=data,
#     stream=True
# ) as response:
#     if response.status_code != 200:
#         print(f"Error: {response.status_code}")
#         exit()

#     full_response = []
#     current_tool_calls: List[Dict] = []
#     current_tool_call: Optional[Dict] = None

#     for chunk in response.iter_lines():
#         if not chunk:
#             continue

#         chunk_str = chunk.decode("utf-8").replace('data: ', '').strip()
#         if not chunk_str or chunk_str == "[DONE]":
#             continue

#         try:
#             chunk_json = json.loads(chunk_str)
#             delta = chunk_json["choices"][0]["delta"]

#             # Собираем текстовый ответ
#             if "content" in delta and delta["content"] is not None:
#                 full_response.append(delta["content"])
#                 print(delta["content"], end="")

#             # Собираем вызов функции
#             if "tool_calls" in delta:
#                 for tool_call in delta["tool_calls"]:
#                     if "function" in tool_call:
#                         if not current_tool_call:
#                             current_tool_call = {
#                                 "id": tool_call.get("id"),
#                                 "type": "function",
#                                 "function": {
#                                     "name": tool_call["function"].get("name", ""),
#                                     "arguments": ""
#                                 }
#                             }
#                         if "arguments" in tool_call["function"]:
#                             current_tool_call["function"]["arguments"] += tool_call["function"]["arguments"]

#         except json.JSONDecodeError:
#             continue

#     if current_tool_call:
#         try:
#             arguments = json.loads(current_tool_call["function"]["arguments"])
#             command = arguments.get("command", "")
#             print(f"Executing command: {command}")
#             result = execute_command(command)

#             # Добавляем вызов и результат в сообщения
#             messages.append({
#                 "role": "assistant",
#                 "content": None,
#                 "tool_calls": [current_tool_call]
#             })
#             messages.append({
#                 "role": "tool",
#                 "content": json.dumps({"result": result}),
#                 "tool_call_id": current_tool_call["id"]
#             })

#         except json.JSONDecodeError as e:
#             print(f"Error parsing tool arguments: {e}")
#             messages.pop()
#     elif full_response:
#         ai_response = "".join(full_response)
#         messages.append({"role": "assistant", "content": ai_response})
#     else:
#         print("No valid response or tool call!")
#         messages.pop()

import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "nvidia/nemotron-nano-9b-v2:free",
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ],
    
  })
)

# Красивый вывод JSON-ответа
if response.status_code == 200:
    try:
        response_json = response.json()
        print(json.dumps(response_json, indent=4, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        print(f"Сырой ответ: {response.text}")
else:
    print(f"Ошибка: {response.status_code}")
    print(f"Сырой ответ: {response.text}")
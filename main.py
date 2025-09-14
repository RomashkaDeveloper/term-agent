import sys

from typing import *
from scripts.model import Model

class Interface(Model):
    def __init__(self):
        super().__init__()

    def chat(self) -> None:
        while True:
            user_input = input("You: ")
            
            if user_input.lower().strip() == "/bye":
                return
            
            if user_input.lower().strip() == "/save":
                self.save()
            else:
                full_response = []

                for token in self.get_response(user_input):
                    full_response.append(token)
                    print(token, end="", flush=True)

def run(user_input: str) -> None:
    agent = Model(fast_start=True)

    full_response = []
    for token in agent.get_response(user_input):
        full_response.append(token)
        print(token, end="", flush=True)

def main():
    interface = Interface()

    if len(sys.argv) == 1:
        interface.chat()
        return
    
    if sys.argv[1] == "run":
        user_input = sys.argv[2]
        run(user_input)
        return
    
    if sys.argv[1] == "config":
        if len(sys.argv) == 3 | 2:
                raise "Передайте значение"
        if sys.argv[2] == "--api-key":
            api_key = sys.argv[3]
            interface.set_api_key(api_key) 
        elif sys.argv[2] == "--system-prompt":
            system_prompt = sys.argv[3]
            interface.set_system_prompt(system_prompt)
        elif sys.argv[2] == "--user-name":
            user_name = sys.argv[3]
            interface.set_user_name(user_name)
        elif sys.argv[2] == "--character-name":
            character_name = sys.argv[3]
            interface.set_user_name(character_name)

if __name__ == "__main__":
    main()

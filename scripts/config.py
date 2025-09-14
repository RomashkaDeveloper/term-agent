import os
import json

from typing import Dict, Any
from scripts import __config_file__, __character__, __user__

class Config:
    def __init__(self) -> None:
        self.config_file = __config_file__

        if not os.path.isfile(self.config_file):
            self.save_config(self.config_file, 
                {
                    "api_key": None,
                    "instruction": "Тебя зовут {character}, ты можешь выполнять команды в терминале путём вызова функции execute_command",
                    "chats": [],
                    "custom_system_prompt": None,
                    "character_name": None,
                    "user_name": None
                }
            )

        self.config = self.load_config(self.config_file)   

    def load_config(self, CONFIG_FILE: str) -> Dict[str, Any]:
        with open(CONFIG_FILE, 'r', encoding="utf-8-sig") as f:
            return json.load(f)
        
    def save_config(self, CONFIG_FILE: str, config: Dict[str, Any]) -> None:
        with open(CONFIG_FILE, 'w', encoding="utf-8-sig") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    def set_api_key(self, api_key: str) -> None:
        self.config["api_key"] = api_key
        self.save_config(self.config_file, self.config)

    def set_system_prompt(self, system_prompt: str) -> None:
        self.config["custom_system_prompt"] = system_prompt
        self.save_config(self.config_file, self.config)

    def set_character_name(self, character_name: str) -> None:
        self.config["character_name"] = character_name
        self.save_config(self.config_file, self.config)

    def set_user_name(self, user_name: str) -> None:
        self.config["user_name"] = user_name
        self.save_config(self.config_file, self.config)

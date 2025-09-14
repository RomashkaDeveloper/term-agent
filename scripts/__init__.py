import os
import sys

__home_dir__ = os.environ.get('HOME', "")

assert os.path.exists(__home_dir__), "Путь к домашней папке не найден"
config_path = os.path.join(__home_dir__, ".agent")
os.makedirs(config_path, exist_ok=True)
__config_file__ = os.path.join(config_path, "config.json")

__platform__ = sys.platform
__shell__ = os.environ.get("SHELL", "unknown") if os.name == "posix" else os.environ.get("COMSPEC", "unknown")
__user__ = "Рома"
__character__ = "Ева"

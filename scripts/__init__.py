import os
import sys

__version__: str = "0.1.0"
__shell__: str = os.environ.get("SHELL", "unknown") if os.name == "posix" else os.environ.get("COMSPEC", "unknown")
__platform__:str = sys.platform

if __platform__ in ["linux", "macos", "darwin"]:
    __home_dir__: str = os.environ.get('HOME', "")
elif __platform__ == "win32":
    __home_dir__: str = os.path.join(os.environ.get("HOMEDRIVE", ""), os.environ.get("HOMEPATH", ""))

assert os.path.exists(__home_dir__), "Путь к домашней папке не найден"
config_path: str = os.path.join(__home_dir__, ".agent")
os.makedirs(config_path, exist_ok=True)
__config_file__: str = os.path.join(config_path, "config.json")

__user__: str = "user"
__character__:str = "Ева"

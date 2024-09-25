import json
import os
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from core.config.config import InputConfig

CUR_DIR = Path(os.path.abspath(__file__)).parent.parent
CACHE_DIR = CUR_DIR/'cache'
CACHE_DIR.mkdir(exist_ok=True)
ENV_FILE_PATH = CUR_DIR / '.env'
CONFIG_FILE_PATH = CUR_DIR / 'input_config.json'

print(f"{CUR_DIR=}")
print(f"{ENV_FILE_PATH=}")
print(f"{CONFIG_FILE_PATH=}")
            
if not CONFIG_FILE_PATH.exists() or not ENV_FILE_PATH.exists():
    InputConfig().save(ENV_FILE_PATH, CONFIG_FILE_PATH)
    
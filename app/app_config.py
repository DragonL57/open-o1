import json
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

CUR_DIR = Path(os.path.abspath(__file__)).parent.parent
CACHE_DIR = CUR_DIR/'cache'
CACHE_DIR.mkdir(exist_ok=True)
ENV_FILE_PATH = CUR_DIR / '.env'
CONFIG_FILE_PATH = CUR_DIR / 'input_config.json'

print(f"{CUR_DIR=}")
print(f"{ENV_FILE_PATH=}")
print(f"{CONFIG_FILE_PATH=}")


@dataclass
class InputConfig:
    model_name: str = 'openai/gpt-3.5-turbo'
    model_api_key: str = 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    max_tokens: int = 1024
    max_steps: int = 10
    temperature: float = 0.2
    timeout: float = 30.0
    sleeptime: float = 0.0
    force_max_steps: bool = True

    @classmethod
    def load(cls, env_file=ENV_FILE_PATH, config_file=CONFIG_FILE_PATH):
        # Load env variables
        load_dotenv(env_file)
        env_dict = {
            'model_name': os.getenv('MODEL_NAME', 'not set'),
            'model_api_key': os.getenv('MODEL_API_KEY', 'not set')
        }

        # Load config JSON
        with open(config_file, 'r') as f:
            config_dict = json.load(f)

        # Combine both
        return cls(
            model_name=env_dict.get('model_name', cls.model_name),
            model_api_key=env_dict.get('model_api_key', cls.model_api_key),
            max_tokens=config_dict.get('max_tokens', cls.max_tokens),
            max_steps=config_dict.get('max_steps', cls.max_steps),
            temperature=config_dict.get('temperature', cls.temperature),
            timeout=config_dict.get('timeout', cls.timeout),
            sleeptime=config_dict.get('sleeptime', cls.sleeptime),
            force_max_steps=config_dict.get('force_max_steps', cls.force_max_steps)
        )

    def save(self, env_file=ENV_FILE_PATH, config_file=CONFIG_FILE_PATH):
        # Read existing env content if it exists
        env_vars = {}
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip():  # Ignore empty lines
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
        
        # Update the necessary keys
        env_vars['MODEL_API_KEY'] = self.model_api_key
        env_vars['MODEL_NAME'] = self.model_name

        # Write back to the .env file
        with open(env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f'{key}={value}\n')

        # Save other parameters to input_config.json
        config_dict = {
            'max_tokens': self.max_tokens,
            'max_steps': self.max_steps,
            'temperature': self.temperature,
            'timeout': self.timeout,
            'sleeptime': self.sleeptime,
            'force_max_steps': self.force_max_steps
        }
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=4)
            
if not CONFIG_FILE_PATH.exists() or not ENV_FILE_PATH.exists():
    InputConfig().save()
    
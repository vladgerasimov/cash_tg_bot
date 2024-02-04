from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

root_dir = Path.cwd()


class BotSettings(BaseSettings):
    bot_token: str = ""
    db_url: str = ""
    menu_buttons: list[str] = []

    @classmethod
    def from_yaml(cls, yaml_path: str | Path):
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
        return cls(**config)


bot_settings = BotSettings.from_yaml(root_dir / "configs" / "bot_settings.yaml")

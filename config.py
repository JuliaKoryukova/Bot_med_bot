# config.py

from dataclasses import dataclass
from typing import List
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: List[int]

@dataclass
class Config:
    tg_bot: TgBot

# Функция для чтения .env
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=env.list("ADMIN_IDS")
        )
    )
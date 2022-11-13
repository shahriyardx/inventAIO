from os import environ

from dotenv import load_dotenv

from src import bot

load_dotenv(".env")
bot.run(environ["TOKEN"])

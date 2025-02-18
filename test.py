import telebot
from telebot.types import *
from datetime import datetime
# Your bot's token
TOKEN = '7404500425:AAHxUetTSf1iBMyyF3XbyqbUoEwpOdaq8J4'

from kvsqlite.sync import Client
from datetime import datetime


users = Client('./db/ok.sqlite')
print(users.keys())
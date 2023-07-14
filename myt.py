import os
import asyncio
from telethon import TelegramClient, events 
from jdatetime import datetime as jdatetime

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

tasks = {}
states = {}

def reset_state(user_id):
  states[user_id] = {
    'step': 'subject',
    'subject': None,
    'year': None,
    'month': None,
    'day': None, 
    'hour': None,
    'minute': None,
    'repeat': None
  }

@client.on(events.NewMessage(pattern='/new'))
async def new_task(event):
  reset_state(event.sender_id)
  await event.respond('موضوع یادآوری رو وارد کن:')

@client.on(events.NewMessage())  
async def handle_subject(event):
  state = states[event.sender_id]

  if state['step'] != 'subject':
    return

  state['subject'] = event.raw_text
  state['step'] = 'year'

  await event.respond('سال یادآوری رو به صورت 4 رقمی وارد کن:')

@client.on(events.NewMessage(pattern=r'\d{4}'))
async def handle_year(event):
  state = states[event.sender_id]

  if state['step'] != 'year':
    return

  try:
    year = int(event.raw_text)
  except ValueError:
    await event.respond('سال وارد شده معتبر نیست')
    return
  
  state['year'] = year
  state['step'] = 'month'

  await event.respond('ماه یادآوری رو به صورت عدد وارد کن (1-12):')

@client.on(events.NewMessage(pattern=r'\d{1,2}'))
async def handle_month(event):

  state = states[event.sender_id]

  if state['step'] != 'month':
    return

  month = int(event.raw_text)

  if month < 1 or month > 12:
    await event.respond('ماه وارد شده معتبر نیست')
    return

  state['month'] = month
  state['step'] = 'day'

  await event.respond('روز یادآوری رو وارد کن:')

# Other handlers

@client.on(events.NewMessage(pattern='/list'))
async def list_tasks(event):
  # List tasks

async def check_reminders():
  # Check and send reminders

client.loop.create_task(check_reminders()) 
client.run_until_disconnected()

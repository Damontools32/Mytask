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

@client.on(events.NewMessage(pattern=r'\d{1,2}')) 
async def handle_day(event):
  state = states[event.sender_id]

  if state['step'] != 'day':
    return

  day = int(event.raw_text)
  if day < 1 or day > 31: 
    await event.respond('روز وارد شده معتبر نیست')
    return

  state['day'] = day
  state['step'] = 'hour'

  await event.respond('ساعت یادآوری رو به صورت عدد وارد کن (0-23):')

@client.on(events.NewMessage(pattern=r'\d{1,2}'))
async def handle_hour(event):
  state = states[event.sender_id]

  if state['step'] != 'hour':
    return

  hour = int(event.raw_text)
  if hour < 0 or hour > 23:
    await event.respond('ساعت وارد شده معتبر نیست')
    return

  state['hour'] = hour
  state['step'] = 'minute'

  await event.respond('دقیقه یادآوری رو وارد کن:')  

@client.on(events.NewMessage(pattern=r'\d{1,2}'))
async def handle_minute(event):
  state = states[event.sender_id]

  if state['step'] != 'minute':
    return

  minute = int(event.raw_text)
  if minute < 0 or minute > 59:
    await event.respond('دقیقه وارد شده معتبر نیست')
    return

  state['minute'] = minute
  state['step'] = 'repeat'  

  await event.respond('تعداد تکرار یادآوری رو وارد کن:')

@client.on(events.NewMessage(pattern=r'\d+'))
async def handle_repeat(event):
  state = states[event.sender_id]

  if state['step'] != 'repeat':
    return

  repeat = int(event.raw_text)

  time = jdatetime(
    year=state['year'], 
    month=state['month'],
    day=state['day'],
    hour=state['hour'],
    minute=state['minute']
  )

  task = (state['subject'], time, repeat)
  tasks[event.sender_id].append(task)

  await event.respond('یادآوری شما ثبت شد')
  reset_state(event.sender_id)

@client.on(events.NewMessage(pattern='/list'))  
async def list_tasks(event):
  user_tasks = tasks.get(event.sender_id, [])

  if not user_tasks:
    await event.respond('شما هنوز هیچ یادآوری ثبت نکردید')
    return

  message = 'لیست یادآوری‌های شما:\n\n'

  for i, task in enumerate(user_tasks):
    message += f'{i+1}. {task[0]} - {task[1]}\n'

  await event.respond(message) 

async def check_reminders():
  while True:
    now = jdatetime.now()

    for user_id, user_tasks in tasks.items():
      for task in user_tasks:
        subject, time, repeat = task
        if now > time and repeat > 0:
          await client.send_message(user_id, f'یادآوری: {subject}')
          
          if repeat > 1:
            task = (subject, time, repeat-1)  
          else:
            user_tasks.remove(task)

    await asyncio.sleep(60)

client.loop.create_task(check_reminders())
client.run_until_disconnected()

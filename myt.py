import os
import asyncio
from telethon import TelegramClient, events
from jdatetime import datetime as jdatetime

# Fetch environment variables
api_id = os.getenv('TELEGRAM_API_ID', 'your_default_api_id')
api_hash = os.getenv('TELEGRAM_API_HASH', 'your_default_api_hash')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN', 'your_default_bot_token')

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

tasks = {}
states = {}

def reset_state(user_id):
    states[user_id] = {
        'step': 'subject',
        'subject': None,
        'time': None,
        'repeat': None,
    }

@client.on(events.NewMessage(pattern='/new'))
async def new_task(event):
    reset_state(event.sender_id)
    await event.respond('موضوع یادآوری رو وارد کن:')

@client.on(events.NewMessage)
async def handle_message(event):
    state = states.get(event.sender_id)
    if not state:
        return

    if state['step'] == 'subject':
        state['subject'] = event.raw_text
        state['step'] = 'year'
        await event.respond('سال یادآوری رو وارد کن (به فرمت YYYY):')
    elif state['step'] == 'year':
        try:
            year = int(event.raw_text)
            if year < 1300 or year > 1500:
                raise ValueError
            state['time'] = str(year)
            state['step'] = 'month'
            await event.respond('ماه یادآوری رو وارد کن (به فرمت MM):')
        except ValueError:
            await event.respond('لطفاً یک سال معتبر وارد کنید (بین 1300 تا 1500):')
            return
    # rest of your code here

    # Don't forget to validate month, day, hour and repeat count similarly 

async def task_scheduler():
    while True:
        now = jdatetime.now()
        for user_id, user_tasks in tasks.items():
            for task in user_tasks:
                subject, time, repeat = task
                if now > time and repeat > 0:
                    await client.send_message(user_id, f'یادآوری: {subject}')
                    if repeat > 1:
                        task = (subject, time, repeat - 1)
                    else:
                        user_tasks.remove(task)
        await asyncio.sleep(60)  # check every minute

client.loop.create_task(task_scheduler())
client.run_until_disconnected()

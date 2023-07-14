from telethon import TelegramClient, events
from jdatetime import datetime as jdatetime
import asyncio

api_id = 'your_api_id'
api_hash = 'your_api_hash'
bot_token = 'your_bot_token'

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
        state['time'] = event.raw_text
        state['step'] = 'month'
        await event.respond('ماه یادآوری رو وارد کن (به فرمت MM):')
    elif state['step'] == 'month':
        state['time'] += '/' + event.raw_text
        state['step'] = 'day'
        await event.respond('روز یادآوری رو وارد کن (به فرمت DD):')
    elif state['step'] == 'day':
        state['time'] += '/' + event.raw_text
        state['step'] = 'hour'
        await event.respond('ساعت یادآوری رو وارد کن (به فرمت 24 ساعته HH):')
    elif state['step'] == 'hour':
        state['time'] += ' ' + event.raw_text
        state['step'] = 'repeat'
        await event.respond('تعداد دفعات تکرار یادآوری رو وارد کن:')
    elif state['step'] == 'repeat':
        state['repeat'] = int(event.raw_text)
        state['time'] = jdatetime.strptime(state['time'], '%Y/%m/%d %H')
        tasks[event.sender_id].append((state['subject'], state['time'], state['repeat']))
        reset_state(event.sender_id)
        await event.respond('یادآوری اضافه شد!')

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
client.run_until_disconnected()￼Enter

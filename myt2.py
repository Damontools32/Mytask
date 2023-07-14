import os
import subprocess
from telethon import TelegramClient, events

api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
bot_token = 'YOUR_BOT_TOKEN'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

@client.on(events.NewMessage)
async def handle_new_message(event):
    if event.message.video:
        video = event.message.video
        video_path = await client.download_media(video)
        output_path = video_path.rsplit('.', 1)[0] + '_compressed.mp4'
        
        command = f'ffmpeg -i {video_path} -vcodec libx265 -crf 45 -preset superfast {output_path}'
        subprocess.run(command, shell=True)
        
        try:
            if os.path.exists(output_path):
                await client.send_file(event.chat_id, output_path, caption="فایل ویدیوی فشرده شده آماده است.")
            else:
                print(f"Compressed video file does not exist: {output_path}")
        finally:
            # حذف فایل‌های دانلود شده و تبدیل شده
            if os.path.exists(video_path): 
                os.remove(video_path)
                
            if os.path.exists(output_path): 
                os.remove(output_path)

client.run_until_disconnected()

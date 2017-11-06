import json
import subprocess

if __name__ == '__main__':
    with open('config.json') as f:
        config = json.load(f)

    host = config.get('host')
    telegram_chat_id = config.get('chat_id', 0)
    subprocess.run(['./script/build.sh', host, str(telegram_chat_id)])

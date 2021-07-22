import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import blocks
import time
import get_datetime
import requests
import json

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
#client2 = slack.WebClient(token=os.environ['BOT_TOKEN'])
BOT_ID = client.api_call('auth.test')['user_id']

#@app.before_first_request
def check_status():
    while(True):
        history = client.conversations_history(channel="C028A23ULRM")
        for message in history.get('messages'):
            user = message.get('user')
            if(user != BOT_ID):
                ts = message.get('ts')
                bool = get_datetime.get_datetime(ts)
                if bool:
                    client.chat_postMessage(channel="C028A23ULRM", blocks=blocks.prompt)
                break
        time.sleep(10)

def send_survey():
    res = client.chat_postMessage(channel="C028A23ULRM", blocks=blocks.button)
    print(res)

@slack_event_adapter.on('member_joined_channel')
def message(payLoad):
    event = payLoad.get('event', {})
    channel_id = event.get('channel')
    user = event.get('user')
    name = client.users_info(user=user).get('user').get('name')
    post_blocks = blocks.onboard_blocks
    post_blocks[0].get('text')['text'] = "Hey " + name + "! 👋 I'm Pretzel. I'm here to help connect you with other colleagues and mentors!\nYou can:"
    client.chat_postMessage(channel=channel_id, blocks=post_blocks)
    #check_status()
    #return

@slack_event_adapter.on('message')
def message(payLoad):
    event = payLoad.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    message_ts = event.get('ts')
    if BOT_ID != user_id:
        final_dict = {}
        final_dict['channel_id'] = channel_id
        final_dict['user_id'] = user_id
        final_dict['text'] = text
        final_dict['message_ts'] = message_ts
        print(final_dict)

@slack_event_adapter.on('user_change')
def message(payLoad):
    # event =payLoad.get('event', {})
    # user = event.get('user')
    # id = user.get('id')
    # user_presence = client.users_getPresence(user=id).get('presence')
    # print(user_presence)
    pass

@app.route('/suggest', methods=['POST', 'GET'])
def suggest():
    data = request.form
    #check_status()
    return Response(), 200

@app.route('/endpoint', methods=['POST', 'GET'])
def func():
    payload = request.form.to_dict()['payload']
    payload = payload.replace('false', 'False')
    payload = payload.replace('null', 'None')
    payload = payload.replace('true', 'True') 
    payload = eval(payload)
    user = payload['user']
    id = user['id']
    username = user['username']
    container = payload['container']
    channel_id = container['channel_id']
    actions = payload['actions']
    value = actions[0]['value']
    final_dict = {}
    final_dict['kerboros_id'] = id
    final_dict['username'] = username
    final_dict['chat_id'] = channel_id
    final_dict['chat_value'] = value
    print(final_dict)
    # final_dict = json.dumps(final_dict)
    # r = requests.post(url = 'https://obeebms169.execute-api.us-east-2.amazonaws.com/dev', data = final_dict)
    # print(r.text)
    return Response(), 200

if __name__ == "__main__":
    client.chat_postMessage(channel="C028A23ULRM", text="https://dev.d3tbz96df27e6u.amplifyapp.com/feedback/")
    # client.conversations_create(name='python')
    # channels = client.conversations_list().get('channels')
    # for channel in channels:
    #     if channel.get('name') == 'python':
    #         client.conversations_invite(channel=channel.get('id'),users='U02795BEL6T')
    app.run(debug=True)
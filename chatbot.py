import os
from slack import WebClient
from slack.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from movieLens import makeExplanation
import time
import re

SLACK_BOT_TOKEN='xoxb-151863340775-1128159758867-xdMHtI3gC7lhxOl0sNRjhGy1'
SLACK_SIGNING_SECRET='1586eafbc98a6195ceb294b989e32165'
my_channel = 's2021706-dev'
my_message = 'goodbye'
# Initialize a Web API client
slack_web_client = WebClient(token=SLACK_BOT_TOKEN)

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events")

explanation_maker=makeExplanation()

def get_res_id(text):
    if "recommend" in text:
        return 1
    elif "choose" in text:
        return 2
    elif "yes" in text or "try" in text:
        return 3
    else:
        return 4


current_user_id=1
def make_response(res_id,text,current_user_id):
    if res_id==1:
        return "Okay, please input your user id. "
    elif res_id==2:
        movie_name=re.findall(r"choose (.*)",text)[0]
        return explanation_maker.make_explanation(movie_name,current_user_id)
    elif res_id==3:
        return "Okay, thank you for your trust."
    else:
        user_id=int(re.findall(r'\d+',text)[0])
        current_user_id=user_id
        message1=explanation_maker.show_preference(user_id)
        message2=explanation_maker.make_recommendation(user_id)
        message=message1+'\n'+message2
        return message



@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # if message.get("subtype") is None and "goodbye" in message.get('text'):

    if message.get("subtype") is None and message["user"]=='U01426ES9CZ':
        # my_message = "Hello <@%s>! :tada:" % message["user"]
        text=message.get('text')
        response_id=get_res_id(text)
        my_message=make_response(response_id,text,current_user_id)
        response = slack_web_client.chat_postMessage(
            channel = message["channel"],
            text = my_message)



slack_events_adapter.start(port=3000)
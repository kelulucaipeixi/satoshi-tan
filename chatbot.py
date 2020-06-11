import os
from slack import WebClient
from slack.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from movieLens import makeExplanation
import time
import re

my_channel = 's2021706-dev'
my_message = 'goodbye'
# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# Our app's Slack Event Adapter for receiving actions via the Events API
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events")

explanation_maker=makeExplanation()

def get_res_id(text):
    if "recommend" in text:
        return 1
    elif "choose" in text:
        return 2
    elif "yes" in text or "try" in text or "ok" in text:
        return 3
    elif len(text)<3:
    	return 4
    else:
        return 5


current_user_id=1
current_feature_id=0
def make_response(res_id,text,current_user_id):
    global current_feature_id
    if res_id==1:
        return "Okay, please input your user id. "
    elif res_id==2:
        movie_name=re.findall(r"choose (.*)",text)[0]
        out,current_feature_id=explanation_maker.make_explanation(movie_name,current_user_id)
        return out
    elif res_id==3:
        explanation_maker.change_feature(current_user_id,current_feature_id)
        return "Okay, thank you for your trust."
    elif res_id==4:
        user_id=int(re.findall(r'\d+',text)[0])
        current_user_id=user_id
        message1=explanation_maker.show_preference(user_id)
        message2=explanation_maker.make_recommendation(user_id)
        message=message1+'\n'+message2
        return message
    else:
    	return "Sorry, I am a movie recommend bot, I can't answer your questions not related to movie recommendation."



@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    # if message.get("subtype") is None and "goodbye" in message.get('text'):
# 	if message.get("subtype") is None and message["user"]=='U01426ES9CZ'
    if message.get("subtype") is None and message["user"]!='U01556TH79A':
        # my_message = "Hello <@%s>! :tada:" % message["user"]
        text=message.get('text')
        response_id=get_res_id(text)
        my_message=make_response(response_id,text,current_user_id)
        response = slack_web_client.chat_postMessage(
            channel = message["channel"],
            text = my_message)



slack_events_adapter.start(port=3000)
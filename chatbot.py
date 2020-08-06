import os
from slack import WebClient
# from slackclient import SlackClient
from slack.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from movieLens import makeExplanation
import time
import re
import Levenshtein
import json
import requests
from flask import Flask,request

app=Flask(__name__)
is_all_name_confirmed=False
my_channel = ''
my_message = 'goodbye'
# chatbot_id = 'U01556TH79A'
chatbot_id = 'U0188FRH2J1'
revised_names=[] #the revised names of user favorite features
not_recommend_lists=[] # names of movies that should not be recommended to user
count=-1 #decide which step chatbot should take
user_favo_feats=[] # names of user favorite features
user_favo_feats_ids=[] 
feat_indice=0 #the pointer to feature for user to score
movie_indice=1
points=[] #the points of user favorite features
best4item_names=[]
# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN2'])
# Our app's Slack Event Adapter for receiving actions via the Events API
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET2'], "/slack/events",app)

explanation_maker=makeExplanation()

def get_res_id(text):
    global count
    global is_all_name_confirmed
    count += 1
    print("count:",count)
    if count == 2 and "no" in text or "No" in text:
        count = 0
        is_all_name_confirmed = False
    if count >= 4 and "no" in text or "No" in text:
        count = 0
    return count

def make_responses(res_id,text):
    global user_favo_feats
    global user_favo_feats_ids
    global count
    global not_recommend_lists
    global points
    global attachment_json
    global best4item_names
    if res_id == 0:
        return "Please tell me the name of some your favorite movies, just input the name and use comma to seperate."
    if res_id == 1:
        names=text.split(',')
        return check_names(names)
    if res_id == 2:
        ans,user_favo_feats_ids,user_favo_feats=explanation_maker.make_explanation(revised_names)
        print(user_favo_feats)
        attachment_json[0]['text']="Please give the score to the feature: "+user_favo_feats[0]
        return ans
    if res_id == 3:
        # points=text2list_feat_value(text)
        # for i in points:
        #     if i>5.0 or i<0:
        #         count-=1
        #         return "Please give score between 0.0-5.0"
        # if len(points)!=len(user_favo_feats):
        #     count-=1
        #     return "Please give score for all the features!"
        favo_feats=dict(zip(user_favo_feats_ids,points))#{'feat1id':'#score','feat2id':'#score'...}
        ans, best4item_names = explanation_maker.make_recommendation(favo_feats,not_recommend_lists)
        not_recommend_lists += best4item_names
        attachment_result_scorer[0]['text'] = "Please tell me the probability you will watch the movie "+best4item_names[0]
        return ans
    else:
        return "Thank you!"
#make user score all the features
json_file=open('feature_scorer.json','r')
attachment_json=json.load(json_file)
#give user several revised name to confirm what user said
json_file2=open('name_reviser.json','r')
attachment_name_reviser=json.load(json_file2)
#make user score the recommended movies finally
json_file3=open('result_scorer.json','r')
attachment_result_scorer=json.load(json_file3)
@slack_events_adapter.on("message")
def handle_message(event_data):
    global feat_indice
    global my_channel
    # if "attachments" in event_data["event"]:
    #     print("attachments",event_data["event"]["attachments"])
    message = event_data["event"]
    text=message.get('text') 
    

    #the agent will continue to give out multiselect-box after show user favorite features.  
    if text is not None and "Could you please score for all the features listed above? The more you like the feature, you should give higher score." in text:
        feat_indice+=1
        response = slack_web_client.chat_postMessage(
            channel = message["channel"],
            attachments = attachment_json)
    if text is not None and "Thank you for score all the features!" in text:
        response_id=get_res_id(text)     
        my_message=make_responses(response_id,text)   
        response = slack_web_client.chat_postMessage(
            channel = message["channel"],
            text = my_message)
    if text is not None and "Please tell me the probability you will watch these movie." in text:
        response = slack_web_client.chat_postMessage(
            channel = my_channel,
            attachments = attachment_result_scorer)
    if message.get("subtype") is None and message["user"]!=chatbot_id:
        # my_message = "Hello <@%s>! :tada:" % message["user"]
        my_channel=message["channel"]
        response_id=get_res_id(text)
        my_message=make_responses(response_id,text)
        if response_id == 1 and is_all_name_confirmed == False:
            pass
        else:        
            response = slack_web_client.chat_postMessage(
                channel = message["channel"],
                text = my_message)
                
            

        # slack_client.api_call("chat.postMessage",channel=message["channel"],text=my_message)
@app.route("/")
def hello():
    return "hello there!"
@app.route("/slack/message_actions",methods=['POST'])
def message_actions():
    global feat_indice
    global revised_names
    global points
    global count
    global movie_indice
    global best4item_names
    form_json = json.loads(request.form["payload"])
    if form_json['callback_id']=='revise_name':
        revised_name=form_json['actions'][0]['selected_options'][0]['value']
        for i in range(len(revised_names)):
            if revised_names[i]=='tmp':
                revised_names[i]=revised_name
                break
        if 'tmp' not in revised_names:
            slack_web_client.chat_postMessage(
                # channel = "C014DCSKMU0",
                channel = my_channel,
                text = check_names(revised_names))
        return ''
    elif form_json['callback_id']=='make_score':
        selection = int(form_json["actions"][0]["value"])
        points.append(selection)
        print(feat_indice)
        if feat_indice == len(user_favo_feats):
            slack_web_client.chat_postMessage(
                channel = my_channel,
                text = "Thank you for score all the features! Please wait and I'll recommend you some movies.")
            return user_favo_feats[feat_indice-1]+": "+str(selection)
        if feat_indice < len(user_favo_feats):
            feat_indice += 1
            text_curr="Please give the score to the feature: "+user_favo_feats[feat_indice-1]
            attachment_json[0]['text']=text_curr
            slack_web_client.chat_postMessage(
                channel = my_channel,
                attachments = attachment_json)
        return user_favo_feats[feat_indice-2]+": "+str(selection)
    else:
        if movie_indice >= 4:
            return best4item_names[movie_indice-1]+": "+form_json['actions'][0]['selected_options'][0]['value']
        print(best4item_names)
        attachment_result_scorer[0]['text']="Please tell me the probability you will watch the movie "+best4item_names[movie_indice]
        movie_indice+=1
        slack_web_client.chat_postMessage(
                channel = my_channel,
                attachments = attachment_result_scorer)
        return best4item_names[movie_indice-2]+": "+form_json['actions'][0]['selected_options'][0]['value']
        
    



def check_name(movie_name):
    movie_name=movie_name.lower()
    max_leven=0
    true_name=''
    for name in explanation_maker.i_t_map:
        #explanation_make.i_t_map中第一个元素是0，后面都是字符串（movie name)
        if name != 0:
            name=name.lower()
            dis=Levenshtein.ratio(name,movie_name)
            #the format of name in dataset is with year, like titanic (1997), use name[:-7] can reduce the year.
            dis2=Levenshtein.ratio(name[:-7],movie_name)
            if dis > max_leven:
                max_leven=dis
                true_name=name
            if dis2 > max_leven:
                max_leven=dis2
                true_name=name
    # print(true_name)
    # print(max_leven)
    if max_leven < 0.8:
        attachment_name_reviser[0]['text']='There are several movies have similar name with '+movie_name+' , please choose the one you refer.'
        attachment_name_reviser[0]['actions'][0]['options']=[]
        for name in explanation_maker.i_t_map:
            if name!=0:
                name=name.lower()
                if movie_name in name:
                    tmp_dict={"text":name,"value":name}
                    attachment_name_reviser[0]['actions'][0]['options'].append(tmp_dict)
        slack_web_client.chat_postMessage(
            channel = "D01556U7FEY",
            attachments = attachment_name_reviser)
        true_name = "tmp"   
    return true_name
def check_names(names):
    global is_all_name_confirmed
    res="Let me make sure that "
    global revised_names
    global not_recommend_lists
    revised_names=[]
    for name in names:
        revised_name=check_name(name)
        res=res+revised_name+","
        revised_names.append(revised_name)
        not_recommend_lists.append(revised_name)
    res=res[:-1]+" are your favorite movies. Tell us yes if it is true or no if it is false."
    # print(revised_names)
    for i in revised_names:
        if i == 'tmp':
            break
        if i == revised_names[-1]:
            is_all_name_confirmed=True
    print(revised_names)
    return res
def text2list_feat_value(text):
    a=text.replace(' ','')
    b=a.split(',')
    c=[float(i) for i in b]
    return c

if __name__ == '__main__':
    # slack_events_adapter.start(port=3000)
    app.run(port=3000)
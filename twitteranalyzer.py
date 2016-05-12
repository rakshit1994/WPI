import sys
import requests
import json
import twitter
import details as config 
import csv
import os

def convert_status_to_pi_content_item(s):
    # My code here
    return { 
        'userid': str(s.user.id), 
        'id': str(s.id), 
        'sourceid': 'python-twitter', 
        'contenttype': 'text/plain', 
        'language': s.lang, 
        'content': s.text, 
        'created': 1000 * s.GetCreatedAtInSeconds(),
        'reply': (s.in_reply_to_status_id == None),
        'forward': False
    }
    

def doProcessing(key,q):
  twitter_api = twitter.Api(consumer_key=key['consumerKey'],
                    consumer_secret=key['consumerSecret'],
                    access_token_key=key['accessToken'],
                    access_token_secret=key['accessSecret'],
                    debugHTTP=True)
  print("doProcessing starts")



  while not q.empty():
    handle=q.get()
    print(handle+"file building starts")
    output_file=open('json/'+handle+'.json','w')
    statuses = twitter_api.GetUserTimeline(screen_name=handle,
                      count=200,
                      include_rts=False)

    pi_content_items_array = map(convert_status_to_pi_content_item, statuses)
    pi_content_items = { 'contentItems' : pi_content_items_array }

    r = requests.post(config.pi_url + '/v2/profile', 
    			auth=(config.pi_username, config.pi_password),
    			headers = {
                    'content-type': 'application/json',
                    'accept': 'application/json'
                },
    			data=json.dumps(pi_content_items)
    		)
    #print("Profile Request sent. Status code: %d, content-type: %s" % (r.status_code, r.headers['content-type']))
    output_file.write(r.text)
    output_file.close()

  q.task_done()
  return "Success in writing to file!"
  

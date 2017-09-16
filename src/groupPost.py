import json
import facebook

def makePost(msg):
    with open('configs/fbook.json') as data_file:    
        data = json.load(data_file)
    access_token = data['fb_access_token']
    #fb_group_id = data['group_id'] 
    fb_group_id = data['test_group_id'] #test group
    #extend access token using https://developers.facebook.com/tools/debug/accesstoken/
    graph = facebook.GraphAPI(access_token)
    graph.put_object(fb_group_id, 'feed', message=msg)

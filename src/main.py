import json

import groupPost
import scrapeESPN


def main_keeper():
    with open('configs/main.json') as data_file:    
        data = json.load(data_file)
    league_id = data['keeper']['league_id']
    year = data['keeper']['year']
    swid = data['keeper']['swid']
    espn_s2 = data['keeper']['espn_s2']
    msg = 'Keeper League Weekly Trophies \n'
    msg = msg + scrapeESPN.get_data(league_id, year, swid, espn_s2)
    groupPost.makePost(msg)
    
def main_regular():
    with open('configs/main.json') as data_file:    
        data = json.load(data_file)
    league_id = data['regular']['league_id']
    year = data['regular']['year']
    swid = data['regular']['swid']
    espn_s2 = data['regular']['espn_s2']
    msg = 'Regular League Weekly Trophies \n'
    msg = msg + scrapeESPN.get_data(league_id, year, swid, espn_s2)
    groupPost.makePost(msg)

def main():
    main_keeper()
    main_regular()


def lambda_handler(event, context):
    main()

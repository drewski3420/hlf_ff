import requests
import json

def fetch_draft():
    league_id = 376
    year = 2017
    ENDPOINT = "http://games.espn.com/ffl/api/v2/"
    params = {
        'leagueId': league_id,
        'seasonId': year,
        'count': '5000'
    }
    cookies = {
        'espn_s2': 'AEAVtZauJ4zy8W0ObxWUCPflgNG1L3JWrh%2FGekHt1%2BeDtDHtoE9lk0vh6Fo4zM1DyIAR5fbMebEWTSLYJq72%2BNhpdp0XOgakjVxoezQdANRPFEVroOXvs%2FuHClGfsb%2BHkpEwllVI4am0ylQ0vg3MyzlbxrzibnG8D5PBjjb3woXIJTGuiibUm2xi5Oz8Ro%2Fnsq3D%2FHbawtUe3xLueWbtFr9STPN%2F5UUKVvEl4qlVg47gtYLnUZJhEVjjP0EofmDopIMF6osWdhRMlqhwpNL3j8Kd',
        'SWID': '{D66C65CC-0127-4004-B04C-5242EAB6412D}'
    }
    r = requests.get('%srecentActivity' % (ENDPOINT, ), params=params, cookies=cookies)
    data = r.json()
    return data
    
def fetch_player(player_id):
    league_id = 376
    year = 2017
    ENDPOINT = "http://games.espn.com/ffl/api/v2/"
    params = {
        'leagueId': league_id,
        'seasonId': year,
        'playerId': player_id
    }
    cookies = {
        'espn_s2': 'AEAVtZauJ4zy8W0ObxWUCPflgNG1L3JWrh%2FGekHt1%2BeDtDHtoE9lk0vh6Fo4zM1DyIAR5fbMebEWTSLYJq72%2BNhpdp0XOgakjVxoezQdANRPFEVroOXvs%2FuHClGfsb%2BHkpEwllVI4am0ylQ0vg3MyzlbxrzibnG8D5PBjjb3woXIJTGuiibUm2xi5Oz8Ro%2Fnsq3D%2FHbawtUe3xLueWbtFr9STPN%2F5UUKVvEl4qlVg47gtYLnUZJhEVjjP0EofmDopIMF6osWdhRMlqhwpNL3j8Kd',
        'SWID': '{D66C65CC-0127-4004-B04C-5242EAB6412D}'
    }
    r = requests.get('%splayerInfo' % (ENDPOINT, ), params=params, cookies=cookies)
    data = r.json()
    try:
        return data['playerInfo']['players'][0]['player']['firstName'] + ' ' + data['playerInfo']['players'][0]['player']['lastName']
    except:
        pass
    
        

data = fetch_draft()
draft = {}
for row in data['items']:
    try:
        if row['pendingMoveItems'][0]['moveTypeId'] == 5:
            player_id =  row['pendingMoveItems'][0]['playerId']
            team_id = row['pendingMoveItems'][0]['toTeamId']
            selection =  row['pendingMoveItems'][0]['draftOverallSelection']
            draft[selection] = {
                'team_id': team_id,
                'player_id': player_id,
                'player': fetch_player(player_id)
            }
    except:
		pass

#for pick in draft:
#   print pick['team_id']
for pick, info in draft.items():
    print 'Pick ' + str(pick) + ': Player ' + str(info['player']) + ' by ' + str(info['team_id'])
#print draft[2]['player_id']

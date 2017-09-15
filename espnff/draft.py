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
    

        

data = fetch_draft()
draft = {}
for row in data['items']:
    if 'pendingMoveItems' in row:
        if row['pendingMoveItems'][0]['moveTypeId'] == 5:
            print row['pendingMoveItems'][0]['playerId']
            print row['pendingMoveItems'][0]['toTeamId']
            print row['pendingMoveItems'][0]['draftOverallSelection']
            #draft.append(

def get_roster(self, week):
		params = {
            'leagueId': league_id,
            'seasonId': year,
            'teamIds': self.team_id
        }
        roster_slots = {0:'QB',2:'RB',4:'WR',6:'TE',23:'FLEX',16:'D/ST',17:'K',20:'Bench'}
        if week is not None:
            params['scoringPeriodId'] = week
        r = requests.get('%srosterInfo' % (self.ENDPOINT, ), params=params, cookies=cookies)
        self.status = r.status_code
        data = r.json()      
        if self.status == 401:
            raise PrivateLeagueException(data['error'][0]['message'])
        elif self.status == 404:
            raise InvalidLeagueException(data['error'][0]['message'])
        elif self.status != 200:
            raise UnknownLeagueException('Unknown %s Error' % self.status)
        
        players = data['leagueRosters']['teams'][0]['slots']
		
		roster = []
        for p in players:
            if 'player' in p:
			    player_name = ('%s %s' %(p['player']['firstName'],p['player']['lastName']))
			    position = roster_slots[p['slotCategoryId']]
			    player_id = p['player']['playerId']
			    roster.append({'name':player_name,'position':position,'player_id':player_id})
        return roster
'''
get weekly stats:http://games.espn.com/ffl/api/v2/playerInfo?leagueId=376&seasonId=2016&playerId=2330&scoringPeriodId=12&useCurrentPeriodRealStats=true
get weekly rosters:http://games.espn.com/ffl/api/v2/rosterInfo?leagueId=376&seasonId=2016&teamId=7&scoringPeriodId=5&teamIds=9
def _fetch_roster(self):
'''

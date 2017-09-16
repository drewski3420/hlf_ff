import requests
class Team(object):
    '''Teams are part of the league'''
    def __init__(self, data, league_id, year, cookies):
        self.team_id = data['teamId']
        self.team_abbrev = data['teamAbbrev']
        self.team_name = "%s %s" % (data['teamLocation'], data['teamNickname'])
        self.division_id = data['division']['divisionId']
        self.division_name = data['division']['divisionName']
        self.wins = data['record']['overallWins']
        self.losses = data['record']['overallLosses']
        self.points_for = data['record']['pointsFor']
        self.points_against = data['record']['pointsAgainst']
        self.owner = "%s %s" % (data['owners'][0]['firstName'],
                                data['owners'][0]['lastName'])
        self.schedule = []
        self.scores = []
        self.mov = []
        self.league_id = league_id
        self.cookies = cookies
        self.year = year
        self.ENDPOINT = "http://games.espn.com/ffl/api/v2/"
        self._fetch_schedule(data)

    def __repr__(self):
        return 'Team(%s)' % (self.team_name, )

    def _fetch_schedule(self, data):
        '''Fetch schedule and scores for team'''
        matchups = data['scheduleItems']

        for matchup in matchups:
            if not matchup['matchups'][0]['isBye']:
                if matchup['matchups'][0]['awayTeamId'] == self.team_id:
                    score = matchup['matchups'][0]['awayTeamScores'][0]
                    opponentId = matchup['matchups'][0]['homeTeamId']
                else:
                    score = matchup['matchups'][0]['homeTeamScores'][0]
                    opponentId = matchup['matchups'][0]['awayTeamId']
            else:
                score = matchup['matchups'][0]['homeTeamScores'][0]
                opponentId = matchup['matchups'][0]['homeTeamId']

            self.scores.append(score)
            self.schedule.append(opponentId)

    def get_roster(self,week=None):
        params = {
            'leagueId': self.league_id,
            'seasonId': self.year,
            'teamIds': self.team_id
        }
        roster_slots = {0:'QB',2:'RB',4:'WR',6:'TE',23:'FLEX',16:'D/ST',17:'K',20:'Bench'}
        if week is not None:
            params['scoringPeriodId'] = week
        r = requests.get('%srosterInfo' % (self.ENDPOINT, ), params=params, cookies=self.cookies)
        data = r.json()      
      
        players = data['leagueRosters']['teams'][0]['slots']
        roster = []
        for p in players:
            if 'player' in p:
                player_name = ('%s %s' %(p['player']['firstName'],p['player']['lastName']))
                position = roster_slots[p['slotCategoryId']]
                player_id = p['player']['playerId']
                params = {
                    'leagueId' : self.league_id,
                    'seasonId' : self.year,
                    'teamIds' : self.team_id,
                    'playerId' : player_id,
                    'useCurrentPeriodRealStats' : 'true',
                    'useCurrentPeriodProjectedStats' : 'true'
                }
                if week is not None:
                    params['scoringPeriodId'] = week
                r = requests.get('%splayerInfo' % (self.ENDPOINT, ), params=params, cookies=self.cookies)
                data = r.json()
                if 'appliedStatTotal' in data['playerInfo']['players'][0]['currentPeriodRealStats']:
                    player_score = data['playerInfo']['players'][0]['currentPeriodRealStats']['appliedStatTotal']
                else:
                    player_score = 0
                if 'appliedStatTotal' in data['playerInfo']['players'][0]['currentPeriodProjectedStats']:
                    projected_score = data['playerInfo']['players'][0]['currentPeriodProjectedStats']['appliedStatTotal']
                else:
                    projected_score = 0
                pro_team = data['playerInfo']['players'][0]['player']['proTeamId'] 
                health_status = data['playerInfo']['players'][0]['player']['healthStatus'] 
                roster.append({'name':player_name,'position':position,'player_id':player_id,'actual_score':player_score, 'projected_score':projected_score, 'pro_team_id':pro_team, 'health_status':health_status})
        return roster

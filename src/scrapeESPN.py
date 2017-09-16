import os
import sqlite3
from datetime import date

import espnff


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE teams(team_id integer
                    ,team_name TEXT
                    ,team_abbrev TEXT
                    ,team_owner TEXT)
    ''')
    cursor.execute('''create table rosters (team_id integer
                    ,team_name integer
                    ,week integer
                    ,player_id integer
                    ,player_name text
                    ,player_position text
                    ,player_pro_team integer
                    ,actual_score real
                    ,projected_score real
                    ,health_status integer)
    ''')
    cursor.execute('''create table matchups (week integer
                    ,winning_team_id integer
                    ,winning_team_name text
                    ,winning_score real
                    ,losing_team_id integer
                    ,losing_team_name text
                    ,losing_score real)
    ''')
    cursor.execute(
        '''create table awards (award text, winner text, datapoint text, week int, s integer, award_type text)''')
    cursor.execute('''Create table calendar (start_dt text, end_dt text, wk integer)''')
    cursor.execute('''with cte as (Select '2017-09-07' as start_dt, '2017-09-14' as end_dt, 1 as wk
                                    union all
                                    select date(start_dt,'+7 day') as start_dt, date(end_dt,'+7 day') as end_dt, wk + 1 as wk from cte where wk < 20)
                    insert into calendar (start_dt, end_dt, wk) select * from cte where wk < 20
    ''')
    cursor.execute('''create table byes (player_pro_team integer, bye_week integer)''')
    cursor.execute('''insert into byes (bye_week, player_pro_team) values ('5', '1'),
                    ('6', '2'),('9', '3'),('6', '4'),('9', '5'),('6', '6'),('5', '7'),('7', '8'),
                    ('8', '9'),('8', '10'),('11', '11'),('10', '12'),('10', '13'),('8', '14'),('1', '15'),
                    ('9', '16'),('9', '17'),('6', '18'),('8', '19'),('11', '20'),('10', '21'),('8', '22'),
                    ('9', '23'),('9', '24'),('11', '25'),('6', '26'),('1', '27'),('6', '28'),('11', '29'),
                    ('8', '30'),('10', '33'),('7', '34')''')
    conn.commit()
    return conn


def populate_tables(conn, league_id, year, espn_s2, swid):
    cursor = conn.cursor()
    league = espnff.League(league_id, year, espn_s2, swid)
    for team in league.teams:
        team_id = team.team_id
        name = team.team_name
        abbrev = team.team_abbrev
        owner = team.owner
        cursor.execute('insert into teams (team_id, team_name, team_abbrev, team_owner) values (?,?,?,?)',
                       (team.team_id, team.team_name, team.team_abbrev, team.owner))

    today = str(date.today())

    for row in cursor.execute('select wk from calendar where start_dt <= ? and ? < end_dt',
                              (today, today)):  # for each week
        i = row[0]
        scoreboard = league.scoreboard(week=i)
        for matchup in scoreboard:
            winning_team_id = matchup.home_team.team_id if matchup.home_score > matchup.away_score else matchup.away_team.team_id  # for each matchup
            winning_team_name = matchup.home_team.team_name if matchup.home_score > matchup.away_score else matchup.away_team.team_name
            winning_score = matchup.home_score if matchup.home_score > matchup.away_score else matchup.away_score
            losing_team_id = matchup.home_team.team_id if matchup.home_score < matchup.away_score else matchup.away_team.team_id  # for each matchup
            losing_team_name = matchup.home_team.team_name if matchup.home_score < matchup.away_score else matchup.away_team.team_name
            losing_score = matchup.home_score if matchup.home_score < matchup.away_score else matchup.away_score
            cursor.execute(
                'insert into matchups (week, winning_team_id, winning_team_name, winning_score, losing_team_id, losing_team_name, losing_score) values (?,?,?,?,?,?,?)',
                (i, winning_team_id, winning_team_name, winning_score, losing_team_id, losing_team_name, losing_score))

            for team in (matchup.home_team, matchup.away_team):  # for each team in matchup
                roster = team.get_roster(week=i)
                for player in roster:  # for each player on team
                    player_id = player['player_id']
                    name = player['name']
                    position = player['position']
                    actual_score = player['actual_score']
                    projected_score = player['projected_score']
                    player_pro_team = player['pro_team_id']
                    health_status = player['health_status']
                    week = i
                    cursor.execute(
                        'insert into rosters (team_id, team_name, week, player_id, player_name, player_position, player_pro_team, actual_score, projected_score, health_status) values (?,?,?,?,?,?,?,?,?,?)',
                        (team.team_id, team.team_name, week, player_id, name, position, player_pro_team, actual_score,
                         projected_score, health_status))
    conn.commit()
    return conn


def run_awards(conn):
    cursor = conn.cursor()

    # Eked it Out
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select 
                        winning_team_name as winner
                        ,round(winning_score - losing_score,2) || ' point margin (' || winning_score || '-' || losing_score || ')' as datapoint
                        ,'Eked it Out (Closest Win)' as award
                        ,null as week
                        ,1 as s
                        ,1 as award_type
                    from matchups
                    order by winning_score - losing_score
                    limit 1
                    ''')
    # Suicide Watch
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select 
                        losing_team_name as winner
                        ,round(winning_score - losing_score,2) || ' point margin (' || losing_score || '-' || winning_score || ')' as datapoint
                        ,'Suicide Watch (Closest Loss)' as award
                        ,null as week
                        ,1 as s
                        ,2 as award_type
                    from matchups
                    order by winning_score - losing_score
                    limit 1
                    ''')
    # Rack em up
    cursor.execute('''Insert into awards (winner, datapoint, award, week, s, award_type)
                    Select
                        t.team_name as winner
                        ,round(score,2) || ' Team Points' as datapoint
                        ,'Rack ''Em Up (Most League Points)' as award
                        ,null as week
                        ,3 as s
                        ,1 as award_type
                    from (  Select winning_score as score, winning_team_id as team_id, week from matchups
                    ) yyz
                        join teams t on t.team_id = yyz.team_id
                    order by score desc
                    limit 1
                    ''')

    # Pine Riding Cowboy
    cursor.execute('''Insert into awards (winner, datapoint, award, week, s, award_type)
                    Select  
                        t.team_name as winner
                        ,round(bench_points,2) || ' Bench Points' as datapoint
                        ,'Pine Ridin'' Cowboy (Most Bench Points in a Loss)' as award
                        ,null as week
                        ,4 as s
                        ,2 as award_type
                    from (
                        Select 
                            sum(actual_score) as bench_points
                            ,team_id
                        from rosters r
                        where r.player_position = 'Bench'
                        group by team_id
                    ) b
                        join (Select losing_team_id as loser from matchups) l on b.team_id = l.loser
                        join teams t on t.team_id = b.team_id
                    order by bench_points desc
                    limit 1
                    ''')
    # mercy rule
    cursor.execute('''Insert into awards (winner, datapoint, award, week, s, award_type)
                    select
                        t.team_name as winner
                        ,round(margin,2) || ' Point Margin' as datapoint
                        ,'Mercy Rule (Biggest Loss)' as award
                        ,null as week
                        ,5 as s
                        ,2 as award_type
                    from (
                        select
                            winning_score - losing_score as margin
                            ,losing_team_id as loser
                        from matchups
                        order by margin desc
                        limit 1
                    ) yyz
                        join teams t on t.team_id = yyz.loser
                    ''')
    # it's better to be lucky than good
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select 
                        t.team_name as winner
                        ,round(winning_score,2) || ' Total Points (Would have lost to ' || Count(*) || ' other teams)' as datapoint
                        ,'It''s Better to Be Lucky than Good (Lowest Winning Point Total)' as award
                        ,null as week
                        ,7 as s
                        ,1 as award_type
                    from (                          
                        Select 
                            winning_score
                            ,winning_team_id
                        from matchups m
                        order by winning_score asc
                        limit 1
                    ) yyz
                        join (Select winning_team_id team_id, winning_score score from matchups
                            union select losing_team_id team_id, losing_score score from matchups) a
                        join teams t on t.team_id = yyz.winning_team_id
                    where a.score > yyz.winning_score
                    ''')
    # life's not fair
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select 
                        t.team_name as winner
                        ,round(losing_score,2) || ' Total Points (Would have beaten ' || Count(*) || ' other teams)' as datapoint
                        ,'Life''s Not Fair, I''ll Never Be King! (Highest Losing Point Total)' as award
                        ,null as week
                        ,7 as s
                        ,2 as award_type
                    from (                          
                        Select 
                            losing_score
                            ,losing_team_id
                        from matchups m
                        order by losing_score desc
                        limit 1
                    ) yyz
                        join (Select winning_team_id team_id, winning_score score from matchups
                            union select losing_team_id team_id, losing_score score from matchups) a
                        join teams t on t.team_id = yyz.losing_team_id
                    where a.score < yyz.losing_score
                    ''')
    # dud of the week
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select
                        t.team_name as winner
                        ,player_name || ': Projected: ' || round(projected_score,2) || ', Actual: ' || round(actual_score,2) as datapoint
                        ,'Dud of the Week (Largest Negative Difference Between Projected and Actual Score)' as award
                        ,null as week
                        ,8 as s
                        ,2 as award_type
                    from (
                        Select
                            projected_score - actual_score as diff
                            ,projected_score
                            ,actual_score
                            ,player_name
                            ,team_id
                        from rosters
                        where actual_score < projected_score
                        order by (projected_score - actual_score) desc
                        limit 1
                    ) yyz
                        join teams t on t.team_id = yyz.team_id
                     ''')
    # stud of the week
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select
                        t.team_name as winner
                        ,player_name || ': Projected: ' || round(projected_score,2) || ', Actual: ' || round(actual_score,2) as datapoint
                        ,'Stud of the Week (Largest Positive Difference Between Projected and Actual Score)' as award
                        ,null as week
                        ,9 as s
                        ,1 as award_type
                    from (
                        Select
                            actual_score - projected_score as diff
                            ,projected_score
                            ,actual_score
                            ,player_name
                            ,team_id
                        from rosters
                        where actual_score > projected_score
                        order by (actual_score - projected_score) Desc
                        limit 1
                    ) yyz
                        join teams t on t.team_id = yyz.team_id
                    ''')
    # flex appeal
    cursor.execute('''insert into awards(winner,datapoint, award, week, s, award_type)
                    Select
                        t.team_name as winner
                        ,player_name || ': ' || round(actual_score,2) || ' Points' as datapoint
                        ,'FLEX Appeal (Highest FLEX Point Total)' as award
                        ,null as week
                        ,10 as s
                        ,1 as award_type
                    from (
                    Select
                        team_id
                        ,player_name
                        ,actual_score
                    from rosters
                    where player_position = 'FLEX'
                    order by actual_score desc
                    limit 1
                    ) yyz 
                        join teams t on t.team_id = yyz.team_id
                    ''')
    # the little engine that literally can't even
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select
                        t.team_name as winner
                        ,'Only Scored ' || round(losing_score,2) || ' Points' as datapoint
                        ,'The Little Engine That Literally Can''t Even (Lowest Point Total)' as award
                        ,null as week
                        ,11 as s
                        ,2 as award_type
                    from (
                    select
                        losing_team_id
                        ,losing_score
                        ,winning_score
                    from matchups
                    order by losing_score asc
                    limit 1
                    ) yyz 
                        join teams t on t.team_id = yyz.losing_team_id
                ''')
    # Fab Five
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select
                        t.team_name as winner
                        ,'5 Players - Look it up yourself' as datapoint
                        ,'Fab Five (20+ points from QB, RBs and WRs)' as award
                        ,null as week
                        ,12 as s
                        ,1 as award_type
                    from (
                            select
                                count(*)
                                ,team_id
                            from rosters
                            where actual_score > 20
                            and player_position in ('QB','RB','WR')
                            group by team_id
                            having count(*) = 5
                        ) cts
                        join teams t on t.team_id = cts.team_id
                    ''')
    # Goose Egg
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select
                        t.team_name
                        ,player_name as datapoint
                        ,'Goose Egg (Zero Points from a Starter)' as award
                        ,null as week
                        ,13 as s
                        ,2 as award_type
                    from (
                            select
                                player_name
                                ,team_id
                            from rosters
                            where actual_score = 0
                            and player_position <> 'Bench'
                        ) cts
                        join teams t on t.team_id = cts.team_id
                     ''')
    # maybe no one
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    Select
                        t.team_name
                        ,'Empty ' || z.player_position || ' instead of ' || z.player_name || ' would have won the matchup.' as datapoint
                        ,'Maybe Just Don''t Start Anybody? (Negative Player Points Led to Loss)' as award
                        ,null as week
                        ,14 as s
                        ,2 as award_type
                    from (Select losing_team_name, losing_team_id, winning_score - losing_score as margin from matchups) m
                        join (Select player_position, team_id, player_name, actual_score from rosters where actual_score < 0) z on z.team_id = m.losing_team_id
                        join teams t on t.team_id = m.losing_team_id 
                    where abs(z.actual_score) > m.margin
                    ''')
    # roster fail
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    select
                        t.team_name as winner
                        ,player_name || ': ' || round(actual_score,2) || ' Points' as datapoint
                        ,'Roster Fail (Highest Scoring Bench Player)' as award
                        ,null as week
                        ,15 as s
                        ,2 as award_type
                    from (
                        Select
                            *
                        from rosters
                        where player_position = 'Bench'
                        order by actual_score desc
                        limit 1
                    ) yyz
                        join teams t on t.team_id = yyz.team_id
                    ''')
    # never tell me the odds
    cursor.execute('''insert into awards (winner, datapoint, award, week, s, award_type)
                    select 
                        tw.team_name as winner
                        ,'Projected Spread: ' || round(w.projected_score - l.projected_score,2) as datapoint
                        ,'Never Tell Me The Odds (Biggest Underdog Win)' as award
                        ,null as week
                        ,16 as s
                        ,1 as award_type
                    from matchups m
                        left join (Select team_id,sum(actual_score) actual_score,sum(projected_score) projected_score from rosters where player_position <> 'Bench' group by team_id) w on w.team_id = m.winning_Team_id
                        left join teams tw on tw.team_id = w.team_id
                        left join (Select team_id,sum(actual_score) actual_score,sum(projected_score) projected_score from rosters where player_position <> 'Bench' group by team_id) l on l.team_id = m.losing_team_id
                        left join teams tl on tl.team_id = l.team_id
                    where w.projected_score < l.projected_score
                    order by w.projected_score - l.projected_score
                    limit 1
                    ''')
    conn.commit()
    return conn


def view_awards(conn):
    cursor = conn.cursor()
    cursor.execute(
        '''Select award, winner, datapoint, week, award_type from awards order by award_type, s, award, winner''')
    r = ''
    lastaward = ''
    thisaward = ''
    for row in cursor:
        thisaward = str(row[0])
        if thisaward != lastaward:
            r = r + '\n'
            r = r + str(row[0]) + '\n'
        r = r + str(row[1]) + ': ' + str(row[2]) + '\n'
        lastaward = thisaward
    return r


def drop_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''drop table if exists awards''')
    cursor.execute('''drop table if exists rosters''')
    cursor.execute('''drop table if exists teams''')
    cursor.execute('''drop table if exists matchups''')
    cursor.execute('''drop table if exists calendar''')
    cursor.execute('''drop table if exists byes''')
    conn.commit()
    return conn


def get_data(league_id, year, swid, espn_s2):
    conn_file = 'data.db'
    try:
        os.remove(conn_file)
    except OSError:
        pass
    conn = sqlite3.connect(conn_file)
    conn = drop_tables(conn)
    conn = create_tables(conn)
    conn = populate_tables(conn, league_id, year, espn_s2, swid)
    conn = run_awards(conn)
    r = view_awards(conn)
    conn.commit()
    conn.close()
    return r

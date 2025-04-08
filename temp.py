'''
SELECT * FROM games
WHERE
    status=status
    AND 
        (away_team_rowid=team_rowid OR home_team_rowid=team_rowid)
'''

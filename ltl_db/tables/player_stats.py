import sqlite3
from classes.classes import SQLiteTable
from classes.dataclasses import PlayerStat


###############################################################################


class PlayerStatsTable(SQLiteTable):
    def __init__(self, testing=False):
        if not testing: 
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'test.db'))
        
        self.dataclass = PlayerStat
        self._table_name = 'player_stats'

        self._list_keys = { 
            'game_rowid': self.read_by_game_rowid,
            'player_nhlid': self.read_by_player_nhlid,
            'player_team_rowid': self.read_by_player_team_rowid,
            'opp_team_rowid': self.read_by_opp_team_rowid,
        }
        self._single_keys = {
            'rowid': self.read_by_rowid,
        }
        self._other_keys = [ 
            'goals',
            'assists',
            'shots_on_goal',
            'blocked_shots',
            'hits',
        ]
        self._group_keys = {
            'all': self.read_all,
            'team_rowid': self.read_by_team_rowid,
        }
        self._filters = { 
            'game_and_player': self.read_by_game_and_player,
            'team_and_player': self.read_by_team_and_player,
            'opp_and_player': self.read_by_opp_and_player,
        }


    #------------------------------------------------------# 


    def init_db(self):
            with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                CREATE TABLE player_stats(
                    game_rowid INTEGER NOT NULL,
                    player_nhlid INTEGER NOT NULL,
                    player_team_rowid INTEGER NOT NULL,
                    opp_team_rowid INTEGER NOT NULL,
                    goals INTEGER NOT NULL,
                    assists INTEGER NOT NULL,
                    shots_on_goal INTEGER NOT NULL,
                    blocked_shots INTEGER NOT NULL,
                    hits INTEGER NOT NULL,
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    FOREIGN KEY(player_team_rowid)
                        REFERENCES teams(nhlid)
                    FOREIGN KEY(opp_team_rowid)
                        REFERENCES teams(nhlid)
                )
            '''
            cur.execute(sql)


    #------------------------------------------------------# 


    def add(self, playerstat: dict) -> int:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            INSERT INTO player_stats(
                game_rowid,
                player_nhlid,
                player_team_rowid,
                opp_team_rowid,
                goals,
                assists,
                shots_on_goal,
                blocked_shots,
                hits
            )
            VALUES (
                :game_rowid,
                :player_nhlid,
                :player_team_rowid,
                :opp_team_rowid,
                :goals,
                :assists,
                :shots_on_goal,
                :blocked_shots,
                :hits
            )
        '''
        cur.execute(sql, playerstat)
        return cur.lastrowid


    #------------------------------------------------------# 

    
    def read_all(self) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats'
            cur.execute(sql)
            return cur.fetchall()


    def read_by_rowid(self, rowid: int) -> PlayerStat:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_game_rowid(self, game_rowid: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE game_rowid=?'
            cur.execute(sql, (game_rowid,))
            return cur.fetchall()


    def read_by_player_nhlid(self, player_nhlid: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE player_nhlid=?'
            cur.execute(sql, (player_nhlid,))
            return cur.fetchall()


    def read_by_player_team_rowid(self, player_team_rowid: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE player_team_rowid=?'
            cur.execute(sql, (player_team_rowid,))
            return cur.fetchall()


    def read_by_opp_team_rowid(self, opp_team_rowid: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE opp_team_rowid=?'
            cur.execute(sql, (opp_team_rowid,))
            return cur.fetchall()


    def read_by_team_rowid(self, team_rowid: ) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = '''
                SELECT * FROM player_stats
                WHERE player_team_rowid=?
                OR opp_team_rowid=?
            '''
            cur.execute(sql, (team_rowid, team_rowid))
            return cur.fetchall()


    def read_by_game_and_player(self, game_rowid: int, player_nhlid: int) -> list[PlayerStat] | PlayerStat:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = '''
                SELECT * FROM player_stats
                WHERE game_rowid=?
                AND player_nhlid=?
            '''
            cur.execute(sql, (game_rowid, player_nhlid))
            response = cur.fetchall()
            
            if not response:
                return response
            if len(response) == 1:
                return response[0]
            return response


    def read_by_team_and_player(self, player_nhlid: int, player_team_rowid: int) -> list[PlayerStat] | PlayerStat:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = '''
                SELECT * FROM player_stats
                WHERE player_nhlid=?
                AND player_team_rowid=?
            '''
            cur.execute(sql, (player_nhlid, player_team_rowid))
            response = cur.fetchall()
            
            if not response:
                return response
            if len(response) == 1:
                return response[0]
            return response


    def read_by_opp_and_player(self, player_nhlid: int, opp_team_rowid: int) -> list[PlayerStat] | PlayerStat:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = '''
                SELECT * FROM player_stats
                WHERE player_nhlid=?
                AND opp_team_rowid=?
            '''
            cur.execute(sql, (player_nhlid, opp_team_rowid))
            response = cur.fetchall()
            
            if not response:
                return response
            if len(response) == 1:
                return response[0]
            return response


    #------------------------------------------------------# 


    def update(self, playerstat: PlayerStat) -> None:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            UPDATE player_stats
            SET
                game_rowid=:game_rowid,
                player_nhlid=:player_nhlid,
                player_team_rowid=:player_team_rowid,
                opp_team_rowid=:opp_team_rowid,
                goals=:goals,
                assists=:assists,
                shots_on_goal=:shots_on_goal,
                blocked_shots=:blocked_shots,
                hits=:hits
            WHERE rowid=:rowid
        '''
        cur.execute(sql, obj.as_dict)
        con.commit()


###############################################################################
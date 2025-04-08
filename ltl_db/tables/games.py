import sqlite3
from classes.classes import SQLiteTable
from classes.dataclasses import Game


###############################################################################


class GamesTable(SQLiteTable):
    def __init__(self, testing=False):
        if not testing: 
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'test.db'))
        
        self.dataclass = Game
        self._table_name = 'games'

        self._list_keys = { 
            'start_time': self.read_by_start_time,
            'status': self.read_by_status,
        }
        self._single_keys = {
            'rowid': self.read_by_rowid,
            'nhlid': self.read_by_nhlid,
        }
        self._other_keys = [ 
            'away_team_points',
            'home_team_points',
        ]
        self._group_keys = {
            'all': self.read_all,
            'team_rowid': self.read_by_team_rowid,
        }
        self._filters = { 
            'status_and_team': self.read_by_status_and_team,
        }


    #------------------------------------------------------# 


    def init_db(self):
            with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                CREATE TABLE games(
                    nhlid INTEGER NOT NULL,
                    start_time INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    away_team_rowid INTEGER NOT NULL,
                    away_team_points INTEGER NOT NULL,
                    home_team_rowid INTEGER NOT NULL,
                    home_team_points INTEGER NOT NULL,
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    FOREIGN KEY(away_team_rowid)
                        REFERENCES teams(rowid)
                    FOREIGN KEY(home_team_rowid)
                        REFERENCES teams(rowid)
                )
            '''
            cur.execute(sql)


    #------------------------------------------------------# 


    def add(self, game: dict) -> int:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            INSERT INTO games(
                nhlid,
                start_time,
                status,
                away_team_rowid,
                away_team_points,
                home_team_rowid,
                home_team_points
            )
            VALUES (
                :nhlid,
                :start_time,
                :status,
                :away_team_rowid,
                :away_team_points,
                :home_team_rowid,
                :home_team_points
            )
        '''
        cur.execute(sql, game)
        return cur.lastrowid


    #------------------------------------------------------# 

    
    def read_all(self) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games'
            cur.execute(sql)
            return cur.fetchall()


    def read_by_rowid(self, rowid: int) -> Game:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_start_time(self, start_time: int) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games WHERE start_time=?'
            cur.execute(sql, (start_time,))
            return cur.fetchall()


    def read_by_status(self, status: str) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games WHERE status=?'
            cur.execute(sql, (status,))
            return cur.fetchall()


    def read_by_nhlid(self, nhlid: int) -> Game:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games WHERE nhlid=?'
            cur.execute(sql, (nhlid,))
            return cur.fetchone()


    def read_by_team_rowid(self, team_rowid: int) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = '''
                SELECT * FROM games
                WHERE away_team_rowid=?
                OR home_team_rowid=?
            '''
            cur.execute(sql, (team_rowid, team_rowid))
            return cur.fetchall()


    def read_by_status_and_team(self, start_time: int, status: str, team_rowid: int) -> list[Game] | Game:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = '''
                SELECT * FROM games
                WHERE
                    start_time=?
                    AND
                        status=?
                    AND
                        (away_team_rowid=? OR home_team_rowid=?)
            '''
            cur.execute(sql, (start_time, status, team_rowid, team_rowid))
            response = cur.fetchall()
            
            if not response:
                return response
            if len(response) == 1:
                return response[0]
            return response


    #------------------------------------------------------# 


    def update(self, game: Game) -> None:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            UPDATE games
            SET
                nhlid=:nhlid,
                start_time=:start_time,
                status=:status,
                away_team_rowid=:away_team_rowid,
                away_team_points=:away_team_points,
                home_team_rowid=:home_team_rowid,
                home_team_points=:home_team_points
            WHERE rowid=:rowid
        '''
        cur.execute(sql, obj.as_dict)
        con.commit()


###############################################################################
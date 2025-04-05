import sqlite3
from classes.classes import SQLiteTable
from classes.dataclasses import Player


###############################################################################


class PlayersTable(SQLiteTable):
    def __init__(self, testing=False):
        if not testing: 
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'test.db'))
        
        self.dataclass = Player
        self._table_name = 'players'

        self._list_keys = { 
            'position': self.read_by_position,
            'name': self.read_by_name,
        }
        self._single_keys = {
            'rowid': self.read_by_rowid,
            'nhlid': self.read_by_nhlid,
            'team_rowid': self.read_by_team_rowid,
        }
        self._other_keys = [ 
        ]
        self._group_keys = {
            'all': self.read_all,
        }
        self._filters = { 
            'team_and_position': self.read_by_team_and_position,
        }


    #------------------------------------------------------# 


    def init_db(self):
            with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                CREATE TABLE players(
                    nhlid INTEGER NOT NULL,
                    team_rowid INTEGER NOT NULL,
                    position TEXT NOT NULL,
                    name TEXT NOT NULL,
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                    
                    FOREIGN KEY(team_rowid)
                        REFERENCES teams(rowid)
                )
            '''
            cur.execute(sql)


    #------------------------------------------------------# 


    def add(self, player: dict) -> int:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            INSERT INTO players(
                nhlid,
                team_rowid,
                position,
                name
            )
            VALUES (
                :nhlid,
                :team_rowid,
                :position,
                :name
            )
        '''
        cur.execute(sql, player)
        return cur.lastrowid


    #------------------------------------------------------# 

    
    def read_all(self) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players'
            cur.execute(sql)
            return cur.fetchall()


    def read_by_rowid(self, rowid: int) -> Player:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_position(self, position: str) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE position=?'
            cur.execute(sql, (position,))
            return cur.fetchall()


    def read_by_name(self, name: str) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE name=?'
            cur.execute(sql, (name,))
            return cur.fetchall()


    def read_by_nhlid(self, nhlid: int) -> Player:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE nhlid=?'
            cur.execute(sql, (nhlid,))
            return cur.fetchone()


    def read_by_team_rowid(self, team_rowid: int) -> Player:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE team_rowid=?'
            cur.execute(sql, (team_rowid,))
            return cur.fetchone()


    def read_by_team_and_position(self, team_rowid: int, position: str) -> list[Player] | Player:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = '''
                SELECT * FROM players
                WHERE team_rowid=?
                AND position=?
            '''
            cur.execute(sql, (team_rowid, position))
            response = cur.fetchall()
            
            if not response:
                return response
            if len(response) == 1:
                return response[0]
            return response


    #------------------------------------------------------# 


    def update(self, player: Player) -> None:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            UPDATE players
            SET
                nhlid=:nhlid,
                team_rowid=:team_rowid,
                position=:position,
                name=:name
            WHERE rowid=:rowid
        '''
        cur.execute(sql, obj.as_dict)
        con.commit()


###############################################################################
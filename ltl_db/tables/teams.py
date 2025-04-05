import sqlite3
from classes.classes import SQLiteTable
from classes.dataclasses import Team


###############################################################################


class TeamsTable(SQLiteTable):
    def __init__(self, testing=False):
        if not testing: 
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'test.db'))
        
        self.dataclass = Team
        self._table_name = 'teams'

        self._list_keys = { 
            'conference': self.read_by_conference,
            'division': self.read_by_division,
        }
        self._single_keys = {
            'rowid': self.read_by_rowid,
            'code': self.read_by_code,
            'nhlid': self.read_by_nhlid,
            'name': self.read_by_name,
        }
        self._other_keys = [ 
        ]
        self._group_keys = {
            'all': self.read_all,
        }
        self._filters = { 
        }


    #------------------------------------------------------# 


    def init_db(self):
            with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                CREATE TABLE teams(
                    conference TEXT NOT NULL,
                    division TEXT NOT NULL,
                    code TEXT NOT NULL,
                    nhlid INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT
                )
            '''
            cur.execute(sql)


    #------------------------------------------------------# 


    def add(self, team: dict) -> int:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            INSERT INTO teams(
                conference,
                division,
                code,
                nhlid,
                name
            )
            VALUES (
                :conference,
                :division,
                :code,
                :nhlid,
                :name
            )
        '''
        cur.execute(sql, team)
        return cur.lastrowid


    #------------------------------------------------------# 

    
    def read_all(self) -> list[Team]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams'
            cur.execute(sql)
            return cur.fetchall()


    def read_by_rowid(self, rowid: int) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_conference(self, conference: str) -> list[Team]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE conference=?'
            cur.execute(sql, (conference,))
            return cur.fetchall()


    def read_by_division(self, division: str) -> list[Team]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE division=?'
            cur.execute(sql, (division,))
            return cur.fetchall()


    def read_by_code(self, code: str) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE code=?'
            cur.execute(sql, (code,))
            return cur.fetchone()


    def read_by_nhlid(self, nhlid: int) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE nhlid=?'
            cur.execute(sql, (nhlid,))
            return cur.fetchone()


    def read_by_name(self, name: str) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE name=?'
            cur.execute(sql, (name,))
            return cur.fetchone()


    #------------------------------------------------------# 


    def update(self, team: Team) -> None:
        with sqlite3.connect(self.db_dir) as con:
        cur = con.cursor()
        sql = '''
            UPDATE teams
            SET
                conference=:conference,
                division=:division,
                code=:code,
                nhlid=:nhlid,
                name=:name
            WHERE rowid=:rowid
        '''
        cur.execute(sql, obj.as_dict)
        con.commit()


###############################################################################
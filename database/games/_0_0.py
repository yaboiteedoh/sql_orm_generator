
import sqlite3
from pathlib import Path
from io import StringIO

from database.classes import SQLiteTable
from database.dataclasses import Game


###############################################################################


class GamesTable(SQLiteTable):
	def __init__(self, testing=False):
		if not testing:
			self.db_dir = str(Path('database', 'data.db'))
		else:
			self.db_dir = str(Path('database', 'test.db'))
		self.dataclass = Game

		self._table_name = 'games'
		self._group_keys = {
			'status': self.read_by_status
		}
		self._object_keys = {
			'nhlid': self.read_by_nhlid
		}
		self._test_data = test_data


	#------------------------------------------------------#


	def init_db(self):
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			sql = '''
				CREATE TABLE games(
					status TEXT NOT NULL,
					nhlid INTEGER NOT NULL,
					timestamp TEXT NOT NULL,
					start_time TEXT NOT NULL,
					home_team_rowid INTEGER NOT NULL,
					home_team_points INTEGER NOT NULL,
					away_team_rowid INTEGER NOT NULL,
					away_team_points INTEGER NOT NULL,
					clock TEXT NOT NULL,
					rowid INTEGER PRIMARY KEY AUTOINCREMENT,
					FOREIGN KEY(home_team_rowid)
						REFERENCES teams(rowid)
					FOREIGN KEY(away_team_rowid)
						REFERENCES teams(rowid)
				)
			'''
			cur.execute(sql)

			
	#------------------------------------------------------# 


	def add(self, game: Game) -> int:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			sql = '''
				INSERT INTO games(
					status,
					nhlid,
					timestamp,
					start_time,
					home_team_rowid,
					home_team_points,
					away_team_rowid,
					away_team_points,
					clock
				)
				VALUES (
					:status,
					:nhlid,
					:timestamp,
					:start_time,
					:home_team_rowid,
					:home_team_points,
					:away_team_rowid,
					:away_team_points,
					:clock
				)
			'''
			cur.execute(sql, game.as_dict)
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


def games_table(testing=False):
	return GamesTable(testing)


###############################################################################


test_data = [{'status': 'TEST 1', 'nhlid': 0, 'timestamp': 'TEST 0', 'start_time': 'TEST 0', 'home_team_rowid': 0, 'home_team_points': 0, 'away_team_rowid': 0, 'away_team_points': 0, 'clock': 'TEST 0'}, {'status': 'TEST 1', 'nhlid': 1, 'timestamp': 'TEST 1', 'start_time': 'TEST 1', 'home_team_rowid': 1, 'home_team_points': 1, 'away_team_rowid': 1, 'away_team_points': 1, 'clock': 'TEST 1'}, {'status': 'TEST 2', 'nhlid': 2, 'timestamp': 'TEST 2', 'start_time': 'TEST 2', 'home_team_rowid': 2, 'home_team_points': 2, 'away_team_rowid': 2, 'away_team_points': 2, 'clock': 'TEST 2'}, {'status': 'TEST 3', 'nhlid': 3, 'timestamp': 'TEST 3', 'start_time': 'TEST 3', 'home_team_rowid': 3, 'home_team_points': 3, 'away_team_rowid': 3, 'away_team_points': 3, 'clock': 'TEST 3'}]


###############################################################################

import sqlite3
from pathlib import Path
from io import StringIO

from database_1.classes import SQLiteTable
from database_1.dataclasses import PStat


###############################################################################


class PstatsTable(SQLiteTable):
	def __init__(self, testing=False):
		if not testing:
			self.db_dir = str(Path('database_1', 'data.db'))
		else:
			self.db_dir = str(Path('database_1', 'test.db'))
		self.dataclass = PStat

		self._table_name = 'pstats'
		self._group_keys = {
			'game_rowid': self.read_by_game_rowid,
			'player_rowid': self.read_by_player_rowid,
			'shots_on_goal': self.read_by_shots_on_goal,
			'goals': self.read_by_goals,
			'assists': self.read_by_assists
		}
		self._object_keys = {
		}
		self._test_data = test_data


	#------------------------------------------------------#


	def init_db(self):
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			sql = '''
				CREATE TABLE pstats(
					game_rowid INTEGER NOT NULL,
					player_rowid INTEGER NOT NULL,
					shots_on_goal INTEGER NOT NULL,
					goals INTEGER NOT NULL,
					assists INTEGER NOT NULL,
					rowid INTEGER PRIMARY KEY AUTOINCREMENT,
					FOREIGN KEY(game_rowid)
						REFERENCES games(rowid)
					FOREIGN KEY(player_rowid)
						REFERENCES players(rowid)
				)
			'''
			cur.execute(sql)

			
	#------------------------------------------------------# 


	def add(self, pstat: PStat) -> int:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			sql = '''
				INSERT INTO pstats(
					game_rowid,
					player_rowid,
					shots_on_goal,
					goals,
					assists
				)
				VALUES (
					:game_rowid,
					:player_rowid,
					:shots_on_goal,
					:goals,
					:assists
				)
			'''
			cur.execute(sql, pstat.as_dict)
			return cur.lastrowid

			
	#------------------------------------------------------# 


	def read_all(self) -> list[PStat]:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM pstats'
			cur.execute(sql)
			return cur.fetchall()


	def read_by_rowid(self, rowid: int) -> PStat:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM pstats WHERE rowid=?'
			cur.execute(sql, (rowid,))
			return cur.fetchone()


	def read_by_game_rowid(self, game_rowid: int) -> list[PStat]:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM pstats WHERE game_rowid=?'
			cur.execute(sql, (game_rowid,))
			return cur.fetchall()


	def read_by_player_rowid(self, player_rowid: int) -> list[PStat]:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM pstats WHERE player_rowid=?'
			cur.execute(sql, (player_rowid,))
			return cur.fetchall()


	def read_by_shots_on_goal(self, shots_on_goal: int) -> list[PStat]:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM pstats WHERE shots_on_goal=?'
			cur.execute(sql, (shots_on_goal,))
			return cur.fetchall()


	def read_by_goals(self, goals: int) -> list[PStat]:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM pstats WHERE goals=?'
			cur.execute(sql, (goals,))
			return cur.fetchall()


	def read_by_assists(self, assists: int) -> list[PStat]:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM pstats WHERE assists=?'
			cur.execute(sql, (assists,))
			return cur.fetchall()


def pstats_table(testing=False):
	return PstatsTable(testing)


###############################################################################


test_data = [{'game_rowid': 1, 'player_rowid': 1, 'shots_on_goal': 1, 'goals': 1, 'assists': 1}, {'game_rowid': 1, 'player_rowid': 1, 'shots_on_goal': 1, 'goals': 1, 'assists': 1}, {'game_rowid': 2, 'player_rowid': 2, 'shots_on_goal': 2, 'goals': 2, 'assists': 2}, {'game_rowid': 3, 'player_rowid': 3, 'shots_on_goal': 3, 'goals': 3, 'assists': 3}]


###############################################################################
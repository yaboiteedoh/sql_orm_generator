
import sqlite3
from pathlib import Path
from io import StringIO

from database_1.classes import SQLiteTable
from database_1.dataclasses import Player


###############################################################################


class PlayersTable(SQLiteTable):
	def __init__(self, testing=False):
		if not testing:
			self.db_dir = str(Path('database_1', 'data.db'))
		else:
			self.db_dir = str(Path('database_1', 'test.db'))
		self.dataclass = Player

		self._table_name = 'players'
		self._group_keys = {
			'status': self.read_by_status,
			'name': self.read_by_name,
			'position': self.read_by_position
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
				CREATE TABLE players(
					status TEXT NOT NULL,
					name TEXT NOT NULL,
					position TEXT NOT NULL,
					nhlid TEXT NOT NULL,
					rowid INTEGER PRIMARY KEY AUTOINCREMENT
				)
			'''
			cur.execute(sql)

			
	#------------------------------------------------------# 


	def add(self, player: Player) -> int:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			sql = '''
				INSERT INTO players(
					status,
					name,
					position,
					nhlid
				)
				VALUES (
					:status,
					:name,
					:position,
					:nhlid
				)
			'''
			cur.execute(sql, player.as_dict)
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


	def read_by_status(self, status: str) -> list[Player]:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM players WHERE status=?'
			cur.execute(sql, (status,))
			return cur.fetchall()


	def read_by_name(self, name: str) -> list[Player]:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM players WHERE name=?'
			cur.execute(sql, (name,))
			return cur.fetchall()


	def read_by_position(self, position: str) -> list[Player]:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM players WHERE position=?'
			cur.execute(sql, (position,))
			return cur.fetchall()


	def read_by_nhlid(self, nhlid: str) -> Player:
		with sqlite3.connect(self.db_dir) as con:
			cur = con.cursor()
			cur.row_factory = self._dataclass_row_factory
			sql = 'SELECT * FROM players WHERE nhlid=?'
			cur.execute(sql, (nhlid,))
			return cur.fetchone()


def players_table(testing=False):
	return PlayersTable(testing)


###############################################################################


test_data = [{'status': 'TEST 1', 'name': 'TEST 1', 'position': 'TEST 1', 'nhlid': 'TEST 0'}, {'status': 'TEST 1', 'name': 'TEST 1', 'position': 'TEST 1', 'nhlid': 'TEST 1'}, {'status': 'TEST 2', 'name': 'TEST 2', 'position': 'TEST 2', 'nhlid': 'TEST 2'}, {'status': 'TEST 3', 'name': 'TEST 3', 'position': 'TEST 3', 'nhlid': 'TEST 3'}]


###############################################################################
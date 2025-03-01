
import sqlite3
from pathlib import Path
from io import StringIO

from database.classes import SQLiteTable
from database.dataclasses import Team


###############################################################################


class TeamsTable(SQLiteTable):
	def __init__(self, testing=False):
		if not testing:
			self.db_dir = str(Path('database', 'data.db'))
		else:
			self.db_dir = str(Path('database', 'test.db'))
		self.dataclass = Team

		self._table_name = 'teams'
		self._group_keys = {
			'conference': self.read_by_conference,
			'division': self.read_by_division
		}
		self._object_keys = {
			'code': self.read_by_code,
			'nhlid': self.read_by_nhlid,
			'name': self.read_by_name
		}
		self._test_data = test_data


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


	def add(self, team: Team) -> int:
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
			cur.execute(sql, team.as_dict)
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


def teams_table(testing=False):
	return TeamsTable(testing)


###############################################################################


test_data = [{'conference': 'TEST 1', 'division': 'TEST 1', 'code': 'TEST 0', 'nhlid': 0, 'name': 'TEST 0'}, {'conference': 'TEST 1', 'division': 'TEST 1', 'code': 'TEST 1', 'nhlid': 1, 'name': 'TEST 1'}, {'conference': 'TEST 2', 'division': 'TEST 2', 'code': 'TEST 2', 'nhlid': 2, 'name': 'TEST 2'}, {'conference': 'TEST 3', 'division': 'TEST 3', 'code': 'TEST 3', 'nhlid': 3, 'name': 'TEST 3'}]


###############################################################################
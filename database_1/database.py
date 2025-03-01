
import sqlite3
from io import StringIO

from .teams import teams_table
from .players import players_table
from .games import games_table
from .pstats import pstats_table

	
###############################################################################


class Database:
	def __init__(self, testing=False):
		results = StringIO() if testing else None
	
		self.teams = teams_table(testing)
		self.players = players_table(testing)
		self.games = games_table(testing)
		self.pstats = pstats_table(testing)

		self.build_sequence = [
				self.teams,
				self.players,
				self.games,

			self.pstats
		]

		if testing:
			try:
				self._test(results)
			except BaseException as e:
				print(results.getvalue())
				raise e


	#------------------------------------------------------# 


	def init_dbs(self, testing=False, results=None):
		for table in self.build_sequence:
			table.init_db()
			if testing:
				results.write(f'\n\ninitializing {table._table_name} table')
				table._test(results)


	#::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


	def _test(self, results):
		results.write(f'\n\n\tSTARTING DATABASE INTEGRATION TEST\n\n')
		teardown_sequence = self.build_sequence[::1]
		for table in teardown_sequence:
			with sqlite3.connect(table.db_dir) as con:
				cur = con.cursor()
				sql = f'DROP TABLE {table._table_name}'
				try:
					cur.execute(sql)
				except sqlite3.OperationalError as e:
					error = str(e)
					if error[:13] == 'no such table':
						results.write(f'\ntried dropping nonexistent table: test.{error[15:]}')
						con.rollback()
						continue
				else:
					results.write(f'\ndropped table: test.{table._table_name}')
		self.init_dbs(testing=True, results=results)
		results.write('\n\n')
		print(results.getvalue())


###############################################################################

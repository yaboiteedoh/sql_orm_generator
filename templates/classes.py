class SQLiteTable:
    #override in the child class
    def __init__(self):
        self.db_dir = 'path'
        self.dataclass = None
        self._table_name = 'base'

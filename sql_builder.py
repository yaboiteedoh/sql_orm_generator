import json
from pathlib import Path
from io import StringIO
from sys import argv


###############################################################################


def main():
    modules = {}
    dataclasses = StringIO()
    database = StringIO()
    root_in_py = StringIO()
    database = StringIO()

    with open(f'{argv[1]}.json') as f:
        db_config = json.load(f)

    db = Path('database')
    db.mkdir()

    in_py = Path('database', '__init__.py')
    with open(in_py, 'w') as f:
        f.write('from .database import Database')

    classes = Path('database', 'classes.py')
    with open('table_base_class.py', 'r') as f:
        base_class = f.read()
    with open(classes, 'w') as f:
        f.write(base_class.replace('    ', '\t'))

    create_table_classes(db_config, modules)
    create_table_dataclasses(db_config, dataclasses)
    create_database_class(db_config, database)
    create_filesystem(db_config, modules)

    dc_path = Path('database', 'dataclasses.py')
    with open(dc_path, 'w') as f:
        f.write(dataclasses.getvalue().replace('    ', '\t'))

    database_path = Path('database', 'database.py')
    with open(database_path, 'w') as f:
        f.write(database.getvalue().replace('    ', '\t'))
    

###############################################################################


def create_database_class(db_config, b):
    b.write(
        '''
import sqlite3
from io import StringIO

'''
)
    for table in db_config:
        b.write(f'from .{table['table_name']} import {table['table_name']}_table\n')

    b.write('''
    
###############################################################################


class Database:
    def __init__(self, testing=False):
        results = StringIO() if testing else None
    
''')
    for table in db_config:
        b.write(f'\t\t\tself.{table['table_name']} = {table['table_name']}(testing)\n')

    b.write('\n\t\t\tself.build_sequence = [\n')
    for i, table in enumerate(db_config):
        if i < len(db_config) - 1:
            b.write(f'\t\t\t\tself.{table['table_name']},\n')
        else:
            b.write(
                f'''
                self.{table['table_name']}
            ]

            if testing:
                try:
                    self._test(results)
                except BaseException as e:
                    print(results.getvalue())
                    raise e

'''
            )
    b.write(
        '''
    #------------------------------------------------------# 


    def init_dbs(self, testing=False, results=None):
        for table in self.build_sequence:
            table.init_db()
            if testing:
                results.write(f'\\n\\ninitializing {table._table_name} table')
                table._test(results)


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


    def _test(self, results, version_number):
        results.write(f'\\n\\n\\tSTARTING DATABASE INTEGRATION TEST\\n\\n')
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
                        results.write(f'\\ntried dropping nonexistent table: test.{error[15:]}')
                        con.rollback()
                        continue
                else:
                    results.write(f'\\ndropped table: test.{table._table_name}')
        self.init_dbs(testing=True, results=results)
        results.write('\\n\\n')
        print(results.getvalue())


###############################################################################
'''
            )


def create_filesystem(db_config, modules):
    for table in db_config:
        create_package(table, modules[table['table_name']])


def create_table_dataclasses(db_config, dataclasses):
    dataclasses.write(
        '''
from dataclasses import dataclass, field, asdict


###############################################################################

'''
    )
    for table in db_config:
        create_dataclass(table, table['dataclass_name'], dataclasses)
    dataclasses.write('\n###############################################################################')


def create_dataclass(table, dataclass_name, b):
    b.write(
        f'''
@dataclass(slots=True)
class {dataclass_name}:
'''
    )
    for key_name, key in table['group_keys'].items():
        python_type = type_map(key['type'])
        b.write(f'\t{key_name}: {python_type}\n')
    for key_name, key in table['object_keys'].items():
        python_type = type_map(key['type'])
        b.write(f'\t{key_name}: {python_type}\n')
    for key_name, key in table['other_keys'].items():
        python_type = type_map(key['type'])
        b.write(f'\t{key_name}: {python_type}\n')
    b.write(
        '''
    @property
    def as_dict(self):
        return asdict(self)

'''
    )


def create_table_classes(db_config, modules):
    initialize_buffers(db_config, modules)

    for table in db_config:
        create_module(modules[table['table_name']])

    for table in db_config:
        table_name = table['table_name']
        config_dict = initialize_class(modules[table_name], table['table_name'], table)
        build_table(**config_dict)


def initialize_buffers(db_config, modules):
    for table in db_config:
        modules[table['table_name']] = StringIO()


def create_package(table, class_buffer):
    package = Path('database', table['table_name'])
    class_file = Path('database', table['table_name'], '_0_0.py')
    init_file = Path('database', table['table_name'], '__init__.py')
    package.mkdir()
    init_buffer = StringIO()
    init_buffer.write(
        f'''
def {table['table_name']}_table():
    from ._0_0 import {table['table_name']}_table

    return {table['table_name']}_table


###############################################################################
'''
    )
    with open(class_file, 'w') as f:
        f.write(class_buffer.getvalue().replace('    ', '\t'))

    with open(init_file, 'w') as f:
        f.write(init_buffer.getvalue().replace('    ', '\t'))



def create_module(buffer):
    buffer.write(
            '''
import sqlite3
from pathlib import Path
from io import StringIO

from database.classes import SQLiteTable
'''
    )


def initialize_class(buffer, table_name, table_config):
    dataclass = ''
    group_keys = {}
    object_keys = {}
    other_keys = {}
    for option, value in table_config.items():
        match option:
            case 'dataclass_name':
                dataclass = value
            case 'group_keys':
                group_keys = value
            case 'object_keys':
                object_keys = value
            case 'other_keys':
                other_keys = value
    buffer.write(f'from database.dataclasses import {dataclass}\n\n\n')
    buffer.write('###############################################################################\n\n\n')
    return {
            'b': buffer,
            'table_name': table_name,
            'dataclass': dataclass,
            'group_keys': group_keys,
            'object_keys': object_keys,
            'other_keys': other_keys
        }


def build_table(
    b,
    table_name,
    dataclass,
    group_keys,
    object_keys,
    other_keys
):
    b.write(
        f"""class {table_name.capitalize()}Table(SQLiteTable):
    def __init__(self, testing=False):
        if not testing:
            self.db_dir = str(Path('database', 'data.db')
        else:
            self.db_dir = str(Path('database', 'test.db')
        self.dataclass = {dataclass}

        self._table_name = '{table_name}'
"""
    )

    b.write('\tself._group_keys = {\n')
    for i, key in enumerate(group_keys.keys()):
        b.write(f"\t\t'{key}': self.read_by_{key}")
        if i == len(group_keys.keys()) - 1:
            b.write('\n')
        else:
            b.write(',\n')
    else:
        b.write('\t}\n')

    b.write('\tself._object_keys = {\n')
    for i, key in enumerate(object_keys.keys()):
        b.write(f"\t\t'{key}': self.read_by_{key}")
        if i == len(object_keys.keys()) - 1:
            b.write('\n')
        else:
            b.write(',\n')
    else:
        b.write('\t}')

    b.write(
        f"""
        self._test_data = test_data


    #------------------------------------------------------#


    def init_db(self):
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                CREATE TABLE {table_name}(
"""
    )

    rowid = ('rowid', {'type': 'INT', 'params': 'PRIMARY KEY AUTOINCREMENT'})
    
    keys = []
    for item in group_keys.items():
        keys.append(item)
    for item in object_keys.items():
        keys.append(item)
    for item in other_keys.items():
        keys.append(item)

    keys.append(rowid)
    foreign_keys = []

    for i, key in enumerate(keys):
        key_name, key_type, key_params, key_references = unpack_key(key)
        if key_references is not None:
            foreign_keys.append((key_name, key_references))
        b.write(f'\t\t\t\t\t{key_name} {key_type} {key_params}')
        if i == len(keys) - 1:
            if foreign_keys != []:
                b.write(',')
                for f_key, references in foreign_keys:
                    b.write(f'\n\t\t\t\t\tFOREIGN KEY({f_key})\n\t\t\t\t\t\tREFERENCES {references}')
        else:
            b.write(',\n')
    else:
        b.write(
            f"""
                )
            '''
            cur.execute(sql)

            
    #------------------------------------------------------# 


    def add(self, {table_name[:-1]}: {dataclass}) -> int:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                INSERT INTO {table_name}(
"""
        )

    for i, key in enumerate(keys):
        key_name, key_type, key_params, _ = unpack_key(key)
        if i < len(keys) - 1:
            b.write(f'\t\t\t\t\t{key_name},\n')
        else:
            b.write('\t\t\t\t)\n\t\t\t\tVALUES (\n')

    for i, key in enumerate(keys):
        key_name, key_type, key_params, _ = unpack_key(key)
        if i < len(keys) - 1:
            b.write(f'\t\t\t\t\t:{key_name},\n')
        else:
            b.write(
                f"""\t\t\t\t)
            '''
            cur.execute(sql, team.as_dict)
            return cur.lastrowid

            
    #------------------------------------------------------# 


    def read_all(self) -> list[{dataclass}]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM {table_name}'
            cur.execute(sql)
            return cur.fetchall()


    def read_by_rowid(self, rowid: int) -> {dataclass}:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM {table_name} WHERE rowid=?'
            cur.execute(sql)
            return cur.fetchone()
"""
            )

    for key_name, key in group_keys.items():
        python_type = type_map(key['type'])
        b.write(
            f'''

    def read_by_{key_name}(self, {key_name}: {python_type}) -> list[{dataclass}]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM {table_name} WHERE {key_name}=?'
            cur.execute(sql, ({key_name},))
            return cur.fetchall()
'''
        )

    for key_name, key in object_keys.items():
        python_type = type_map(key['type'])
        b.write(
            f'''

    def read_by_{key_name}(self, {key_name}: {python_type}) -> {dataclass}:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM {table_name} WHERE {key_name}=?'
            cur.execute(sql, ({key_name},))
            return cur.fetchone()
'''
        )

    b.write(
        f'''

def {table_name}_table(testing=False):
    return {table_name.capitalize()}Table(testing)


###############################################################################
'''
    )


def unpack_key(key):
    key_name, key_dict = key
    key_type = key_dict['type']
    key_params = key_dict['params']
    key_references = None
    if 'references' in key_dict.keys():
        key_references = key_dict['references']
    return (key_name, key_type, key_params, key_references)


def type_map(t):
    tm = {'TEXT': 'str', 'INT': 'int'}
    return tm[t]


###############################################################################


if __name__ == "__main__":
    main()


###############################################################################

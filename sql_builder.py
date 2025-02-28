import json
from io import StringIO
from sys import argv


###############################################################################


def main():
    modules = {}
    classes = StringIO()
    dataclasses = StringIO()
    database = StringIO()

    with open(f'{argv[1]}.json') as f:
        db_config = json.load(f)

    initialize_buffers(db_config, modules)
    
    for table_name in db_config.keys():
        create_module(modules[table_name])

    for table_name, table_config in db_config.items():
        config_dict = initialize_class(modules[table_name], table_name, table_config)
        build_table(**config_dict)

    for module, buffer in modules.items():
        # print(module, '\n\t', buffer)
        print(buffer.getvalue())


###############################################################################


def initialize_buffers(db_config, modules):
    for table_name in db_config.keys():
        modules[table_name] = StringIO()


def create_module(buffer):
    buffer.write(
            '''
import sqlite3
from pathlib import Path
from io import StringIO

from utils.classes import SQLiteTable
'''
    )


def initialize_class(buffer, table_name, table_config):
    dataclass = ''
    group_keys = {}
    object_keys = {}
    for option, value in table_config.items():
        match option:
            case "dataclass_name":
                dataclass = value
            case "group_keys":
                group_keys = value
            case "object_keys":
                object_keys = value
    buffer.write(f'from utils.dataclasses import {dataclass}\n\n\n')
    buffer.write('###############################################################################\n\n\n')
    return {
            'b': buffer,
            'table_name': table_name,
            'dataclass': dataclass,
            'group_keys': group_keys,
            'object_keys': object_keys
        }


def build_table(
    b,
    table_name,
    dataclass,
    group_keys,
    object_keys
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

    keys.append(rowid)
    foreign_keys = []

    for i, key in enumerate(keys):
        key_name, key_type, key_params, key_references = unpack_key(key)
        if key_references is not None:
            foreign_keys.append((key_name, key_references))
        b.write(f'\t\t\t{key_name} {key_type} {key_params}')
        if i == len(keys) - 1:
            if foreign_keys != []:
                b.write(',')
                for f_key, references in foreign_keys:
                    b.write(f'\n\t\t\tFOREIGN KEY({f_key})\n\t\t\t\tREFERENCES {references}')
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
            b.write(f'\t\t\t{key_name},\n')
        else:
            b.write('\t\t)\n\t\tVALUES (\n')

    for i, key in enumerate(keys):
        key_name, key_type, key_params, _ = unpack_key(key)
        if i < len(keys) - 1:
            b.write(f'\t\t\t:{key_name},\n')
        else:
            b.write(
                f"""\t\t)
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
        type_map = {'TEXT': 'str', 'INT': 'int'}
        python_type = type_map[key['type']]
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
        type_map = {'TEXT': 'str', 'INT': 'int'}
        python_type = type_map[key['type']]
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


###############################################################################


if __name__ == "__main__":
    main()


###############################################################################

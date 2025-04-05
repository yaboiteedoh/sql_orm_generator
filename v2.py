import json
from io import StringIO
from pathlib import Path
from sys import argv

from jinja2 import Template


###############################################################################


def main():
    with open(f'{argv[1]}.json') as f:
        db_config = json.load(f)
    for db_name, config in db_config.items():
        db = Database(db_name, config)
        generate_module(db)


###############################################################################


TABLE = Path('templates', 'table.txt')


###############################################################################


class Database:
    def __init__(
        self,
        db_name,
        tables
    ):
        self.name = db_name
        self.tables = [Table(**table) for table in tables]


class Table:
    def __init__(
        self,
        table_name,
        dataclass_name,
        keys,
        groups,
        filters,
        join=False
    ):
        self.references = False
        self.join = join
        self.name = table_name
        self.dataclass = dataclass_name

        self.keys = [DBKey(**key) for key in keys]
        self.length = len(self.keys) - 1
        self.list_keys = [
            key for key in self.keys
            if 'returns' in key.classes.check
            and key.classes.returns == 'group'
        ]
        self.single_keys = [
            key for key in self.keys
            if 'returns' in key.classes.check
            and key.classes.returns == 'single'
        ]
        self.other_keys = [
            key for key in self.keys
            if not key.classes.check
        ]
        for key in self.keys:
            if 'references' in key.classes.check:
                self.references = True

        self.key_groups = [
            DBKeyGroup(self.keys, **group)
            for group in groups
        ]
        self.filters = [
            DBKeyFilter(self.keys, **filter)
            for filter in filters
        ]


class DBKey:
    def __init__(
        self,
        name,
        data_type,
        params,
        key_class_dict
    ):
        self.name = name
        self.data_type = data_type
        self.params = params
        self.classes = DBKeyClass(**key_class_dict)

        match self.data_type:
            case 'TEXT':
                self.py_data_type = 'str'
            case 'INTEGER':
                self.py_data_type = 'int'
            case _:
                self.py_data_type = f'INVALID DATA TYPE IN CONFIG: {self.data_type}'


class DBKeyGroup:
    def __init__(
        self,
        key_list,
        name,
        keys
    ):
        self.name = name
        self.keys = [
            key for key in key_list
            if key.name in keys
        ]
        self.length = len(self.keys) - 1


class DBKeyFilter:
    def __init__(
        self,
        key_list,
        name,
        keys
    ):
        self.name = name
        self.keys = []
        self.keys = [
            key for key in key_list
            if key.name in keys
        ]
        self.length = len(self.keys) - 1


class DBKeyClass:
    def __init__(
        self,
        returns=None,
        references=None,
        group=None,
        filters=None
    ):
        self.check = []
        if returns:
            self.check.append('returns')
        if references:
            self.check.append('references')
        if group:
            self.check.append('group')
        if filters:
            self.check.append('filters')

        self.returns = returns
        self.references = references
        self.group = group
        self.filters = filters


###############################################################################


def generate_module(db: Database):
    fs = generate_filesystem(db)
    
    for table in db.tables:
        render_table_template(table, fs)


def generate_filesystem(db):
    fs = {}
    fs['path'] = Path(db.name)
    fs['path'].mkdir()
    fs['init'] = Path(db.name, '__init__.py')
    fs['database'] = Path(db.name, 'database.py')

    fs['tables'] = {}
    fs['tables']['path'] = Path(db.name, 'tables')
    fs['tables']['path'].mkdir()
    fs['tables']['init'] = Path(db.name, 'tables', '__init__.py')

    fs['classes'] = {}
    fs['classes']['path'] = Path(db.name, 'classes')
    fs['classes']['path'].mkdir()
    fs['classes']['init'] = Path(db.name, 'classes', '__init__.py')
    fs['classes']['classes'] = Path(db.name, 'classes', 'classes.py')
    fs['classes']['dataclasses'] = Path(db.name, 'classes', 'dataclasses.py')
    
    for table in db.tables:
        fs['tables'][table.name] = Path(db.name, 'tables', f'{table.name}.py')
    return fs


def render_table_template(table: Table, fs):
    with open(TABLE, 'r') as f:
        template_string = f.read()
    
    template = Template(template_string)
    table_class = template.render(
        table=table,
        enumerate=enumerate
    )
    
    with open(fs['tables'][table.name], 'w') as f:
        f.write(table_class)


###############################################################################


if __name__ == '__main__':
    main()


###############################################################################

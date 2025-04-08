import json
from io import StringIO
from pathlib import Path
from sys import argv, exit

from jinja2 import Template


###############################################################################


def main():
    try:
        json_filename = argv[1]
    except IndexError:
        print('Please provide a valid config filename')
        exit(1)

    with open(f'{json_filename}.json') as f:
        db_config = json.load(f)
    for db_name, config in db_config.items():
        db = Database(db_name, config)
        generate_module(db)


###############################################################################


TABLE_TEMPLATE = Path('templates', 'table.txt')


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

        self.key_groups = [
            DBKeyGroup(self.keys, **group)
            for group in groups
        ]
        self.filters = [
            DBKeyFilter(self.keys, self.key_groups, **filter)
            for filter in filters
        ]

        for key in self.keys:
            if 'references' in key.classes.check:
                self.references = True


class DBKey:
    def __init__(
        self,
        name,
        data_type,
        params,
        key_class_dict
    ):
        self.data_type = data_type
        match self.data_type:
            case 'TEXT':
                self.py_data_type = 'str'
            case 'INTEGER':
                self.py_data_type = 'int'
            case _:
                msg = f'INVALID DATA TYPE IN CONFIG: {self.name}, {self.data_type}'
                raise NotImplementedError(msg)

        self.name = name
        self.params = params
        self.classes = DBKeyClass(**key_class_dict)


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
        self.py_data_type = self.keys[0].py_data_type


class DBKeyFilter:
    def __init__(
        self,
        key_list,
        group_list,
        name,
        keys
    ):
        self.name = name
        self.keys = [
            key for key in key_list
            if key.name in keys
        ]
        self.groups = [
            group for group in group_list
            if group.name in keys
        ]
        self.queries = self.keys + self.groups
        self.length = len(self.queries) - 1


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
    with open(TABLE_TEMPLATE, 'r') as f:
        template_string = f.read()
    
    template = Template(template_string)
    table_class = template.render(
        table=table,
        enumerate=enumerate,
        isinstance=isinstance,
        DBKeyGroup=DBKeyGroup
    )
    
    with open(fs['tables'][table.name], 'w') as f:
        f.write(table_class)


###############################################################################


if __name__ == '__main__':
    main()


###############################################################################

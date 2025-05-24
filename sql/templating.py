import json
import os
import jinja2
from pathlib import Path


templates = os.path.expanduser('~/dev/sql_orm_generator/sql/templates/')
env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))

TABLE = env.get_template('table.txt')


def generate_filesystem(db):
    fs = {'path': Path(db.name)}
    fs['path'].mkdir()
    fs['init'] = Path(db.name, '__init__.py')
    fs['database'] = Path(db.name, 'database.py')
    fs['config'] = Path(db.name, f'{db.name}_config.json')

    fs['tables'] = {'path': Path(db.name, 'tables')}
    fs['tables']['path'].mkdir()
    fs['tables']['init'] = Path(db.name, 'tables', '__init__.py')

    fs['classes'] = {'path': Path(db.name, 'classes')}
    fs['classes']['path'].mkdir()
    fs['classes']['init'] = Path(db.name, 'classes', '__init__.py')
    fs['classes']['classes'] = Path(db.name, 'classes', 'classes.py')
    fs['classes']['dataclasses'] = Path(db.name, 'classes', 'dataclasses.py')

    for table in db.tables:
        fs['tables'][table.name] = Path(db.name, 'tables', f'{table.name}.py')

    return fs


def generate_module(db, fs):
    for table in db.tables:
        render_table_template(table, fs)


def render_table_template(table, fs):
    table_class = TABLE.render(
        table=table,
        enumerate=enumerate
    )

    with open(fs['tables'][table.name], 'w') as f:
        f.write(table_class)

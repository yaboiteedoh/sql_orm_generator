import json
import os
import jinja2
from pathlib import Path


templates = os.path.expanduser('~/dev/sql_orm_generator/sql/templates/')
env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))

TABLE = env.get_template('table.txt')
CLASSES = env.get_template('classes.txt')
DATACLASSES = env.get_template('dataclasses.txt')
DATABASE = env.get_template('database.txt')
TABLE_INIT = env.get_template('table_init.txt')


def generate_filesystem(path, db):
    fs = {
        'path': Path(path, db.name).resolve(),
        'init': Path(path, db.name, '__init__.py').resolve(),
        'database': Path(path, db.name, 'database.py').resolve(),
        'config': Path(path, db.name, f'{db.name}_config.json').resolve(),
        'tables': {
            'path': Path(path, db.name, 'tables').resolve(),
            'init': Path(path, db.name, 'tables', '__init__.py').resolve()
        },
        'classes': {
            'path': Path(path, db.name, 'classes').resolve(),
            'init': Path(path, db.name, 'classes', '__init__.py').resolve(),
            'classes': Path(path, db.name, 'classes', 'classes.py').resolve(),
            'dataclasses': Path(path, db.name, 'classes', 'dataclasses.py').resolve(),
        },
        'data': {
            'path': Path(path, db.name, 'data').resolve(),
            'db': Path(path, db.name, 'data', 'data.db').resolve()
        }
    }

    for table in db.tables:
        fs['tables'][table.name] = Path(db.name, 'tables', f'{table.name}.py')

    return fs


def generate_module(db, fs):
    for dir in [
        fs['path'],
        fs['tables']['path'],
        fs['classes']['path'],
        fs['data']['path']
    ]:
        dir.mkdir()

    open(fs['data']['db'], 'w').close()
    open(fs['classes']['init'], 'w').close()

    with open(fs['classes']['classes'], 'w') as f:
        f.write(CLASSES.render())

    with open(fs['init'], 'w') as f:
        f.write('from .database import Database')

    for table in db.tables:
        table_class = TABLE.render(
            table=table,
            enumerate=enumerate,
            db_name=db.name
        )
        with open(fs['tables'][table.name], 'w') as f:
            f.write(table_class)

    for template, location in {
        DATABASE: fs['database'],
        DATACLASSES: fs['classes']['dataclasses'],
        TABLE_INIT: fs['tables']['init']
    }.items():
        rendered_template = template.render(
            tables=db.tables
        )
        with open(location, 'w') as f:
            f.write(rendered_template)


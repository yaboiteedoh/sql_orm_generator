# sql_orm_generator
an orm generator that spits out a complete database object based on a json config file detailing your sql tables

## operation
to generate a module, run `python3 v2.py {target json file (in root directory of the generator)}`
to use the generated module, just drop it in to your project, and import it like a custom module

`from {database name} import Database`
- instantiating the database object initializes the sql tables locally

reach into each table to manipulate its data. The `__init__()` function of each table will show you a directory of relevant functions

## functionality
aside from being able to detail which columns you want query functions for, there's also support for
- grouping columns, to return any objects with data matching the single input value
- filtering columns, to return any objects that meet all query requirements

## json format
```
{
    'database name': [
        'table name':
            'name of the table',
        'dataclass name':
            'name of the associated dataclass',
        'keys': [
            {
                'name': 
                    'name of the corresponding db column',
                'data_type':
                    'SQL data type, converted to python data type internall'
                'params':
                    'SQL Parameters (AUTOINCREMENT, NOT NULL, ...) all in one string'
                'key_class_dict': {
                    'returns':
                        '"list" or "group" to determine fetchall vs fetchone',
                    'references':
                        '"table(key name)" of the referenced column'
                }
            }
        ],
        'groups': [
            {
                'name': 
                    'name of the group, used for function names',
                'keys': [
                    'key name',
                    'key name',
                    ...
                ]
            }
        ],
        'filters': [
            {
                'name':
                    'name of the filter, used for function names',
                'keys': [
                    'key name',
                    'key name',
                    ...
                ]
            }
        ]
    ]
}


## TODO
### Filters
- allow for filtering with groups

### Templates
- `root/__init__.py`
- `root/database.py`
- `tables/__init__.py`
- `classes/classes.py`
- `classes/dataclasses.py`

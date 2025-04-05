# sql_orm_generator
an orm generator that spits out a complete database object based on a json config file detailing your sql tables.
the generated code is meant to be boilerplate, to be built upon as needed, but works with standard library so as to be lightweight and flexible for any implementation.

## operation
to generate a module, run `python3 v2.py {target json file (in root directory of the generator)}`.
to use the generated module, just drop it in to your project, and import it like a custom module.

`from {database name} import Database`
- instantiating the database object initializes the sql tables locally.

reach into each table to manipulate its data. The `__init__()` function of each table will show you a directory of relevant functions.

## functionality
aside from being able to detail which columns you want query functions for, there's also support for
- grouping columns, to return any objects with data matching the single input value.
- filtering columns, to return any objects that meet all query requirements.
- generating multiple parallel db files, though currently each gets output to a different module
    - I may instead rework this to create multiple database classes in the same main database module which all get sent to the `root/__init__.py`

## json format
```
{
    'database name': [....................... list of tables
        {
            'table name':
                'name of the table',
            'dataclass name':
                'name of the associated dataclass',
            'keys': [............................ list of sql columns
                {
                    'name': 
                        'name of the corresponding db column',
                    'data_type':
                        'SQL data type, converted to python data type internally'
                    'params':
                        'SQL Parameters (AUTOINCREMENT, NOT NULL, ...) all in one string'
                    'key_class_dict': {
                        'returns':
                            '"list" or "group" to determine fetchall vs fetchone',
                        'references':
                            '"table(key name)" of the referenced column'
                    }
                },
                ...
            ],
            'groups': [.......................... list of similar sql columns
                {
                    'name': 
                        'name of the group, used for function names',
                    'keys': [
                        'key name',
                        'key name',
                        ...
                    ]
                },
                ...
            ],
            'filters': [......................... list of contextual sql columns
                {
                    'name':
                        'name of the filter, used for function names',
                    'keys': [
                        'key name',
                        'key name',
                        ...
                    ]
                },
                ...
            ]
        },
        ...
    ],
    ...
}
```

## TODO
### Filters
- allow for filtering with groups

### Join Tables
- seperate table class
    - inhreits from SQLiteTable
    - gonna need to adjust the templating according to join syntax
- this is gonna change fastest as I learn more about joins, which will test this system's ability to grow as my dev journey continues

### Templates
- `root/__init__.py`
- `root/database.py`
- `tables/__init__.py`
- `tables/join_table.py`
- `classes/classes.py`
- `classes/dataclasses.py`

### Shell Functionality
- package as a cli operable dev tool
- `sql_gen {json file}` to read a config file anywhere and generate a python module locally

### Frontend
- couple options here
    - web app consisting of a dynamic form to generate a config file
    - godot app that does the same thing without having to run flask
        - I think I can use the http request node to build out a rudimentary update system on remote devices
        - This option is also more secure, as I don't have to worry about managing any user data whatsoever
        - file browser node to control output location

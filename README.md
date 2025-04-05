# sql_orm_generator
an orm generator that spits out a complete database object based on a json config file detailing your sql tables

# json format
```
{
    'database name': [
        'table name':
            '*name of the table*',
        'dataclass name':
            '*name of the associated dataclass*',
        'keys': [
            {
                'name': 
                    '*name of the corresponding db column*',
                'data_type':
                    '*SQL data type, converted to python data type internall*'
                'params':
                    '*SQL Parameters (AUTOINCREMENT, NOT NULL, ...) all in one string*'
                'key_class_dict': {
                    'returns':
                        '*"list" or "group" to determine fetchall vs fetchone*',
                    'references':
                        '*"table(key name)" of the referenced column*'
                }
            }
        ],
        'groups': [
            {
                'name': 
                    '*name of the group, used for function names*',
                'keys': [
                    '*key name*'
                    '*key name*'
                    ...
                ]
            }
        ],
        'filters': [
            {
                'name':
                    '*name of the filter, used for function names*',
                'keys': [
                    '*key name*',
                    '*key name*',
                    ...
                ]
            }
        ]
    ]
}
```

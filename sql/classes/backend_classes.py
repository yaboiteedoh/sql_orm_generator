class Database:
    def __init__(
        self,
        db_name,
        tables
    ):
        self.name = db_name
        self.tables = [Table(**table) for table in tables]

        self.validate()


    def validate(self):
        table_names = [table.name for table in self.tables]

        if not self.name:
            msg = 'TRIED TO GENERATE UNNAMED DATABASE'
            raise ValueError(msg)

        for table in self.tables:
            column_names = [column.name for column in table.columns]
            group_names = [group.name for group in table.groups]
            filter_names = [filter.name for filter in table.filters]

            if (not table.name or len(table.name) < 1):
                msg = f'INVALID TABLE NAME: {table.name if table.name else "NONE"}'
                raise ValueError(msg)

            if table_names.count(table.name) > 1:
                msg = f'DATABASE CONTAINS DUPLICATE TABLES {table.name}'
                raise ValueError(msg)

            for column in table.columns:
                if not column.name:
                    msg = f'TABLE {table.name} CONTAINS AN UNNAMED COLUMN'
                    raise ValueError(msg)
                if column.name == 'rowid':
                    msg = f'TABLE {table.name} INCLUDES A ROWID COLUMN\n\tThis column is automatically generated'
                    raise ValueError(msg) 

                if column_names.count(column.name) > 1:
                    msg = f'TABLE {table.name} CONTAINS DUPLICATE COLUMNS {column.name}'
                    raise ValueError(msg)
                
                if 'references' in column.classes.check:
                    target_table, target_column = column.classes.references.split('(')
                    target_column = target_column[:-1]
                    target_table_check = [
                        t for t in self.tables
                        if t.name == target_table
                    ]
                    if not target_table_check:
                        msg = f'REFERENCE COLUMN {column.name} ON TABLE {table.name} REFERENCES NONEXISTENT TABLE {column.classes.references}'
                        raise ValueError(msg)
                    target_column_check = [
                        t for t in target_table_check[0].columns
                        if t.name == target_column
                    ]
                    if (not target_column_check and target_column != 'rowid'):
                        msg = f'REFERENCE COLUMN {column.name} ON TABLE {table.name} REFERENCES NONEXISTENT COLUMN {column.classes.references}'
                        raise ValueError(msg)

                if 'returns' in column.classes.check:
                    if (
                        not column.classes.returns
                        or column.classes.returns not in ['group', 'single']
                    ):
                        msg = f'RETURN COLUMN {column.name} ON TABLE {table.name} HAS AN INVALID RETURN TYPE'
                        raise ValueError(msg)

            for group in table.groups:
                if not group.name:
                    msg = f'TABLE {table.name} CONTAINS AN UNNAMED GROUP'
                    raise ValueError(msg) 

                if group_names.count(group.name) > 1:
                    msg = f'TABLE {table.name} CONTAINS DUPLICATE GROUPS {group.name}'
                    raise ValueError(msg)

                for target_column in group.columns:
                    target_column_check = [
                        t for t in table.columns
                        if t == target_column
                    ]
                    if not target_column_check:
                        msg = f'COLUMN GROUP {group.name} ON TABLE {table.name} CONTAINS A NONEXISTENT COLUMN {target_column.name}'
                        raise ValueError(msg)

            for filter in table.filters:
                if not filter.name:
                    msg = f'TABLE {table.name} CONTAINS AN UNNAMED FILTER'
                    raise ValueError(msg) 

                if filter_names.count(filter.name) > 1:
                    msg = f'TABLE {table.name} CONTAINS DUPLICATE FILTERS {filter.name}'
                    raise ValueError(msg)

                for target_column in filter.columns:
                    target_column_check = [
                        t for t in table.columns
                        if t == target_column
                    ]
                    if not target_column_check:
                        msg = f'FILTER {filter.name} ON TABLE {table.name} CONTAINS A NONEXISTENT COLUMN {target_column.name}'
                        raise ValueError(msg)

                for target_group in filter.groups:
                    target_group_check = [
                        t for t in table.groups
                        if t == target_group
                    ]
                    if not target_group_check:
                        msg = f'FILTER {filter.name} ON TABLE {table.name} CONTAINS A NONEXISTENT GROUP {target_group.name}'
                        raise ValueError(msg)


class Table:
    def __init__(
        self,
        table_name,
        dataclass_name,
        columns,
        groups,
        filters,
        join=False
    ):
        self.references = False
        self.join = join
        self.name = table_name
        self.dataclass = dataclass_name

        self.columns = [Column(**column) for column in columns]
        self.length = len(self.columns) - 1
        self.list_columns = [
            column for column in self.columns
            if 'returns' in column.classes.check
            and column.classes.returns == 'group'
        ]
        self.single_columns = [
            column for column in self.columns
            if 'returns' in column.classes.check
            and column.classes.returns == 'single'
        ]
        self.other_columns = [
            column for column in self.columns
            if not 'returns' in column.classes.check
        ]

        self.groups = [
            Group(self.columns, **group)
            for group in groups
        ]
        self.filters = [
            Filter(self.columns, self.groups, **filter)
            for filter in filters
        ]

        for column in self.columns:
            if 'references' in column.classes.check:
                self.references = True
                break


class Column:
    def __init__(
        self,
        name,
        data_type,
        params,
        column_class_dict
    ):
        match data_type:
            case 'TEXT':
                self.py_data_type = 'str'
            case 'INTEGER':
                self.py_data_type = 'int'
            case _:
                msg = f'INVALID DATA TYPE FOR COLUMN: {self.name}, {self.data_type}'
                raise ValueError(msg)

        self.data_type = data_type
        self.name = name
        self.params = params
        self.classes = ColumnClass(**column_class_dict)


class Group:
    def __init__(
        self,
        column_list,
        name,
        columns
    ):
        self.name = name
        self.columns = [
            column for column in column_list
            if column.name in columns
        ]
        self.length = len(self.columns) - 1
        self.py_data_type = self.columns[0].py_data_type


class Filter:
    def __init__(
        self,
        column_list,
        group_list,
        name,
        queries
    ):
        self.name = name
        self.columns = [
            column for column in column_list
            if column.name in queries 
        ]
        self.groups = [
            group for group in group_list
            if group.name in queries 
        ]
        self.queries = self.columns + self.groups
        self.length = len(self.queries) - 1


class ColumnClass:
    def __init__(
        self,
        returns=None,
        references=None
    ):
        self.check = []
        if returns:
            self.check.append('returns')
        if references:
            self.check.append('references')

        self.returns = returns
        self.references = references

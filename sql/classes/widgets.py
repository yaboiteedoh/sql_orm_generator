from tkinter import filedialog

import teedoh_kinter as tk

from utils import snake_case, pascal_case
from templating import generate_filesystem, generate_module
from file_config import save_config, load_config
from .classes import Database


class GroupFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columns = {}
        
        self.options = self.add_component(tk.Frame)
        self._group_name = self.options.add_component(
            tk.LabeledEntry,
            text='Group Name: '
        )
        self.options.add_component(
            tk.Button,
            text='Remove Group',
            command=lambda: self.parent.remove(self)
        )
        self.config_frame = self.add_component(
            tk.Frame,
            max_columns=2,
            grid_children=True
        )
        for column in self.parent.parent.columns.children:
            self.columns[column.name] = self.config_frame.add_component(
                tk.CheckButton,
                text=column.name
            )
        self.update()


    @property
    def name(self):
        return snake_case(self._group_name.value)


    @name.setter
    def name(self, value):
        self._group_name.value = value


    @property
    def config(self):
        return {
            'name': self.name,
            'columns': [
                snake_case(column)
                for column, active in self.columns.items()
                if active.value
            ]
        }


class FilterFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.queries = {}

        self.options = self.add_component(tk.Frame)
        self._filter_name = self.options.add_component(
            tk.LabeledEntry,
            text='Filter Name: '
        )
        self.options.add_component(
            tk.Button,
            text='Remove Filter',
            command=lambda: self.parent.remove(self)
        )
        self.config_frame = self.add_component(
            tk.Frame,
            max_columns=2,
            grid_children=True
        )
        for query in self.parent.parent.columns.children + self.parent.parent.groups.children:
            self.queries[query.name] = self.config_frame.add_component(
                tk.CheckButton,
                text=query.name
            )
        self.update()


    @property
    def name(self):
        return snake_case(self._filter_name.value)


    @name.setter
    def name(self, value):
        self._filter_name.value = value


    @property
    def config(self):
        return {
            'name': self.name,
            'queries': [
                snake_case(name)
                for name, obj in self.queries.items()
                if obj.active
            ]
        }


class ColumnFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.options = self.add_component(tk.Frame)
        self._column_name = self.options.add_component(
            tk.LabeledEntry,
            text='Column Name: '
        )
        self.options.add_component(
            tk.Button,
            text='Remove Column',
            command=lambda: self.parent.remove(self)
        )
        self.config_frame = self.add_component(tk.Frame)
        self.data_type_selector = self.config_frame.add_component(
            tk.Frame,
            grid_children=True
        )
        self.data_type_selector.add_component(
            tk.Label,
            text='Data Type: '
        )
        self._data_type = self.data_type_selector.add_component(
            tk.RadioMenu,
            options=['TEXT', 'INTEGER'],
            default='TEXT'
        )
        self._not_null = self.config_frame.add_component(
            tk.CheckButton,
            text='NOT NULL',
            data_type='str',
            values=['', 'NOT NULL']
        )
        self.return_selector = self.config_frame.add_component(
            tk.Frame,
            grid_children=True
        )
        self._returns = self.return_selector.add_component(
            tk.CheckButton,
            text='Returns'
        )
        self._unique = self.return_selector.add_component(
            tk.CheckButton,
            text='UNIQUE',
            data_type='str',
            values=['group', 'single']
        )
        self._returns.add_trace(lambda: self.toggle_return_selector())
        self.references_selector = self.config_frame.add_component(
            tk.Frame,
            grid_children=True
        )
        self._references = self.references_selector.add_component(
            tk.CheckButton,
            text='References'
        )
        self.table_selector = self.references_selector.add_component(
            tk.LabeledOption,
            text='Table: ',
            options=[]
        )
        self.column_selector = self.references_selector.add_component(
            tk.LabeledOption,
            text='Column: ',
            options=[]
        )
        self._references.add_trace(lambda: self.toggle_reference_selector())

        self.table_selector.menu.tkinter.bind(
            '<Button-1>',
            lambda e: self.update_tables()
        )
        self.column_selector.menu.tkinter.bind(
            '<Button-1>',
            lambda e: self.update_columns()
        )

        self.toggle_return_selector(value=False)
        self.toggle_reference_selector(value=False)

        self.update()


    @property
    def name(self):
        return snake_case(self._column_name.value)


    @name.setter
    def name(self, value):
        self._column_name.value = value


    @property
    def data_type(self):
        return self._data_type.value


    @data_type.setter
    def data_type(self, value):
        self._data_type.value = value


    @property
    def not_null(self):
        return self._not_null.value


    @not_null.setter
    def not_null(self, value):
        self._not_null.active = value


    @property
    def returns(self):
        return self._returns.value


    @returns.setter
    def returns(self, value):
        self._returns.active = value


    @property
    def unique(self):
        return self._unique.value


    @unique.setter
    def unique(self, value):
        self._unique.active = value


    @property
    def references(self):
        return self._references.value


    @references.setter
    def references(self, value):
        self._references.active = value


    @property
    def referenced_table(self):
        return self.table_selector.value

    
    @referenced_table.setter
    def referenced_table(self, value):
        self.table_selector.value = value


    @property
    def referenced_column(self):
        return self.column_selector.value


    @referenced_column.setter
    def referenced_column(self, value):
        self.column_selector.value = value


    def toggle_return_selector(self, value=None):
        v = value
        if value is None:
            v = self.returns
        self._unique.toggle_active(value=v)


    def toggle_reference_selector(self, value=None):
        v = value
        if value is None:
            v = self.returns
        self.table_selector.toggle_active(value=v), 
        self.column_selector.toggle_active(value=v)


    def update_tables(self):
        self.update()
        tables = [table.name for table in self.parent.parent.parent.parent.tables.children]
        self.table_selector.options = tables
        self.update()


    def update_columns(self):
        self.update()
        columns = None
        for table in self.parent.parent.parent.parent.tables.children:
            if table.name == self.referenced_table:
                columns = [column.name for column in table.columns.children] + ['rowid']
        if not columns:
            return
        self.column_selector.options = columns


    @property
    def config(self):
        params = ''
        if self.not_null:
            params += f' {self.not_null}'

        config_dict = {
            'name': self.name,
            'data_type': self.data_type,
            'params': params,
            'column_class_dict': {}
        }

        if self.returns:
            config_dict['column_class_dict']['returns'] = self.unique

        if self.references:
            references = f'{snake_case(self.referenced_table)}({snake_case(self.referenced_column)})'
            config_dict['column_class_dict']['references'] = references

        return config_dict


class TableFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.options = self.add_component(tk.Frame)
        self._table_name = self.options.add_component(
            tk.LabeledEntry,
            text='Table Name: '
        )
        self.options.add_component(
            tk.Button,
            text='Remove Table',
            command=lambda: self.parent.remove(self)
        )
        self._options_buttons = self.options.add_component(
            tk.ButtonMatrix,
            buttons=[
                'Add Column',
                'Clear Columns',
                'Add Group',
                'Clear Groups',
                'Add Filter',
                'Clear Filters'
            ]
        )
        self.columns = self.add_component(
            tk.DynamicComponentFrame,
            max_columns=0,
            child_class=ColumnFrame
        )
        self.groups = self.add_component(
            tk.DynamicComponentFrame,
            max_columns=0,
            child_class=GroupFrame
        )
        self.filters = self.add_component(
            tk.DynamicComponentFrame,
            max_columns=0,
            child_class=FilterFrame
        )
        for button in self._options_buttons.components:
            match button.text:
                case 'Add Column':
                    button.set_command(self.columns.add)
                case 'Clear Columns':
                    button.set_command(self.columns.clear)
                case 'Add Group':
                    button.set_command(self.groups.add)
                case 'Clear Groups':
                    button.set_command(self.groups.clear)
                case 'Add Filter':
                    button.set_command(self.filters.add)
                case 'Clear Filters':
                    button.set_command(self.filters.clear)

        self.update()


    @property
    def name(self):
        return snake_case(self._table_name.value)


    @name.setter
    def name(self, name):
        self._table_name.value = name


    @property
    def config(self):
        return {
            'table_name': self.name,
            'dataclass_name': pascal_case(self.name)[:-1],
            'columns': [column.config for column in self.columns.children],
            'groups': [group.config for group in self.groups.children],
            'filters': [filter.config for filter in self.filters.children]
        }


class DbFrame(tk.Frame):
    def __init__(self, parent, parent_frame, fill):
        super().__init__(parent, parent_frame=parent_frame, fill=fill)

        self.options = self.add_component(tk.Frame)
        self._db_name = self.options.add_component(
            tk.LabeledEntry,
            text='DB Name: '
        )
        self._options_buttons = self.options.add_component(
            tk.ButtonMatrix,
            max_columns=1,
            buttons=[
                'Add Table',
                'Clear Tables',
                'Import DB',
                'Export DB'
            ]
        )
        self.tables = self.add_component(
            tk.DynamicComponentFrame,
            child_class=TableFrame
        )
        for button in self._options_buttons.components:
            match button.text:
                case 'Add Table':
                    button.set_command(self.tables.add)
                case 'Clear Tables':
                    button.set_command(self.tables.clear)
                case 'Import DB':
                    button.set_command(self.import_db)
                case 'Export DB':
                    button.set_command(self.export_db)

        self.update()


    @property
    def name(self):
        return snake_case(self._db_name.value)


    @name.setter
    def name(self, name):
        self._db_name.value = name


    def import_db(self):
        config = load_config()

        self.tables.clear()

        for db_name, tables in config.items():
            self.name = db_name

            for table in tables:
                table_frame = self.tables.add()
                table_frame.name = table['table_name']

                for column in table['columns']:
                    column_frame = table_frame.columns.add()
                    column_frame.name = column['name']
                    column_frame.data_type = column['data_type']
                    if 'NOT NULL' in column['params']:
                        column_frame.not_null = True
                    if 'returns' in column['column_class_dict']:
                        column_frame.returns = True
                        if column['column_class_dict']['returns'] == 'single':
                            column_frame.unique = True

            for table in tables:
                table_frame = [
                    t for t in self.tables.children
                    if table['table_name'] == t.name
                ][0]
                table_frame.update()

                for column in table['columns']:
                    column_frame = [
                        c for c in table_frame.columns.children
                        if column['name'] == c.name
                    ][0]
                    
                    if 'references' in column['column_class_dict']:
                        column_frame.references = True

                        r_table, r_column = \
                            column['column_class_dict']['references'].split('(')
                        r_column = r_column[:-1]

                        column_frame.update_tables()
                        column_frame.update_columns()
                        column_frame.referenced_table = r_table
                        column_frame.referenced_column = r_column

                for group in table['groups']:
                    group_frame = table_frame.groups.add()
                    group_frame.name = group['name']
                    for column in group['columns']:
                        group_frame.columns[column].active = True

                for filter in table['filters']:
                    filter_frame = table_frame.filters.add()
                    filter_frame.name = filter['name']
                    for query in filter['queries']:
                        filter_frame.queries[query].active = True


    def export_db(self):
        config = self.config
        for db_name, tables_list in config.items():
            path = filedialog.askdirectory(title='Where to Save DB Module?')
            db = Database(db_name, tables_list)
            fs = generate_filesystem(path, db)
            generate_module(db, fs)
            save_config(config, fs)


    @property
    def config(self):
        return {self.name: [table.config for table in self.tables.children]}



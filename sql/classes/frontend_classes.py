import tkinter as tk
from tkinter import ttk

from utils import snake_case, pascal_case
from templating import generate_filesystem, generate_module
from file_config import save_config
from .components import COMPONENTS
from .backend_classes import Database


class Frame:
    def __init__(
        self,
        parent_obj=None,
        parent_frame=None,
        max_columns=False,
        grid_children=False
    ):
        self.parent_obj = parent_obj
        self.parent_frame = parent_frame
        self.max_columns = max_columns
        self.grid_children = grid_children

        self.frame = ttk.Frame(self.parent_frame)
        self.components = []

        self.cur_column = 0
        self.cur_row = 0

        self.build_frame()


    def build_frame(self):
        pass


    def update(self):
        self.parent_obj.update()


    def add_component(self, tk_type, params={}, parent=None):
        if not tk_type in COMPONENTS:
            raise NotImplementedError

        parent = parent if parent else self.frame
        component = COMPONENTS[tk_type](parent, **params)
        self.components.append(component)
        return component

    
    def child_frame(self, **kwargs):
        return Frame(parent_obj=self, parent_frame=self.frame, **kwargs)

    
    def pack(self):
        if self.grid_children:
            self.grid_components()
        else:
            self.pack_components(fill=tk.X)
        self.frame.pack(fill=tk.X)


    def grid_components(self):
        for component in self.components:
            component.grid(row=self.cur_row, column=self.cur_column, sticky=tk.NSEW)
            self.cur_column += 1

            if self.max_columns:
                if self.cur_column > self.max_columns:
                    self.cur_row += 1
                    self.cur_column = 0


    def countdown_cur_column():
        self.cur_column -= 1


    def pack_components(self, fill=None):
        for component in self.components:
            if fill:
                component.pack(fill=fill)
            else:
                component.pack(fill=tk.X)


class FilterFrame(Frame):
    def build_frame(self):
        self.queries = {}

        # Options frame contains structure relevant data and controls
        self.options_frame = self.child_frame(grid_children=True)
        self.options_frame.add_component(
            'label',
            {'text': 'Filter Name: '}
        )
        self.filter_name = self.options_frame.add_component('entry')
        self.options_frame.add_component(
            'button',
            {
                'text': 'Remove Filter',
                'command': lambda: self.parent_obj.remove_filter(self)
            }
        )
        self.options_frame.pack()

        # Config frame contains option controls
        self.config_frame = self.child_frame(max_columns=2, grid_children=True)
        for query in (self.parent_obj.column_names + self.parent_obj.group_names):
            self.queries[query] = tk.BooleanVar()
            self.queries[query].set(False)
            self.config_frame.add_component(
                'check_button',
                {
                    'text': query,
                    'variable': self.queries[query],
                    'onvalue': True,
                    'offvalue': False
                }
            )
        self.config_frame.pack()


    @property
    def name(self):
        return snake_case(self.filter_name.get())


    @property
    def config(self):
        return {
            'name': self.name,
            'queries': [
                snake_case(column)
                for column, active in self.queries.items()
                if active.get()
            ]
        }

                        
class GroupFrame(Frame):
    def build_frame(self):
        self.columns = {}
        
        # Options frame contains structure relevant data and controls
        self.options_frame = self.child_frame(grid_children=True)
        self.options_frame.add_component(
            'label',
            {'text': 'Group Name: '}
        )
        self.group_name = self.options_frame.add_component('entry')
        self.options_frame.add_component(
            'button',
            {
                'text': 'Remove Group',
                'command': lambda: self.parent_obj.remove_group(self)
            }
        )
        self.options_frame.pack()

        # Config frame contains option controls
        self.config_frame = self.child_frame(max_columns=2, grid_children=True)
        for column in self.parent_obj.column_names:
            self.columns[column] = tk.BooleanVar()
            self.columns[column].set(False)
            self.config_frame.add_component(
                'check_button',
                {
                    'text': column,
                    'variable': self.columns[column],
                    'onvalue': True,
                    'offvalue': False
                }
            )
        self.config_frame.pack()

    
    @property
    def name(self):
        return snake_case(self.group_name.get())


    @property
    def config(self):
        return {
            'name': self.name,
            'columns': [
                snake_case(column)
                for column, active in self.columns.items()
                if active.get()
            ]
        }


class ColumnFrame(Frame):
    def build_frame(self):
        self.data_type = tk.StringVar(value='TEXT')
        self.not_null = tk.StringVar(value = '')
        self.column_classes = {
            'returns': [
                tk.BooleanVar(),
                tk.StringVar(value='')
            ],
            'references': [
                tk.BooleanVar(),
                tk.StringVar(value=''),
                tk.StringVar(value='')
            ]
        }
        self.column_classes['returns'][0].set(False)
        self.column_classes['references'][0].set(False)

        # Options frame contains structure relevant data and controls
        self.options_frame = self.child_frame(max_columns=2, grid_children=True)
        self.options_frame.add_component(
            'label',
            {'text': 'Column Name: '}
        )
        self.column_name = self.options_frame.add_component('entry')
        self.options_frame.add_component(
            'button',
            {
                'text': 'Remove Column',
                'command': lambda: self.parent_obj.remove_column(self)
            }
        )
        self.options_frame.pack()
        
        # Config frame contains option controls
        self.config_frame = self.child_frame()

        self.data_type_selector = self.config_frame.child_frame(grid_children=True)
        self.data_type_selector.add_component(
            'label',
            {'text': 'Data Type: '}
        )
        for data_type in ['TEXT', 'INTEGER']:
            self.data_type_selector.add_component(
                'radio_button',
                {
                    'text': data_type,
                    'variable': self.data_type,
                    'value': data_type
                }
            )
        self.data_type_selector.pack()

        not_null_box = self.config_frame.add_component(
            'check_button',
            {
                'text': 'NOT NULL',
                'variable': self.not_null,
                'onvalue': 'NOT NULL',
                'offvalue': ''
            }
        )
        not_null_box.pack()

        self.column_class_frame = self.config_frame.child_frame(
            max_columns=2,
            grid_children=True
        )

        self.return_selector = self.column_class_frame.child_frame(grid_children=True)
        self.return_checkbox = self.return_selector.add_component(
            'check_button',
            {
                'text': 'Returns',
                'variable': self.column_classes['returns'][0],
                'onvalue': True,
                'offvalue': False,
                'command': self.toggle_return_selector
            }
        )
        for return_type in ['Single', 'Group']:
            self.return_selector.add_component(
                'radio_button',
                {
                    'text': return_type,
                    'variable': self.column_classes['returns'][1],
                    'value': return_type.lower()
                }
            )

        self.references_selector = self.column_class_frame.child_frame(
            grid_children=True
        )
        self.references_checkbox = self.references_selector.add_component(
            'check_button',
            {
                'text': 'References',
                'variable': self.column_classes['references'][0],
                'onvalue': True,
                'offvalue': False,
                'command': self.toggle_references_selector
            }
        )
        self.references_selector.add_component(
            'label',
            {'text': 'Table: '}
        )
        self.table_selector = self.references_selector.add_component(
            'option_menu',
            {
                'variable': self.column_classes['references'][1],
                'value': ''
            }
        )
        self.references_selector.add_component(
            'label',
            {'text': 'Column: '}
        )
        self.column_selector = self.references_selector.add_component(
            'option_menu',
            {
                'variable': self.column_classes['references'][2],
                'value': ''
            }
        )
        self.table_selector.bind('<Button-1>', lambda e: self.update_tables())
        self.column_selector.bind('<Button-1>', lambda e: self.update_columns())

        self.column_class_frame.pack()
        self.return_selector.grid_components()
        self.return_selector.frame.grid(column=1, row=0)
        self.references_selector.grid_components()
        self.references_selector.frame.grid(column=1, row=1)
        self.config_frame.pack()
        self.toggle_return_selector(value=False)
        self.toggle_references_selector(value=False)
        
        self.update()


    def toggle_return_selector(self, value=None):
        s = self.column_classes['returns'][0].get()
        if s != None:
            state = tk.NORMAL if s else tk.DISABLED

        if value != None:
            state = tk.NORMAL if value else tk.DISABLED

        for component in self.return_selector.components:
            if component == self.return_checkbox:
                continue
            component.configure(state=state)


    def toggle_references_selector(self, value=None):
        s = self.column_classes['references'][0].get()
        if s != None:
            state = tk.NORMAL if s else tk.DISABLED

        if value != None:
            state = tk.NORMAL if value else tk.DISABLED

        for component in self.references_selector.components:
            if component == self.references_checkbox:
                continue
            component.configure(state=state)


    def update_tables(self):
        tables = self.parent_obj.parent_obj.table_names
        menu = self.table_selector['menu']
        menu.delete(0, 'end')

        for table in tables:
            menu.add_command(
                label=table,
                command=lambda value=table: (
                    self.column_classes['references'][1].set(value)
                )
            )


    def update_columns(self):
        columns = None
        table_name = self.column_classes['references'][1].get()
        menu = self.column_selector['menu']

        for table in self.parent_obj.parent_obj.tables:
            if table.name == table_name:
                columns = table.column_names + ['rowid']
        if not columns:
            return

        menu.delete(0, 'end')
        for column in columns:
            menu.add_command(
                label=column,
                command = lambda value=column: (
                    self.column_classes['references'][2].set(value)
                )
            )


    @property
    def name(self):
        return snake_case(self.column_name.get())


    @property
    def config(self):
        if self.not_null.get():
            params = f' {self.not_null.get()}'
        else:
            params = ''

        config_dict = {
            'name': self.name,
            'data_type': self.data_type.get(),
            'params': params,
            'column_class_dict': {}
        }

        if self.column_classes['returns'][0].get():
            returns = self.column_classes['returns'][1].get()
            config_dict['column_class_dict']['returns'] = returns
        if self.column_classes['references'][0].get():
            data = self.column_classes['references']
            references = f'{snake_case(data[1].get())}({snake_case(data[2].get())})'
            config_dict['column_class_dict']['references'] = references

        return config_dict



class TableFrame(Frame):
    def build_frame(self):
        self.columns = []
        self.groups = []
        self.filters = []

        # Options frame contains structure relevant data and controls
        self.options_frame = self.child_frame(grid_children=True)
        self.options_frame.add_component(
            'label',
            {'text': 'Table Name: '}
        )
        self.table_name = self.options_frame.add_component('entry')
        self.options_frame.add_component(
            'button',
            {
                'text': 'Remove Table',
                'command': lambda: self.parent_obj.remove_table(self)
            }
        )

        # Matrix for placing column group and filter controls
        self.button_matrix = self.child_frame(
            max_columns=1,
            grid_children=True
        )
        self.button_matrix.add_component(
            'button',
            {'text': 'Add Column', 'command': self.add_column}
        )
        self.button_matrix.add_component(
            'button',
            {'text': 'Clear Columns', 'command': self.clear_columns}
        )
        self.button_matrix.add_component(
            'button',
            {'text': 'Add Group', 'command': self.add_group}
        )
        self.button_matrix.add_component(
            'button',
            {'text': 'Clear Groups', 'command': self.clear_groups}
        )
        self.button_matrix.add_component(
            'button',
            {'text': 'Add Filter', 'command': self.add_filter}
        )
        self.button_matrix.add_component(
            'button',
            {'text': 'Clear Filters', 'command': self.clear_filters}
        )
        self.options_frame.pack()
        self.button_matrix.grid_components()

        
        # Container Frames
        self.columns_frame = self.child_frame()
        self.groups_frame = self.child_frame()
        self.filters_frame = self.child_frame()
        self.columns_frame.pack(),
        self.groups_frame.pack(),
        self.filters_frame.pack()
        self.button_matrix.frame.pack()
        self.update()


    def add_column(self):
        column = ColumnFrame(
            parent_obj=self,
            parent_frame=self.columns_frame.frame
        )
        self.columns.append(column)
        column.pack()
        self.update()


    def add_group(self):
        group = GroupFrame(
            parent_obj=self,
            parent_frame=self.groups_frame.frame
        )
        self.groups.append(group)
        group.pack()
        self.update()


    def add_filter(self):
        filter = FilterFrame(
            parent_obj=self,
            parent_frame=self.filters_frame.frame
        )
        self.filters.append(filter)
        filter.pack()
        self.update()


    def remove_column(self, column):
        for component in column.frame.winfo_children():
            component.destroy()
        self.columns.remove(column)
        column.frame.destroy()
        self.update()


    def remove_group(self, group):
        for component in group.frame.winfo_children():
            component.destroy()
        self.groups.remove(group)
        group.frame.destroy()
        self.update()


    def remove_filter(self, filter):
        for component in filter.frame.winfo_children():
            component.destroy()
        self.filters.remove(filter)
        filter.frame.destroy()
        self.update()


    def clear_columns(self):
        for column in self.columns:
            for component in column.frame.winfo_children():
                component.destroy()
            column.frame.destroy()
        self.columns = []
        self.update()


    def clear_groups(self):
        for group in self.groups:
            for component in group.frame.winfo_children():
                component.destroy()
            group.frame.destroy()
        self.groups = []
        self.update()


    def clear_filters(self):
        for filter in self.filters:
            for component in filter.frame.winfo_children():
                component.destroy()
            filter.frame.destroy()
        self.filters = []
        self.update()


    @property
    def name(self):
        return snake_case(self.table_name.get())

    
    @property
    def column_names(self):
        return [column.name for column in self.columns]


    @property
    def group_names(self):
        return [group.name for group in self.groups]


    @property
    def config(self):
        return {
            'table_name': self.name,
            'dataclass_name': pascal_case(self.name)[:-1],
            'columns': [column.config for column in self.columns],
            'groups': [group.config for group in self.groups],
            'filters': [filter.config for filter in self.filters]
        }


class DbFrame(Frame):
    def build_frame(self):
        self.tables = []

       # Options frame contains structure relevant data and controls
        self.options_frame = self.child_frame(grid_children=True)
        self.options_frame.add_component(
            'label',
            {'text': 'DB Name: '}
        )
        self.db_name = self.options_frame.add_component('entry')
        self.options_frame.add_component(
            'button',
            {'text': 'Add Table', 'command': self.add_table}
        )
        self.options_frame.add_component(
            'button',
            {'text': 'Clear Tables', 'command': self.clear_tables}
        )
        self.options_frame.add_component(
            'button',
            {'text': 'Export DB', 'command': self.export_db}
        )
        self.options_frame.pack_components(fill=tk.X)
        self.options_frame.frame.pack(side=tk.TOP, anchor=tk.NW, fill=tk.X)

        # Tables frame is a container for TableFrame objects
        self.tables_frame = self.child_frame(grid_children=True)
        self.tables_frame.pack()

        self.update()


    def update(self):
        self.parent_frame.update_idletasks()
        self.parent_frame.configure(
                scrollregion=self.parent_frame.bbox('all')
            )


    @property
    def name(self):
        return snake_case(self.db_name.get())


    @property
    def table_names(self):
        return [table.name for table in self.tables]


    def add_table(self):
        table = TableFrame(
            parent_obj=self,
            parent_frame=self.tables_frame.frame
        )
        self.tables.append(table)
        table.frame.grid(row=0, column=self.tables_frame.cur_column, sticky='n')
        self.tables_frame.cur_column += 1


    def remove_table(self, table):
        table.clear_columns()
        for component in table.frame.winfo_children():
            component.destroy()
        table.frame.destroy()
        self.tables.remove(table)
        self.tables_frame.cur_column -= 1
        self.update()


    def clear_tables(self):
        for table in self.tables:
            table.clear_columns()
            for component in table.frame.winfo_children():
                component.destroy()
            table.frame.destroy()
        self.tables = []
        self.update()
            

    def export_db(self):
        config = self.config
        for db_name, tables_list in config.items():
            db = Database(db_name, tables_list)
            fs = generate_filesystem(db)
            save_config(config, fs)
            generate_module(db, fs)

    @property
    def config(self):
        return {self.name: [table.config for table in self.tables]}

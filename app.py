import json
import tkinter as tk
from tkinter import ttk


component_map = {
    'button': tk.Button,
    'check_button': tk.Checkbutton,
    'radio_button': tk.Radiobutton,
    'listbox': tk.Listbox,
    'label': tk.Label,
    'entry': tk.Entry
}
root = tk.Tk()
root.title('TEEDOH\'S SQL ORM GENERATOR')
root.geometry('650x800')

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

scrollbar = ttk.Scrollbar(
    main_frame,
    orient=tk.VERTICAL,
    command=canvas.yview
)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind(
    '<Configure>',
    lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
)

def main():
    frame = DbFrame(parent_frame=canvas)
    canvas.create_window((0,0), window=frame.frame, anchor='nw')

    root.mainloop()


def snake_case(s):
    return s.lower().replace(' ', '_')

def pascal_case(s):
    return s.title().replace(' ', '')


class Frame:
    def __init__(
            self,
            parent_obj=None,
            parent_frame=None,
            max_columns=False,
            max_rows=False
    ):
        self.parent_obj = parent_obj
        self.parent_frame = parent_frame if parent_frame else root

        self.frame = ttk.Frame(self.parent_frame)
        self.components = []

        self.column = 0
        self.max_columns = max_columns
        self.row = 0
        self.max_rows = max_rows

        self.build_frame()


    def add_component(self, tk_type, params={}, parent=None):
        if not tk_type in list(component_map.keys()):
            raise NotImplementedError

        parent = parent if parent else self.frame

        component = component_map[tk_type](parent, **params)
        self.components.append(component)
        return component


    def child_frame(self, **kwargs):
        return Frame(self, self.frame, **kwargs)


    def pack(self):
        for component in self.components:
            component.pack()
        self.frame.pack()


    def grid(self):
        self.partial_grid()
        self.frame.pack()


    def partial_grid(self):
        for component in self.components:
            component.grid(row=self.row, column=self.column)
            self.column += 1

            if self.max_columns:
                if self.column > self.max_columns:
                    self.row += 1
                    self.column = 0


    def build_frame(self):
        pass


    @staticmethod
    def update_canvas():
        canvas.configure(scrollregion=canvas.bbox('all'))


class KeyFrame(Frame):
    def build_frame(self):
        self.data_type = tk.StringVar(value='TEXT')
        self.not_null = tk.StringVar(value='')
        self.key_classes = {
            'returns': [
                tk.BooleanVar(value=False),
                tk.StringVar(value='')
            ],
            'references': [
                tk.BooleanVar(value=False),
                tk.StringVar(value='')
            ]
        }

        # Options frame manages the top level object
        self.options_frame = self.child_frame(max_columns=2)
        self.options_frame.add_component(
            'label',
            {'text': 'Column Name: '}
        )
        self.key_name = self.options_frame.add_component('entry')
        self.key_name.bind(
            '<FocusOut>',
            lambda e: self.parent_obj.update_key_name(self)
        )
        self.options_frame.add_component(
            'button',
            {
                'text': 'Remove Column',
                'command': lambda : self.parent_obj.remove_key(self)
            }
        )

        # Config frame manages the data layer
        self.config_frame = self.child_frame()
        self.config_frame.add_component(
            'check_button',
            {
                'text': 'NOT NULL',
                'variable': self.not_null,
                'onvalue': 'NOT NULL',
                'offvalue': ''
            }
        )        
        self.data_type_selector = self.config_frame.child_frame()
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

        self.key_class_frame = self.config_frame.child_frame(max_columns=2)
        self.key_class_frame.add_component(
            'check_button',
            {
                'text': 'Returns',
                'variable': self.key_classes['returns'][0],
                'onvalue': True,
                'offvalue': False,
                'command': self.toggle_return_selector
            }
        )
        self.return_selector = self.key_class_frame.child_frame()
        for return_type in ['Single', 'Group']:
            self.return_selector.add_component(
                'radio_button',
                {
                    'text': return_type,
                    'variable': self.key_classes['returns'][1],
                    'value': return_type.lower()
                }
            )
        
        # Initialize components
        for component in self.return_selector.components:
            component.configure(state=tk.DISABLED)

        # Pack all the frames
        self.options_frame.grid()
        self.config_frame.pack()
        self.data_type_selector.grid()
        self.key_class_frame.grid()
        self.return_selector.partial_grid()
        self.return_selector.frame.grid(column=1, row=0)
        self.update_canvas()


    def toggle_return_selector(self, value=None):
        if self.key_classes['returns'][0].get():
            for component in self.return_selector.components:
                component.configure(state=tk.NORMAL)
        else:
            for component in self.return_selector.components:
                component.configure(state=tk.DISABLED)


    @property
    def name(self):
        return self.key_name.get()


    @property
    def config(self):
        params = f'{self.not_null.get()}'
        return {
            'name': self.key_name.get(),
            'data_type': self.data_type.get(),
            'params': params,
            'key_class_dict': {
                key: value[1].get()
                for key, value in self.key_classes.items()
                if value[0].get()
            }
        }


class TableFrame(Frame):
    def build_frame(self):
        self.keys = {}

        self.options_frame = self.child_frame()
        self.keys_frame = self.child_frame()

        self.options_frame.add_component(
            'label',
            {'text': 'Table Name: '}
        )
        self.table_name = self.options_frame.add_component('entry')
        self.table_name.bind(
            '<FocusOut>',
            lambda e: self.parent_obj.update_table_name(self)
        )

        self.options_frame.add_component(
            'button',
            {'text': 'Add Column', 'command': self.add_key}
        )
        self.options_frame.add_component(
            'button',
            {'text': 'Clear Columns', 'command': self.clear_keys}
        )
        self.options_frame.add_component(
            'button',
            {
                'text': 'Remove Table',
                'command': lambda : self.parent_obj.remove_table(self)
            }
        )

        self.options_frame.grid()
        self.keys_frame.pack()
        self.update_canvas()


    def add_key(self):
        frame = KeyFrame(
            parent_obj=self,
            parent_frame=self.keys_frame.frame
        )
        self.keys[frame] = frame.name
        frame.pack()


    def update_key_name(self, key):
        self.keys[key] = key.name


    def remove_key(self, key):
        for component in key.frame.winfo_children():
            component.destroy()
        key.frame.destroy()
        del self.keys[key]
        self.update_canvas()
        

    def clear_keys(self):
        for key in self.keys:
            for component in key.frame.winfo_children():
                component.destroy()
            key.frame.destroy()
        self.keys = {}


    def update_table_names(self, names):
        pass


    @property
    def name(self):
        return self.table_name.get()


    @property
    def config(self):
        return {
            'table_name': snake_case(self.name),
            'dataclass_name': pascal_case(self.name)[:-1],
            'keys': [key.config for key in self.keys],
            'groups': [],
            'filters': []
        }


class DbFrame(Frame):
    def build_frame(self):
        self.tables = {}

        self.options_frame = self.child_frame()
        self.tables_frame = self.child_frame()

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
            {'text': 'Export DB' ,'command': self.export_db}
        )

        self.options_frame.grid()
        self.tables_frame.pack()
        self.update_canvas()


    def add_table(self):
        frame = TableFrame(
            parent_obj=self,
            parent_frame=self.tables_frame.frame
        )
        self.tables[frame] = ''
        frame.pack()


    def update_table_name(self, table):
        self.tables[table] = table.name
        tables = self.tables.values()
        
        for t in self.tables:
            other_tables = [
                table for table in tables
                if table != t.name
            ]
            t.update_table_names(other_tables)

    
    def remove_table(self, table):
        for component in table.frame.winfo_children():
            component.destroy()
        table.frame.destroy()
        del self.tables[table]
        self.update_canvas()


    def clear_tables(self):
        for table in self.tables:
            for component in table.frame.winfo_children():
                component.destroy()
            table.frame.destroy()
        self.tables = {}


    def export_db(self):
        db = {self.db_name.get(): [table.config for table in self.tables]}
        db = json.dumps(db)
        print(db)


if __name__ == '__main__':
    main()

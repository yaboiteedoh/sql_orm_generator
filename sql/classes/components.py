import tkinter as tk
from tkinter import ttk


COMPONENTS = {}
FILL = {
    'x': {
        'fill': tk.X,
        'sticky': tk.EW
    },
    'y': {
        'fill': tk.Y,
        'sticky': tk.NS
    },
    'both': {
        'fill': tk.BOTH,
        'sticky': tk.NSEW
    },
    'neither': {
        'fill': None,
        'sticky': None
    }
}


class Component:
    def __init__(
        self,
        parent,
        parent_frame=None,
        fill='both'
    ):
        self.parent = parent
        self.parent_frame = parent_frame if parent_frame else parent.tkinter
        self.tkinter = None
        self.vars = []
        if not isinstance(fill, dict):
            self.fill = FILL[fill]
        else:
            self.fill = fill


    def add_var(self, data_type, default=None):
        match data_type:
            case 'str':
                var = tk.StringVar()
            case 'int':
                var = tk.IntVar()
            case 'bool':
                var = tk.BooleanVar()
            case 'float':
                var = tk.DoubleVar()
            case _: 
                raise ValueError(f'Component received invalid datatype in var creation {data_type}')

        if default is not None:
            var.set(default)

        self.vars.append(var)
        return var


    def toggle_active(self, value=None):
        state=value
        if value is not None:
            state = tk.NORMAL if value else tk.DISABLED
        self.tkinter.configure(state=state)


    def update(self):
        self.parent.update()


    def pack(self, grid=None):
        parent=self.parent
        print(f'{self}, {parent=} {grid=}')
        if grid:
            self.tkinter.grid(
                row=grid['row'],
                column=grid['column'],
                sticky=self.fill['sticky']
            )
        else:
            self.tkinter.pack(fill=self.fill['fill'])


    def destroy(self):
        self.vars = []
        self.tkinter.destroy()


class Frame(Component):
    def __init__(
        self,
        parent,
        fill_children='both',
        grid_children=False,
        max_columns=None,
        update_func=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            parent_frame,
            fill
        )

        self.max_columns = max_columns
        self.grid_children = grid_children
        self.fill_children = FILL[fill_children]

        self.tkinter = ttk.Frame(self.parent_frame)
        self.components = []
        self.update_func = update_func
        self.cur_column = 0
        self.cur_row = 0


    def add_component(
            self,
            type,
            parent=None,
            **kwargs
    ):
        if not type in COMPONENTS:
            raise NotImplementedError

        parent = parent if parent else self
        component = COMPONENTS[type](parent=parent, fill=self.fill_children, **kwargs)
        self.components.append(component)
        return component


    def update(self):
        if not self.update_func:
            super().update()
        else:
            self.update_func()

    
    def countdown_cur_column():
        self.cur_column -= 1


    def toggle_active(self, value=None):
        if value is not None:
            state = tk.NORMAL if value else tk.DISABLED
        for component in self.components:
            if component.tkinter.winfo_class() in STATE_COMPONENTS:
                component.toggle_active(value=state)


    def pack(self, just_children=False, grid=None):
        if self.grid_children:
            for component in self.components:
                component.pack(
                    grid={
                        'row': self.cur_row,
                        'column': self.cur_column
                    }
                )
                self.cur_column += 1
                if self.max_columns is not None:
                    if self.cur_column > self.max_columns:
                        self.cur_row += 1
                        self.cur_column = 0
        else:
            for component in self.components:
                component.pack()

        if not just_children:
            super().pack(grid=grid)


    def destroy(self):
        for component in self.components:
            component.destroy()
        super().destroy()


class Button(Component):
    def __init__(
        self,
        parent,
        text,
        command,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            parent_frame,
            fill
        )

        self.tkinter = tk.Button(
            self.parent_frame,
            text=text,
            command=command
        )


    @property
    def text(self):
        return self.tkinter.cget('text')


    @text.setter
    def text(self, text):
        self.tkinter.configure(text=text)


    def set_command(self, command):
        self.tkinter.configure(command=command)


class Label(Component):
    def __init__(
        self,
        parent,
        text,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            parent_frame,
            fill
        )

        self.tkinter = tk.Label(
            self.parent_frame,
            text=text
        )

    
    @property
    def text(self):
        return self.tkinter.cget('text')


    @text.setter
    def text(self, text):
        self.tkinter.config(text=text)


class Entry(Component):
    def __init__(
        self,
        parent,
        default=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            parent_frame,
            fill
        )

        self.tkinter = ttk.Entry(
            self.parent_frame
        )
        
        if default:
            self.value = default

        else:
            self.value = ''


    @property
    def value(self):
        return self.tkinter.get()


    @value.setter
    def value(self, text):
        self.tkinter.delete(0, tk.END)
        self.tkinter.insert(0, text)


class CheckButton(Component):
    def __init__(
        self,
        parent,
        text,
        data_type='bool',
        default=False,
        values=[False, True],
        command=None,
        custom_trace=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            parent_frame,
            fill
        )

        self._active = self.add_var('bool')
        self._value = self.add_var(data_type)

        self.tkinter = tk.Checkbutton(
            self.parent_frame,
            text=text,
            variable=self._active,
            command=command
        )

        trace = custom_trace if custom_trace else self._default_trace
        self._active.trace_add(
            'write',
            lambda name, index, mode: self._value_trace()
        )
        self._value.trace_add(
            'write',
            lambda name, index, mode: trace()
        )

        self._off_value, self._on_value = values
        self._active.set(default)


    @property
    def active(self):
        return self._active.get()


    @active.setter
    def active(self, value):
        self._active.set(value)


    @property
    def value(self):
        return self._value.get()


    def add_trace(self, trace_func):
        self._value.trace_add(
            'write',
            lambda name, index, mode: trace_func()
        )


    def _value_trace(self):
        self.update()
        if self._active.get():
            if self._value.get() == self._off_value:
                self._value.set(self._on_value)
        else:
            if self._value.get() == self._on_value:
                self._value.set(self._off_value)
        

    def _default_trace(self):
        self.update()
        match self._value.get():
            case self._on_value:
                self._active.set(True)
            case self._off_value:
                self._active.set(False)


class RadioButton(Component):
    def __init__(
        self,
        parent,
        text,
        data_type='str',
        value=None,
        variable=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            parent_frame,
            fill
        )

        if not variable:
            if data_type in ['str', 'int', 'float']:
                self._value = self.add_var(data_type)
            else:
                raise ValueError(f'Radiobutton received invalid datatype in constructor: {data_type}')
        else:
            self._value = variable

        if not value:
            self._value = self.add_var('str')
            self._selection = text
        else:
            self._selection = value
        
        self.tkinter = tk.Radiobutton(
            self.parent_frame,
            text=text,
            variable=self._value,
            value=self._selection
        )

    @property
    def text(self):
        return self.tkinter.cget('text')

    
    @text.setter
    def text(self, text):
        self.tkinter.configure(text=text)


    def set_value(self, value):
        self.tkinter.configure(value=value)
                

class OptionMenu(Component):
    def __init__(
        self,
        parent,
        options,
        default='',
        variable=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            parent_frame,
            fill
        )

        if variable:
            self._value = variable
        else:
            self._value = self.add_var('str')

        self.tkinter = tk.OptionMenu(
            self.parent_frame,
            variable=self._value,
            value=default
        )
        self.options = options


    @property
    def options(self):
        menu = self.tkinter['menu']
        if menu_end := menu.index('end') is not None:
            items = [
                menu.entrycget(i, 'label')
                for i in range(menu_end + 1)
            ]
            return items
        else:
            return None


    @options.setter
    def options(self, options):
        menu = self.tkinter['menu']
        menu.delete(0, tk.END)

        for option in options:
            menu.add_command(
                label=option,
                command=lambda value=option: setattr(self, 'value', value)
            )


    @property
    def value(self):
        return self._value.get()


    @value.setter
    def value(self, value):
        self._value.set(value)


class RadioMenu(Frame):
    def __init__(
        self,
        parent,
        options=[],
        data_type='str',
        default=None,
        fill_children='both',
        grid_children=True,
        max_columns=0,
        update_func=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            fill_children,
            grid_children,
            max_columns,
            update_func,
            parent_frame,
            fill
        )

        self.data_type = data_type
        if isinstance(options, list):
            self.data_type = 'str'

        if data_type in ['str', 'int', 'float']:
            self._value = self.add_var(data_type)
        else:
            raise ValueError(f'RadioMenu received invalid datatype in constructor: {data_type}')

        if isinstance(options, list):
            for text in options:
                self.add_component(
                    'radio_button',
                    text=text,
                    variable=self._value,
                    value=text
                )
        else:
            for text, value in options.items():
                self.add_component(
                    'radio_button',
                    text=text,
                    data_type=self.data_type,
                    value=value
                )

        if default:
            self.value = default


    @property
    def value(self):
        return self._value.get()


    @value.setter
    def value(self, value):
        self._value.set(value)


class LabeledOption(Frame):
    def __init__(
        self,
        parent,
        text,
        options,
        default='',
        variable=None,
        fill_children='both',
        grid_children=True,
        max_columns=1,
        update_func=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            fill_children,
            grid_children,
            max_columns,
            update_func,
            parent_frame,
            fill
        )
        if variable:
            self._value = variable
        else:
            self._value = self.add_var('str')

        self.label = self.add_component(
            'label',
            text=text
        )
        self.menu = self.add_component(
            'option_menu',
            variable=self._value,
            options=options,
            default=default
        )
        

    @property
    def value(self):
        return self._value.get()


    @value.setter
    def value(self, value):
        self._value.set(value)


    @property
    def options(self):
        return self.menu.options


    @options.setter
    def options(self, options):
        self.menu.options = options


class LabeledEntry(Frame):
    def __init__(
        self,
        parent,
        text,
        default=None,
        fill_children='both',
        grid_children=True,
        max_columns=1,
        update_func=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            fill_children,
            grid_children,
            max_columns,
            update_func,
            parent_frame,
            fill
        )
        
        self.label = self.add_component(
            'label',
            text=text
        )
        self.entry = self.add_component(
            'entry',
            default=default
        )


    @property
    def value(self):
        return self.entry.tkinter.get()


    @value.setter
    def value(self, value):
        self.entry.tkinter.delete(0, tk.END)
        self.entry.tkinter.insert(0, value)


class ButtonMatrix(Frame):
    def __init__(
        self,
        parent,
        buttons=[],
        fill_children='both',
        grid_children=True,
        max_columns=None,
        update_func=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent,
            fill_children,
            grid_children,
            max_columns,
            update_func,
            parent_frame,
            fill
        )

        if isinstance(buttons, list):
            for text in buttons:
                self.add_component(
                    'button',
                    text=text,
                    command=self._pass
                )
        else:
            for text, command in buttons.items():
                self.add_component(
                    'button',
                    text=text,
                    command=command
                )


    @staticmethod
    def _pass():
        pass


class DynamicComponentFrame(Frame):
    def __init__(
        self,
        parent,
        child_class,
        default_blueprints={},
        fill_children='both',
        grid_children=True,
        max_columns=None,
        update_func=None,
        parent_frame=None,
        fill='both'
    ):
        super().__init__(
            parent=parent,
            fill_children=fill_children,
            grid_children=grid_children,
            max_columns=max_columns,
            update_func=update_func,
            parent_frame=parent_frame,
            fill=fill
        )

        self.children = []
        self.child_class = child_class
        self.default_blueprints = default_blueprints


    def add(self, blueprints=None):
        if not blueprints:
            child = self.child_class(self, **self.default_blueprints)
        else:
            child = self.child_class(self, **blueprints)
        self.children.append(child)

        grid={
            'row': self.cur_row,
            'column': self.cur_column
        }
        child.pack(grid=grid)
        self.cur_column += 1
        if self.max_columns is not None:
            if self.cur_column > self.max_columns:
                self.cur_row += 1
                self.cur_column = 0

        return child


    def remove(self, child):
        self.children.remove(child)
        child.destroy()
        self.cur_column -= 1
        if self.cur_column < 0:
            self.cur_column = self.max_columns
            self.cur_row -= 1
        self.update()


    def clear(self):
        for child in self.children:
            child.destroy()
            self.cur_column -= 1
            if self.cur_column < 0:
                self.cur_column = self.max_columns
                self.cur_row -= 1
        self.children = []
        self.update()


    def destroy(self):
        self.clear()
        super().destroy()


COMPONENTS = {
    'button': Button,
    'check_button': CheckButton,
    'radio_button': RadioButton,
    'option_menu': OptionMenu,
    'label': Label,
    'entry': Entry,
    'frame': Frame,
    'radio_menu': RadioMenu,
    'labeled_entry': LabeledEntry,
    'button_matrix': ButtonMatrix,
    'dynamic_component_frame': DynamicComponentFrame,
    'labeled_option': LabeledOption
}

STATE_COMPONENTS = [
    'Button',
    'Checkbutton',
    'Menubutton'
]

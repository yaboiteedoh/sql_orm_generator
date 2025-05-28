import tkinter as tk
from tkinter import ttk

from .widgets import DbFrame


def configure_scrollbar():
    container = tk.Frame(TK)
    container.pack(fill=tk.BOTH, expand=1)
    
    canvas = tk.Canvas(container)

    y_scrollbar = ttk.Scrollbar(
        container,
        orient=tk.VERTICAL,
        command=canvas.yview
    )
    x_scrollbar = ttk.Scrollbar(
        container,
        orient=tk.HORIZONTAL,
        command=canvas.xview
    )
    y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    canvas.configure(yscrollcommand=y_scrollbar.set)
    canvas.configure(xscrollcommand=x_scrollbar.set)
    canvas.bind(
        '<Configure>',
        lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
    )

    return canvas


TK = tk.Tk()
TK.title('TEEDOH\'S SQL ORM GENERATOR')
TK.geometry('590x800')
CANVAS = configure_scrollbar()
_frame = DbFrame(parent='root', parent_frame=CANVAS)
_frame.pack()
CANVAS.create_window((0,0), window=_frame.tkinter, anchor='nw')


import tkinter as tk
from tkinter import ttk

from .widgets import DbFrame


def configure_scrollbar():
    container = tk.Frame(TK)
    container.pack(fill=tk.BOTH, expand=1)
    
    canvas = tk.Canvas(container)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    scrollbar = ttk.Scrollbar(
        container,
        orient=tk.VERTICAL,
        command=canvas.yview
    )
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        '<Configure>',
        lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
    )

    return canvas

TK = tk.Tk()
TK.title('TEEDOH\'S SQL ORM GENERATOR')
TK.geometry('590x800')
CANVAS = configure_scrollbar()
_frame = DbFrame(parent_frame=CANVAS)
CANVAS.create_window((0,0), window=_frame.frame, anchor='nw')


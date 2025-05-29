from teedoh_kinter import Tk

from .widgets import DbFrame

TK = Tk(
    title='TEEDOH\'S SQL ORM GENERATOR',
    geometry='590x800'
)
TK.add_component(
    DbFrame
)
TK.pack()

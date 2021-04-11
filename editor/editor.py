#!/usr/bin/env python
import json
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Notebook

from enums.item_type import ItemType
from tk_utils import center
from easy import EasyJSONField, EasyItem, EasyJSONKey, EasyJSONEnum, EasyGridTree, EasyValidation,\
    EasyJSONStatsWeights, EasyJSONBattleStats


# TODO Add consolidate
class JSONEditor(Frame):
    def __init__(self, master, editor_grid: EasyGridTree, sample_create: dict, read_from: str):
        super().__init__(master)
        self.read_path = read_from
        with open(self.read_path, 'r') as f:
            self.data = json.load(f)
        self.editor_grid: EasyGridTree = editor_grid
        self.editor_grid.sample_create = sample_create
        self.tree = None
        self.save_button = None
        self.add_button = None
        self.remove_button = None
        self.create_widgets()
        self.pack(fill=BOTH, expand=True)

    def on_save_pre(self, _):
        self.after(0, self.on_save)

    def on_add_pre(self, _):
        self.after(0, self.on_add)

    def on_remove_pre(self, _):
        self.after(0, self.on_remove)

    def on_add(self):
        self.editor_grid.on_add()

    def on_remove(self):
        self.editor_grid.on_remove()

    def on_save(self):
        if self.editor_grid.modified_data:
            if messagebox.askyesno('Save All', f"You are going to save modifications to "
                                   f"{', '.join([x['Name'] for x in self.editor_grid.modified_data.values()])}."
                                               f" Save all?"):
                self.data.update(self.editor_grid.modified_data)
                trk = set()
                for k in self.data.keys():
                    if self.data[k].get('INTERNAL_DELETED') is not None:
                        trk.add(k)
                for k in trk:
                    del self.data[k]
                with open(self.read_path, 'w') as f:
                    json.dump(self.data, f, indent=2)
                self.editor_grid.update(self.data)
                self.editor_grid.modified_data.clear()
                messagebox.showinfo('Save All', "Saved successfully!")
        else:
            messagebox.showinfo("Save All", "There are no modifcations!")
        return True

    def create_widgets(self):
        self.editor_grid.build(self)
        self.editor_grid.update(self.data)
        self.editor_grid.grid(0, 0)

        scroll = Scrollbar(self, orient="vertical", command=self.editor_grid.treeview.yview)
        scroll.grid(row=0, column=1, sticky='news')

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        save_frame = Frame(self)

        self.add_button = Button(save_frame, text="(+) Create")
        self.add_button.bind("<Button-1>", self.on_add_pre)
        self.add_button.pack(side=LEFT, padx=5)

        self.remove_button = Button(save_frame, text="(-) Delete")
        self.remove_button.bind("<Button-1>", self.on_remove_pre)
        self.remove_button.pack(side=LEFT, padx=5)

        self.save_button = Button(save_frame, text="Save All")
        self.save_button.bind("<Button-1>", self.on_save_pre)
        self.save_button.pack(side=LEFT, padx=5)

        save_frame.grid(row=1, column=0, columnspan=2, pady=(20, 20))


class Items(JSONEditor):
    def __init__(self, master=None):
        super().__init__(master,
                         EasyGridTree([
                             EasyItem('Id', EasyJSONKey(), 0, 0),
                             EasyItem('Name', EasyJSONField('Name', 'Name', EasyValidation.not_empty), 0, 0),
                             EasyItem('Type', EasyJSONEnum('Type', 'Type', ItemType), 1, 0),
                             EasyItem('Stats', EasyJSONStatsWeights('Stats'), 0, 1, rowspan=2),
                         ], [64, 128, 128]),
                         {
                             'Name': 'Item',
                             'Type': ItemType.BOOT.get_name(),
                             'Stats': {}
                         },
                         read_from='../game_data/items.json')


class Enemies(JSONEditor):
    def __init__(self, master=None):
        super().__init__(master,
                         EasyGridTree([
                             EasyItem('Id', EasyJSONKey(), 0, 0),
                             EasyItem('Name', EasyJSONField('Name', 'Name', EasyValidation.not_empty), 0, 0),
                             EasyItem('Stats', EasyJSONBattleStats('Stats'), 0, 1, rowspan=2),
                         ], [64, 128]),
                         {
                             'Name': 'Enemy',
                             'Stats': {}
                         },
                         read_from='../game_data/enemies.json')


class Editor(Tk):
    def __init__(self):
        super().__init__()

        self.title('Tim Bot Editor')
        self.minsize(960, 480)
        self.create_widgets()

    def create_widgets(self):
        tabs = Notebook(self)
        tabs.add(Items(tabs), text='Items')
        tabs.add(Enemies(tabs), text='Enemies')
        tabs.pack(fill=BOTH, expand=True, padx=4, pady=4)


app = Editor()
center(app, app)
app.mainloop()

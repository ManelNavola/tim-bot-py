#!/usr/bin/env python
import json
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Notebook
from typing import Any

from enums.item_type import EquipmentType, ItemType
from enums.location import Location
from item_data.stat import Stat
from tk_utils import center
from easy import EasyJSONField, EasyItem, EasyJSONKey, EasyJSONEnum, EasyGridTree, EasyValidation, \
    EasyJSONStatsWeights, EasyJSONBattleStats


class JSONEditor(Frame):
    def __init__(self, master, editor_grid: EasyGridTree, sample_create: dict, read_from: str,
                 filter_by: list[tuple[str, Any]] = None):
        super().__init__(master)
        if filter_by is None:
            filter_by = []
        self.read_path = read_from
        with open(self.read_path, 'r') as f:
            self.data = {}
            for k, v in json.load(f).items():
                fg: bool = True
                for fb in filter_by:
                    if v.get(fb[0], None) != fb[1]:
                        fg = False
                        break
                if fg:
                    self.data[k] = v
        self.editor_grid: EasyGridTree = editor_grid
        self.editor_grid.sample_create = sample_create
        self.tree = None
        self.save_button = None
        self.add_button = None
        self.remove_button = None
        self.consolidate_button = None
        self.create_widgets()
        self.pack(fill=BOTH, expand=True)

    def on_save_pre(self, _):
        self.after(0, self.on_save)

    def on_add_pre(self, _):
        self.after(0, self.on_add)

    def on_remove_pre(self, _):
        self.after(0, self.on_remove)

    def on_consolidate_pre(self, _):
        self.after(0, self.on_consolidate)

    def on_add(self):
        self.editor_grid.on_add()

    def on_remove(self):
        self.editor_grid.on_remove()

    def on_consolidate(self):
        if messagebox.askyesno('Consolidate', "Are you sure you want to consolidate the WHOLE JSON? "
                                              "This action cannot be undone!"):
            # Save all
            self.data.update(self.editor_grid.modified_data)
            trk = set()
            for k in self.data.keys():
                if self.data[k].get('INTERNAL_DELETED') is not None:
                    trk.add(k)
            for k in trk:
                del self.data[k]

            last_index = -1
            keys_to_consolidate = []
            for k in self.data.keys():
                if k.startswith('X'):
                    keys_to_consolidate.append(k)
                else:
                    last_index = max(last_index, int(k))
            last_index += 1

            for k in keys_to_consolidate:
                self.data[str(last_index)] = self.data.pop(k)
                last_index += 1

            with open(self.read_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            self.editor_grid.update(self.data)
            self.editor_grid.modified_data.clear()

            messagebox.showinfo('Consolidate', "The JSON has been consolidated.")

    def on_save(self):
        if self.editor_grid.modified_data:
            if messagebox.askyesno('Save All',
                                   f"You are going to save modifications to "
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
            messagebox.showinfo("Save All", "There are no modifications!")
        return True

    def create_widgets(self):
        self.editor_grid.build(self)
        self.editor_grid.update(self.data)
        self.editor_grid.grid(0, 0)

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
        self.remove_button.pack(side=LEFT, padx=(5, 20))

        self.save_button = Button(save_frame, text="Save All")
        self.save_button.bind("<Button-1>", self.on_save_pre)
        self.save_button.pack(side=LEFT, padx=20)

        self.consolidate_button = Button(save_frame, text="Consolidate (!)")
        self.consolidate_button.bind("<Button-1>", self.on_consolidate_pre)
        self.consolidate_button.pack(side=LEFT, padx=(20, 5))

        save_frame.grid(row=1, column=0, columnspan=2, pady=(20, 20))


class Equipment(JSONEditor):
    def __init__(self, master=None):
        super().__init__(master,
                         EasyGridTree([
                             EasyItem('Id', EasyJSONKey(), 0, 0, field_width=4),
                             EasyItem('Name', EasyJSONField('Name', 'Name', EasyValidation.not_empty), 0, 0,
                                      field_width=20),
                             EasyItem('Location', EasyJSONEnum('Location', 'Location', Location), 1, 0),
                             EasyItem('Tier', EasyJSONField('Tier', 'Tier', EasyValidation.positive, width=5),
                                      2, 0,
                                      field_width=5),
                             EasyItem('Subtype', EasyJSONEnum('Subtype', 'Subtype', EquipmentType), 3, 0),
                             EasyItem('Stats', EasyJSONStatsWeights('Stats'), 0, 1, row_span=4),
                         ], [64, 128, 128, 32, 128]),
                         {
                             'Name': 'Item',
                             'Location': Location.NOWHERE.get_id(),
                             'Tier': 0,
                             'Type': ItemType.EQUIPMENT.get_id(),
                             'Subtype': EquipmentType.BOOT.get_id(),
                             'Stats': {}
                         },
                         read_from='../game_data/items.json',
                         filter_by=[('Type', 0)])


class Enemies(JSONEditor):
    def __init__(self, master=None):
        super().__init__(master,
                         EasyGridTree([
                             EasyItem('Id', EasyJSONKey(), 0, 0, field_width=4),
                             EasyItem('Name', EasyJSONField('Name', 'Name', EasyValidation.not_empty), 0, 0,
                                      field_width=20),
                             EasyItem('Location', EasyJSONEnum('Location', 'Location', Location), 1, 0),
                             EasyItem('Pool', EasyJSONField('Pool', 'Pool', width=8), 2, 0),
                             EasyItem('Stats', EasyJSONBattleStats('Stats'), 0, 1, row_span=3),
                         ], [64, 128, 128, 64]),
                         {
                             'Name': 'Enemy',
                             'Location': Location.NOWHERE.get_id(),
                             'Stats': {
                                 Stat.HP.get_abv(): 4,
                                 Stat.STR.get_abv(): 4,
                                 Stat.DEF.get_abv(): 2
                             }
                         },
                         read_from='../game_data/enemies.json')


class Editor(Tk):
    def __init__(self):
        super().__init__()

        self.title('Tim Bot Editor')
        self.minsize(960, 480)
        self.create_widgets()

        def try_close():
            if messagebox.askyesno("Quit", "Are you sure you want to exit?"):
                self.destroy()

        self.protocol("WM_DELETE_WINDOW", try_close)

    def create_widgets(self):
        tabs = Notebook(self)
        tabs.add(Equipment(tabs), text='Equipment')
        tabs.add(Enemies(tabs), text='Enemies')
        tabs.pack(fill=BOTH, expand=True, padx=4, pady=4)


app = Editor()
center(app, app)
app.mainloop()

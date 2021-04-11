import copy
import random
from abc import ABC, abstractmethod
from tkinter import messagebox
from tkinter.ttk import Treeview
from typing import Any, cast
from tkinter import *

from jsonpath_ng import parse

from adventures.battle_data.battle_entity import BattleEntity
from entities.bot_entity import BotEntity
from tk_utils import center
from item_data.stats import Stats


class EasyData:
    def __init__(self, data, on_edit=None):
        self.data = data
        self.on_edit = on_edit

    def update(self):
        if self.on_edit:
            self.on_edit()


class Easy(ABC):
    def __init__(self):
        self.frame = None
        self.easy_data = None

    @abstractmethod
    def build(self, parent):
        pass

    def update(self, easy_data):
        self.easy_data = easy_data

    def grid(self, row, column, sticky='nsew', columnspan=1, rowspan=1):
        self.frame.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan, sticky=sticky)


class EasyItem:
    def __init__(self, name: str, easy: Easy, row: int, column: int, sticky: str = 'nsew',
                 columnspan: int = 1, rowspan: int = 1):
        self.name = name
        self.easy = easy
        self.row = row
        self.column = column
        self.sticky = sticky
        self.rowspan = rowspan
        self.columnspan = columnspan


class EasyJSON(Easy, ABC):
    def __init__(self, path: str):
        super().__init__()
        self.path = parse(path)
        self.is_editable = True

    def get_value(self, data=None):
        if not data:
            data = self.easy_data.data
        match = self.path.find(data)
        if match:
            return match[0].value
        return ''

    def set_value(self, value):
        to_explore = str(self.path).split('.')
        current = self.easy_data.data
        while len(to_explore) > 1:
            current = current[to_explore[0]]
            del to_explore[0]
        if value:
            if type(value) == str:
                value = value.strip()
            current[to_explore[0]] = value
        elif to_explore[0] in current:
            del current[to_explore[0]]
        self.easy_data.update()

    def show(self, data: dict[str, Any], key) -> str:
        return self.get_value(data)


class EasyJSONKey(EasyJSON):
    def __init__(self):
        super().__init__('EasyJSONKey')
        self.is_editable = False

    def build(self, parent):
        pass

    def show(self, data: dict[str, Any], key) -> str:
        return key


class EasyValidation:
    @staticmethod
    def not_empty(new_value: str):
        if new_value:
            return True, new_value
        return False, None

    @staticmethod
    def empty_or_positive(new_value: str):
        try:
            if new_value:
                if int(new_value) > 0:
                    return True, int(new_value)
                elif int(new_value) == 0:
                    return True, None
            else:
                return True, None
        except ValueError:
            return False, None
        return False, None


class EasyJSONWithVar(EasyJSON):
    def __init__(self, path: str):
        super().__init__(path)
        self.path = parse(path)
        self.var = None

    def build(self, parent):
        self.var = StringVar()

    def update(self, data):
        super().update(data)
        self.var.set(self.get_value())


class EasyJSONWithValidation(EasyJSONWithVar):
    def __init__(self, path: str, validation):
        super().__init__(path)
        self.path = parse(path)
        self.validation = validation
        self.validation_command = None
        self.var = None
        self.last_valid_text = None
        self.inp = None

    def update(self, data):
        super().update(data)
        self.last_valid_text = self.var.get()

    def execute_validation(self, action, new_text):
        if action.startswith('focus'):
            success, result = self.validation(new_text)
            if success:
                # self.var.set(new_text)
                self.last_valid_text = new_text
                self.set_value(result)
                return True
            else:
                _, result = self.validation(self.last_valid_text)
                self.var.set(self.last_valid_text)
                self.register_validation()
                self.set_value(result)
                return True
        else:
            success, result = self.validation(new_text)
            if success:
                # self.var.set(new_text)
                self.last_valid_text = new_text
                self.set_value(result)
                return True
            else:
                self.set_value(new_text)
                return True

    def register_validation(self, inp=None):
        if inp is not None:
            self.inp = inp
            self.validation_command = self.frame.register(self.execute_validation)
        self.inp.configure(validate='all', validatecommand=(self.validation_command, '%V', '%P'))
        return self.validation_command


class EasyJSONField(EasyJSONWithValidation):
    def __init__(self, name: str, path: str, validation=None, width: int = 20):
        super().__init__(path, validation)
        self.name = name
        self.width = width

    def build(self, parent):
        super().build(parent)
        self.frame = Frame(parent)

        label = Label(self.frame, text=self.name, justify='center')
        label.pack(anchor=CENTER, padx=10, pady=(5, 5))

        if self.validation:
            inp = Entry(self.frame, textvariable=self.var, validate='all', justify='center')
            inp.configure(validatecommand=(self.register_validation(inp), '%V', '%P'))
        else:
            inp = Entry(self.frame, textvariable=self.var, justify='center')
        inp.configure(width=self.width)
        inp.pack(padx=10, pady=(5, 5))


class EasyJSONEnum(EasyJSONWithVar):
    def __init__(self, name: str, path: str, my_enum):
        super().__init__(path)
        self.name = name
        self.enum = my_enum

    def save(self, _):
        self.set_value(self.var.get())

    def build(self, parent):
        super().build(parent)
        self.frame = Frame(parent)

        label = Label(self.frame, text=self.name)
        label.pack(anchor=CENTER, padx=10, pady=(10, 5))

        inp = OptionMenu(self.frame, self.var, *[x.get_name() for x in self.enum.get_all()], command=self.save)
        inp.configure(width=12)
        inp.pack(padx=10, pady=(0, 5))


class EasyGrid(Easy):
    def __init__(self, structure, weights=None):
        Easy.__init__(self)
        if weights is None:
            weights = []
        self.structure: list[EasyItem] = structure
        self.weights: list[int] = weights

    def build(self, parent):
        self.frame = Frame(parent)

        for ei in self.structure:
            ei.easy.build(self.frame)

    def update(self, data):
        for ei in self.structure:
            ei.easy.update(data)

    def grid(self, row, column, sticky='nsew', columnspan=1, rowspan=1):
        Easy.grid(self, row, column, sticky, columnspan, rowspan)
        for i in range(len(self.weights)):
            self.frame.grid_columnconfigure(i, weight=self.weights[i])
        for ei in self.structure:
            if isinstance(ei.easy, EasyJSON):
                ej = cast(EasyJSON, ei.easy)
                if ej.is_editable:
                    ej.grid(ei.row, ei.column, ei.sticky, ei.columnspan, ei.rowspan)


class EasyJSONStats(EasyGrid, EasyJSON):
    def __init__(self, path):
        x = 0
        y = 0
        limit = 4
        structure = []
        for stat in Stats.get_all():
            structure.append(EasyItem(stat.abv,
                                      EasyJSONField(stat.abv, path + '.' + stat.abv, EasyValidation.empty_or_positive,
                                                    width=5),
                                      y, x))
            x += 1
            if x == limit:
                x = 0
                y += 1
        EasyGrid.__init__(self, structure, [1 for _ in range(limit)])
        EasyJSON.__init__(self, path)
        self.stat_fields: list[EasyItem] = []

    def build(self, parent):
        EasyGrid.build(self, parent)

    def update(self, data):
        EasyGrid.update(self, data)

    def grid(self, row, column, sticky='nsew', columnspan=1, rowspan=1):
        EasyGrid.grid(self, row, column, sticky, columnspan, rowspan)

    def show(self, data: dict[str, Any], key) -> str:
        tr = []
        for stat in Stats.get_all():
            value = EasyJSON.get_value(self, data).get(stat.abv, 0)
            if value:
                tr.append(f"{stat.abv}: {value}")
        return ', '.join(tr)


class EasyJSONStatsWeights(EasyJSONStats):
    def show(self, data: dict[str, Any], key) -> str:
        tr = []
        for stat in Stats.get_all():
            value = EasyJSON.get_value(self, data).get(stat.abv, 0)
            if value:
                if value == 1:
                    tr.append((f"{stat.abv}", value))
                else:
                    tr.append((f"{stat.abv} x{value}", value))
        tr.sort(key=lambda x: -x[1])
        return ', '.join([x[0] for x in tr])


class EasyJSONBattleStats(EasyJSONStats):
    def show(self, data: dict[str, Any], key) -> str:
        stat_data = {Stats.get_by_abv(x): v for x, v in data['Stats'].items()}
        return BattleEntity(BotEntity('', stat_data)).print()


class EasyGridTree(EasyGrid):
    def __init__(self, structure, widths: list[int]):
        EasyGrid.__init__(self, structure)
        self.data = None
        self.modified_data = {}
        self.current_id = None
        self.original_row = None
        self.modified_row = None
        self.window = None
        self.eg = None
        self.eg_save_button = None
        self.eg_reset_button = None
        self.treeview = None
        self.widths = widths
        self.sample_create = None
        self.creating = False

    def is_modified(self):
        return not (self.original_row == self.modified_row)

    def modified(self):
        if self.creating:
            self.eg_save_button['state'] = "normal"
        else:
            if self.is_modified():
                self.eg_save_button['state'] = "normal"
            else:
                self.eg_save_button['state'] = "disable"

        if self.creating:
            if self.original_row == self.modified_row:
                self.eg_reset_button['state'] = "disabled"
            else:
                self.eg_reset_button['state'] = "normal"
        else:
            if self.data.get(self.current_id):
                if self.data[self.current_id] == self.modified_row:
                    self.eg_reset_button['state'] = "disabled"
                else:
                    self.eg_reset_button['state'] = "normal"
            else:
                if self.modified_data[self.current_id] == self.modified_row:
                    self.eg_reset_button['state'] = "disabled"
                else:
                    self.eg_reset_button['state'] = "normal"

    def on_add(self):
        self.creating = True
        self.eg_save_button['text'] = 'Create'

        self.current_id = 'X\n\n' + str(random.random())
        self.original_row = copy.deepcopy(self.sample_create)
        self.modified_row = copy.deepcopy(self.sample_create)
        self.eg_reset_button['state'] = "disabled"

        self.eg_save_button['state'] = "disable"

        self.eg.update(EasyData(self.modified_row, self.modified))
        self.modified()

        center(self.window)
        self.window.grab_set()
        self.window.deiconify()

    def on_remove(self):
        if not self.treeview.selection():
            return

        index = self.treeview.selection()[0]
        self.current_id = str(self.treeview.item(index)['values'][0]).split('*')[0]
        if not self.current_id.startswith('X'):
            messagebox.showinfo('Delete', 'You cannot delete a consolidated element!')
            return

        self.original_row = self.modified_data.get(self.current_id, None)
        if self.original_row is None:
            self.original_row = self.data[self.current_id]
        name = self.original_row['Name']
        if messagebox.askyesno('Delete', f"Are you sure you want to delete {name}?"):
            new_row = {'Name': name, 'INTERNAL_DELETED': True}
            if self.current_id in self.data:
                self.modified_data[self.current_id] = new_row
            else:
                del self.modified_data[self.current_id]
            self.update_row(self.current_id, new_row)

    def on_double_click(self, _):
        if not self.treeview.selection():
            return

        self.creating = False
        self.eg_save_button['text'] = 'Save'

        index = self.treeview.selection()[0]
        self.current_id = str(self.treeview.item(index)['values'][0]).split('*')[0]
        self.original_row = self.modified_data.get(self.current_id, None)
        if self.original_row is None:
            self.original_row = self.data[self.current_id]
        self.modified_row = copy.deepcopy(self.original_row)

        self.modified()

        self.eg_save_button['state'] = "disable"

        self.eg.update(EasyData(self.modified_row, self.modified))

        center(self.window)
        self.window.grab_set()
        self.window.deiconify()

    def build(self, parent):
        self.frame = Frame(parent)

        self.treeview = Treeview(self.frame, selectmode='browse', column=tuple([ei.name for ei in self.structure]),
                                 show='headings')
        for i in range(len(self.structure)):
            ei = self.structure[i]
            self.treeview.heading(f'#{i + 1}', text=ei.name, anchor=CENTER)
            self.treeview.column(f'#{i + 1}', anchor=W)
        self.treeview.bind("<Double-1>", self.on_double_click)
        self.treeview.pack(fill=BOTH, expand=True)

        for i in range(len(self.widths)):
            val = self.widths[i]
            if val:
                self.treeview.column(f'#{i + 1}', minwidth=val, width=val, stretch=NO)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=0)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)

        self.frame.pack(fill=BOTH, expand=True)

        # Window

        self.window = Toplevel(self.treeview)
        self.window.title("JSON Editor")
        self.window.resizable(False, False)
        self.window.withdraw()

        self.eg = EasyGrid(self.structure, self.weights)
        self.eg.build(self.window)
        self.eg.grid(0, 0)

        save_frame = Frame(self.window)

        self.eg_save_button = Button(save_frame, text="Save")
        self.eg_save_button.pack(side=LEFT, padx=5)
        self.eg_reset_button = Button(save_frame, text="Reset")
        self.eg_reset_button.pack(side=RIGHT, padx=5)

        def recur_diff(a, b):
            for k in a.keys():
                if a[k] == b.get(k, None):
                    if type(a[k]) == dict:
                        diff = recur_diff(a[k], b.get(k, None))
                        if diff:
                            return diff
                else:
                    return k
            return None

        def focus_set(_):
            last_modification = recur_diff(self.original_row, self.modified_row)
            self.eg_save_button.focus_set()

            def after_focus():
                if self.creating:
                    self.window.withdraw()
                    self.window.grab_release()
                    self.modified_data[self.current_id] = self.modified_row
                    total = self.original_row.copy()
                    total.update(self.modified_row)
                    self.modified_row = None
                    self.update_row(self.current_id, total)
                    print(self.modified_data)
                    messagebox.showinfo("Created", "Created successfully!")
                else:
                    if last_modification and (not self.is_modified()):
                        messagebox.showinfo("Error", f"Could not save: field '{last_modification}' was wrong!")
                    elif self.is_modified():
                        self.window.withdraw()
                        self.window.grab_release()
                        self.modified_data[self.current_id] = self.modified_row
                        total = self.original_row.copy()
                        total.update(self.modified_row)
                        current_data = self.data.get(self.current_id)
                        if current_data is None:
                            current_data = self.modified_data[self.current_id]
                        elif current_data == self.modified_row:
                            del self.modified_data[self.current_id]
                        self.modified_row = None
                        self.update_row(self.current_id, total)
                        messagebox.showinfo("Saved", "Saved successfully!")

            self.treeview.after(0, after_focus)

        self.eg_save_button.bind("<1>", focus_set)
        self.eg_save_button['state'] = "disabled"

        def reset_focus_set(_):
            self.eg_reset_button.focus_set()

            def after_reset_focus():
                if messagebox.askyesno('Reset', 'Are you sure you want to reset modified data?'):
                    if (self.current_id in self.modified_data) and (self.current_id in self.data):
                        del self.modified_data[self.current_id]
                    if self.creating:
                        self.original_row = self.sample_create
                        self.modified_row = copy.deepcopy(self.sample_create)
                    else:
                        self.original_row = self.data.get(self.current_id)
                        if self.original_row is None:
                            self.original_row = self.modified_data[self.current_id]
                            self.modified_row = copy.deepcopy(self.original_row)
                            self.update_row(self.current_id, self.modified_data[self.current_id])
                        else:
                            self.original_row = self.modified_data[self.current_id]
                            self.modified_row = copy.deepcopy(self.original_row)
                            self.update_row(self.current_id, self.modified_row[self.current_id])
                    self.eg.update(EasyData(self.modified_row, self.modified))
                    self.modified()

            self.treeview.after(0, after_reset_focus)

        self.eg_reset_button.bind("<1>", reset_focus_set)
        self.eg_reset_button['state'] = "disabled"

        save_frame.grid(row=1, column=0, sticky='s', pady=(15, 15))

        def try_close():
            if self.is_modified():
                if messagebox.askokcancel("Quit", "Are you sure you want to exit without saving?"):
                    self.window.grab_release()
                    self.window.withdraw()
            else:
                self.window.grab_release()
                self.window.withdraw()

        self.window.protocol("WM_DELETE_WINDOW", try_close)

    def update_row(self, row_id, row_data):
        to_show = []
        if row_data.get('INTERNAL_DELETED') is not None:
            if self.treeview.exists(row_id):
                self.treeview.delete(row_id)
            return
        for ei in self.structure:
            if isinstance(ei.easy, EasyJSON):
                ej = cast(EasyJSON, ei.easy)
                to_show.append(ej.show(row_data, row_id))
        if self.treeview.exists(row_id):
            got_data = self.data.get(row_id)
            if got_data is None:
                got_data = self.modified_data[row_id]
            if got_data == row_data:
                self.treeview.item(row_id, values=tuple(to_show))
            else:
                to_show[0] += '*'
                self.treeview.item(row_id, values=tuple(to_show))
        else:
            self.treeview.insert('', END, row_id, values=tuple(to_show))

    def update(self, data):
        self.data = data
        self.treeview.delete(*self.treeview.get_children())
        for k in sorted(data.keys()):
            self.update_row(k, data[k])

    def grid(self, row, column, sticky='nsew', columnspan=1, rowspan=1):
        Easy.grid(self, row, column, sticky, columnspan, rowspan)

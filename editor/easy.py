import copy
import random
from abc import ABC, abstractmethod
from tkinter import messagebox
from tkinter.ttk import Treeview
from typing import Any, cast
from tkinter import *

from jsonpath_ng import parse

from adventure_classes.generic.battle_entity import BattleEntity
from entities.bot_entity import BotEntity
from tk_utils import center
from item_data.stat import Stat


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

    def grid(self, row, column, sticky='nsew', column_span=1, row_span=1):
        self.frame.grid(row=row, column=column, columnspan=column_span, rowspan=row_span, sticky=sticky)


class EasyItem:
    def __init__(self, name: str, easy: Easy, row: int, column: int, sticky: str = 'nsew',
                 column_span: int = 1, row_span: int = 1, field_width: int = 10):
        self.name = name
        self.easy = easy
        self.row = row
        self.column = column
        self.sticky = sticky
        self.row_span = row_span
        self.column_span = column_span
        self.field_width = field_width


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
        if value is not None:
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
    def any(new_value: str):
        return True, new_value

    @staticmethod
    def not_empty(new_value: str):
        if new_value:
            return True, new_value
        return False, None

    @staticmethod
    def positive(new_value: str):
        try:
            if new_value:
                if int(new_value) >= 0:
                    return True, int(new_value)
        except ValueError:
            return False, None
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
    def __init__(self, name: str, path: str, validation: Any = EasyValidation.any, width: int = 20):
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

        inp = OptionMenu(self.frame, self.var, *[x.get_name() for x in self.enum], command=self.save)
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

    def grid(self, row, column, sticky='nsew', column_span=1, row_span=1):
        Easy.grid(self, row, column, sticky, column_span, row_span)
        for i in range(len(self.weights)):
            self.frame.grid_columnconfigure(i, weight=self.weights[i])
        for ei in self.structure:
            if isinstance(ei.easy, EasyJSON):
                ej = cast(EasyJSON, ei.easy)
                if ej.is_editable:
                    ej.grid(ei.row, ei.column, ei.sticky, ei.column_span, ei.row_span)


class EasyJSONStats(EasyGrid, EasyJSON):
    def __init__(self, path):
        x = 0
        y = 0
        limit = 4
        structure = []
        for stat in Stat:
            structure.append(EasyItem(stat.get_abv(),
                                      EasyJSONField(stat.get_abv(), path + '.' + stat.get_abv(),
                                                    EasyValidation.empty_or_positive,
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

    def grid(self, row, column, sticky='nsew', column_span=1, row_span=1):
        EasyGrid.grid(self, row, column, sticky, column_span, row_span)

    def show(self, data: dict[str, Any], key) -> str:
        tr = []
        for stat in Stat.get_all():
            value = EasyJSON.get_value(self, data).get(stat.abv, 0)
            if value:
                tr.append(f"{stat.abv}: {value}")
        return ', '.join(tr)


class EasyJSONStatsWeights(EasyJSONStats):
    def show(self, data: dict[str, Any], key) -> str:
        tr = []
        for stat in Stat:
            value = EasyJSON.get_value(self, data).get(stat.get_abv())
            if value:
                tr.append((f"{stat.value.represent(stat.get_value(value))} {stat.get_abv()}", value))
        tr.sort(key=lambda x: -x[1])
        return ', '.join([x[0] for x in tr])


class EasyJSONBattleStats(EasyJSONStats):
    def show(self, data: dict[str, Any], key) -> str:
        stat_data = {Stat.get_by_abv(x): v for x, v in data['Stats'].items()}
        return BattleEntity(BotEntity('', stat_data)).print() + f' [{sum(stat_data.values())}]'


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
        self.tree_view = None
        self.widths = widths
        self.sample_create = None
        self.creating = False
        self.filters = None
        self.filtering_by = None

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
        if not self.tree_view.selection():
            return

        index = self.tree_view.selection()[0]
        self.current_id = str(self.tree_view.item(index)['values'][0]).split('*')[0]
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
        if not self.tree_view.selection():
            return

        self.creating = False
        self.eg_save_button['text'] = 'Save'

        index = self.tree_view.selection()[0]
        self.current_id = str(self.tree_view.item(index)['values'][0]).split('*')[0]
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

    def inp_upd_serve(self, i):
        def inp_upd(x):
            self.filtering_by[i] = x.lower()
            self.update()
            return True
        return inp_upd

    def build(self, parent):
        self.frame = Frame(parent)

        self.filtering_by = [None] * len(self.structure)

        self.filters = Frame(self.frame)

        for i in range(len(self.structure)):
            element = self.structure[i]
            if isinstance(element.easy, EasyJSONKey) or isinstance(element.easy, EasyJSONStats):
                continue
            text = Label(self.filters, text=element.name)
            text.pack(side=LEFT, padx=5)
            if isinstance(element.easy, EasyJSONEnum):
                inp = OptionMenu(self.filters, StringVar(), '', *[x.get_name() for x in element.easy.enum],
                                 command=self.inp_upd_serve(i))
                inp.configure(width=element.field_width)
                inp.pack(side=LEFT, pady=5)
            else:
                inp = Entry(self.filters)
                inp.configure(width=element.field_width)
                validation_command = self.frame.register(self.inp_upd_serve(i))
                inp.configure(validate='all', validatecommand=(validation_command, '%P'))
                inp.pack(side=LEFT, pady=5)

        self.filters.grid(row=0, column=0, columnspan=2, sticky='ew')

        self.tree_view = Treeview(self.frame, selectmode='browse', column=tuple([ei.name for ei in self.structure]),
                                  show='headings')
        for i in range(len(self.structure)):
            ei = self.structure[i]
            self.tree_view.heading(f'#{i + 1}', text=ei.name, anchor=CENTER)
            self.tree_view.column(f'#{i + 1}', anchor=W)
        self.tree_view.bind("<Double-1>", self.on_double_click)
        self.tree_view.bind("<Return>", self.on_double_click)
        self.tree_view.grid(row=1, column=0, sticky='news')

        scroll = Scrollbar(self.frame, orient="vertical", command=self.tree_view.yview)
        scroll.grid(row=1, column=1, sticky='ns')

        self.tree_view.configure(yscrollcommand=scroll.set)

        for i in range(len(self.widths)):
            val = self.widths[i]
            if val:
                self.tree_view.column(f'#{i + 1}', minwidth=val, width=val, stretch=NO)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=0)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)

        self.frame.grid(row=2, column=0, columnspan=2, sticky='news')

        self.frame.rowconfigure(0, weight=0)

        # Window

        self.window = Toplevel(self.tree_view)
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
                        if (current_data is not None) and current_data == self.modified_row:
                            del self.modified_data[self.current_id]
                        self.modified_row = None
                        self.update_row(self.current_id, total)

            self.tree_view.after(0, after_focus)

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

            self.tree_view.after(0, after_reset_focus)

        self.eg_reset_button.bind("<1>", reset_focus_set)
        self.eg_reset_button['state'] = "disabled"

        save_frame.grid(row=1, column=0, sticky='s', pady=(15, 15))

        def try_close():
            if self.is_modified():
                if messagebox.askyesno("Quit", "Are you sure you want to exit without saving?"):
                    self.window.grab_release()
                    self.window.withdraw()
            else:
                self.window.grab_release()
                self.window.withdraw()

        self.window.protocol("WM_DELETE_WINDOW", try_close)

    def update_row(self, row_id, row_data):
        to_show = []
        if row_data.get('INTERNAL_DELETED') is not None:
            if self.tree_view.exists(row_id):
                self.tree_view.delete(row_id)
            return
        for ei in self.structure:
            if isinstance(ei.easy, EasyJSON):
                ej = cast(EasyJSON, ei.easy)
                to_show.append(ej.show(row_data, row_id))
        if self.tree_view.exists(row_id):
            got_data = self.data.get(row_id)
            if got_data is None:
                got_data = self.modified_data[row_id]
            if got_data == row_data:
                self.tree_view.item(row_id, values=tuple(to_show))
            else:
                to_show[0] += '*'
                self.tree_view.item(row_id, values=tuple(to_show))
        else:
            self.tree_view.insert('', END, row_id, values=tuple(to_show))

    @staticmethod
    def sort(x: str):
        if x.isnumeric():
            return int(x)
        else:
            return -1

    def update(self, data=None):
        if data:
            self.data = data
        else:
            data = copy.deepcopy(self.data)
            data.update(self.modified_data)
        self.tree_view.delete(*self.tree_view.get_children())
        for k in sorted(data.keys(), key=EasyGridTree.sort):
            correct = True
            for i in range(len(self.structure)):
                if self.filtering_by[i]:
                    if self.structure[i].name in data[k]:
                        if self.filtering_by[i] not in data[k][self.structure[i].name].lower():
                            correct = False
                            break
            if correct:
                self.update_row(k, data[k])

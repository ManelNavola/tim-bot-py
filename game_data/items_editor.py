import json
import random
from typing import Any, Optional

import PySimpleGUI as Sg

from item_data.abilities import Ability, AbilityDesc
from item_data.item_classes import ItemType
from item_data.stats import Stats


def item_dict_to_row(key: str, data: dict) -> list[str]:
    stat_list: list[str] = []
    for stat in Stats.get_all():
        stat_list.append(data['Stats'].get(stat.abv, ""))
    return [key, data['Name'], data['Type']] + stat_list + [data.get('Ability', "")]


def item_row_to_dict(row: list[str]) -> tuple[str, dict[str, Any]]:
    stats: dict = {}
    all_stats = Stats.get_all()
    for i in range(len(all_stats)):
        if row[i + 3]:
            stats[all_stats[i].abv] = row[i + 3]
    after_stats: int = len(all_stats) + 3
    data: dict = {
        'Name': row[1],
        'Type': row[2],
        'Stats': {k: int(v) for k, v in stats.items()}
    }
    if row[after_stats]:
        data['Ability'] = row[after_stats]
    return row[0], data


def modify_item_row(item_data) -> Optional[list]:
    i = 1
    all_stats = Stats.get_all()
    name_column = Sg.Column([
        [Sg.Text("Name")],
        [Sg.InputText(item_data[i], size=(20, 1), justification='center', enable_events=True, key='ChangedName')]
    ], expand_y=True, pad=(0, 0))
    i += 1
    type_column = Sg.Column([
        [Sg.Text("Type")],
        [Sg.Combo([x.get_name() for x in ItemType.get_all()], item_data[i] or ItemType.get_all()[0].get_name(),
                  size=(15, 1), enable_events=True, key=f'Changed{i}', readonly=True)]
    ], expand_y=True, pad=(0, 0))
    i += 1
    stat_columns = []
    for stat in all_stats:
        stat_columns.append(Sg.Column([
            [Sg.Text(stat.abv)],
            [Sg.InputText(item_data[i], size=(5, 1), justification='center', enable_events=True,
                          key=f"Changed{i}")]
        ], expand_y=True, pad=(0, 0)))
        i += 1

    ability_column = Sg.Column([
        [Sg.Text("Ability")],
        [Sg.Combo([x.get_name() for x in Ability.get_all()] + [''], item_data[i],
                  size=(15, 1), enable_events=True, key=f'Changed{i}', readonly=True)]
    ], expand_y=True, pad=(0, 0))

    ab_name = item_data[len(Stats.get_all()) + 3]
    ab: Optional[AbilityDesc] = Ability.get_by_name(ab_name)
    window = Sg.Window("Modifying item", [
        [name_column, type_column] + stat_columns + [ability_column],
        [Sg.Button("Save Item"), Sg.Text('No ability' if ab is None else f'{ab_name}: {ab.get_tier(0).print()}',
                                         key='Ability', size=(80, 1))]
    ], modal=True, size=(960 + 32, 128 + 32), enable_close_attempted_event=True, font=("Helvetica", 11))

    new_item_data = [x for x in item_data]
    while True:
        event, values = window.read()
        if event == Sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            if '-'.join([str(x) for x in new_item_data]) != '-'.join([str(x) for x in item_data]):
                a = Sg.popup_yes_no("Do you want to exit without saving?")
                if a == 'Yes':
                    break
            else:
                break
        elif event == 'Save Item':
            i = 1
            if len(new_item_data[i]) < 1:
                Sg.popup_error("Name cannot be empty!")
            elif new_item_data[i] != new_item_data[i].strip():
                Sg.popup_error("White space before or after the name is not allowed :S")
                window['ChangedName'].update(new_item_data[i].strip())
                new_item_data[i] = new_item_data[i].strip()
            else:
                i += 2
                all_empty = True
                failed = False
                diff = i
                for _ in all_stats:
                    if new_item_data[i] != '':
                        all_empty = False
                        try:
                            int(new_item_data[i])
                        except ValueError:
                            Sg.popup_error(f"Stat {all_stats[i - diff].abv} must be empty or an int above 0")
                            failed = True
                            break
                    i += 1
                if not failed:
                    if all_empty:
                        Sg.popup_error("At least one stat must be filled")
                    else:
                        Sg.popup_ok("Saved successfully")
                        window.close()
                        return new_item_data
        elif event.startswith('Changed'):
            new_item_data = [item_data[0]] + list(values.values())
            for x in values.values():
                if x.isnumeric():
                    new_item_data.append(int(x))
                else:
                    new_item_data.append(x)
            ab_name = new_item_data[len(Stats.get_all()) + 3]
            if ab_name != '':
                window['Ability'].update(f'{ab_name}: {Ability.get_by_name(ab_name).get_tier(0).print()}')
            else:
                window['Ability'].update('No ability')

    window.close()

    return None


def items_window():
    changes: bool = False
    filter_by: str = 'All'
    contains: str = ''
    last_index: int = 0

    with open('items.json', 'r') as json_file:
        loaded_json = json.load(json_file)

    item_rows: list[list[Any]] = []
    modified: set[str] = set()

    for item_id in sorted(loaded_json):
        item_rows.append(item_dict_to_row(item_id, loaded_json[item_id]))
        if item_id.isnumeric():
            last_index = max(int(item_id), last_index)

    current_item_rows = [x for x in item_rows]

    table = Sg.Table(item_rows, ['Id', 'Name', 'Type'] + [x.abv for x in Stats.get_all()] + ['Ability'], key='Table',
                     col_widths=[4, 20, 10] + [5 for _ in Stats.get_all()] + [15],
                     justification='center', bind_return_key=True, auto_size_columns=False,
                     alternating_row_color='#AACCAA', num_rows=50)

    def update_table():
        nonlocal current_item_rows, table
        if filter_by == 'All':
            current_item_rows = [x for x in item_rows]
        elif filter_by == 'Unconsolidated':
            current_item_rows = [x for x in item_rows if x[0][0] == 'X']
        else:
            current_item_rows = [x for x in item_rows if x[2] == filter_by]
        table.update([x for x in current_item_rows if contains.lower() in x[1].lower()])

    gui = [
        [Sg.Text("Filter by:"),
         Sg.Combo(['All', 'Unconsolidated'] + [x.get_name() for x in ItemType.get_all()], 'All',
                  size=(15, 1), enable_events=True, key='Filter', readonly=True),
         Sg.Text("Contains:"),
         Sg.InputText('', size=(20, 1), enable_events=True, key='Contains'),
         Sg.HSeparator(),
         Sg.Button("Consolidate", key='Cons'),
         Sg.Button("(+) Add new Item", key='Add'),
         Sg.Button("SAVE ALL", key='Save', disabled=True)],
        [table]
    ]

    window = Sg.Window("Items", gui, modal=True, size=(960, 640), font=("Helvetica", 11), finalize=True)
    window['Table'].expand(expand_x=True, expand_y=True, expand_row=True)

    while True:
        event, values = window.read()
        if event == 'Table':
            if values['Table']:
                index = values['Table'][0]
                new_row = modify_item_row(item_rows[index])
                if new_row is not None:
                    item_rows[index] = new_row
                    modified.add(new_row[0])
                    changes = True
                    update_table()
        elif event == 'Add':
            new_row = modify_item_row(item_dict_to_row('', {
                'Name': "",
                'Stats': {},
                'Type': ItemType.BOOT.get_name()
            }))
            if new_row is not None:
                new_row[0] = 'X\n' + str(random.random())
                item_rows.append(new_row)
                changes = True
                update_table()
        elif event == 'Save':
            saving = Sg.Window("Saving", [[Sg.Text("Saving...", key="Saving", size=(20, 1))],
                                          [Sg.HSeparator(), Sg.Button("OK", disabled=True), Sg.HSeparator()]],
                               modal=True, size=(240, 64), finalize=True, enable_close_attempted_event=True)
            for row in item_rows:
                if (loaded_json.get(row[0]) is None) or (row[0] in modified):
                    _, loaded_json[row[0]] = item_row_to_dict(row)
            with open("items.json", "w") as f:
                json.dump(loaded_json, f, indent=2)

            modified.clear()
            saving["Saving"].update("Saved successfully!")
            saving["OK"].update(disabled=False)
            window["Save"].update(disabled=True)
            window["Cons"].update(disabled=False)
            changes = False
            while True:
                event2, value2 = saving.read()
                if event2 == 'OK' or event2 == Sg.WINDOW_CLOSED or event2 == Sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                    break

            saving.close()
        elif event == 'Cons':
            is_yes = Sg.popup_yes_no("Are you sure you want to consolidate the JSON? This is an irreversible action!")
            if is_yes == 'Yes':
                saving = Sg.Window("Consolidating...", [[Sg.Text("Saving...", key="Saving", size=(20, 1))],
                                                        [Sg.HSeparator(), Sg.Button("OK", disabled=True),
                                                         Sg.HSeparator()]],
                                   modal=True, size=(240, 64), finalize=True, enable_close_attempted_event=True)
                last_index += 1
                for row in item_rows:
                    if row[0].startswith('X'):
                        del loaded_json[row[0]]
                        _, loaded_json[last_index] = item_row_to_dict(row)
                        last_index += 1
                with open("items.json", "w") as f:
                    json.dump(loaded_json, f, indent=2)

                saving["Saving"].update("JSON Consolidated!")
                saving["OK"].update(disabled=False)
                while True:
                    event2, value2 = saving.read()
                    if event2 == 'OK' or event2 == Sg.WINDOW_CLOSED or event2 == Sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                        break

                saving.close()
                break
        elif event in ['Filter', 'Contains']:
            if event == 'Filter':
                filter_by = values['Filter']
            elif event == 'Contains':
                contains = values['Contains']
            update_table()
        elif event == Sg.WINDOW_CLOSED:
            break

        if changes:
            window["Save"].update(disabled=False)
            window["Cons"].update(disabled=True)

    window.close()

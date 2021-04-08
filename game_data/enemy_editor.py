import json
import random
from typing import Any, Optional

import PySimpleGUI as Sg

from entities.bot_entity import BotEntity
from item_data.item_classes import ItemType
from item_data.stats import Stats
from adventures.battle_data.battle_entity import BattleEntity


def enemy_dict_to_row(key: str, data: dict) -> list[str]:
    stat_list: list[str] = []
    for stat in Stats.get_all():
        stat_list.append(data['Stats'].get(stat.abv, ""))
    return [key, data['Name']] + stat_list


def enemy_row_to_dict(row: list[str]) -> tuple[str, dict[str, Any]]:
    stats: dict = {}
    all_stats = Stats.get_all()
    for i in range(len(all_stats)):
        if row[i + 2]:
            stats[all_stats[i].abv] = row[i + 2]
    data: dict = {
        'Name': row[1],
        'Stats': {k: int(v) for k, v in stats.items()}
    }
    return row[0], data


def build_entity(enemy_data: list[str]) -> BattleEntity:
    stats: dict = {}
    all_stats = Stats.get_all()
    for i in range(len(all_stats)):
        if enemy_data[i + 2]:
            try:
                stats[all_stats[i]] = int(enemy_data[i + 2])
            except ValueError:
                pass
    return BattleEntity(BotEntity(enemy_data[1], stats))


def modify_enemy_row(enemy_data) -> Optional[list]:
    i = 1
    all_stats = Stats.get_all()
    name_column = Sg.Column([
        [Sg.Text("Name")],
        [Sg.InputText(enemy_data[i], size=(20, 1), justification='center', enable_events=True, key='ChangedName')]
    ], expand_y=True, pad=(0, 0))
    i += 1
    stat_columns = []
    for stat in all_stats:
        stat_columns.append(Sg.Column([
            [Sg.Text(stat.abv)],
            [Sg.InputText(enemy_data[i], size=(5, 1), justification='center', enable_events=True,
                          key=f"Changed{i}")]
        ], expand_y=True, pad=(0, 0)))
        i += 1

    window = Sg.Window("Modifying enemy", [
        [name_column] + stat_columns,
        [Sg.Button("Save Enemy"), Sg.Text(f"{build_entity(enemy_data).print()}",
                                          key='Ability', size=(80, 1))]
    ], modal=True, size=(960 + 32, 128 + 32), enable_close_attempted_event=True, font=("Helvetica", 11))

    new_enemy_data = [x for x in enemy_data]
    while True:
        event, values = window.read()
        if event == Sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            if '-'.join([str(x) for x in new_enemy_data]) != '-'.join([str(x) for x in enemy_data]):
                a = Sg.popup_yes_no("Do you want to exit without saving?")
                if a == 'Yes':
                    break
            else:
                break
        elif event == 'Save Enemy':
            i = 1
            if len(new_enemy_data[i]) < 1:
                Sg.popup_error("Name cannot be empty!")
            elif new_enemy_data[i] != new_enemy_data[i].strip():
                Sg.popup_error("White space before or after the name is not allowed :S")
                window['ChangedName'].update(new_enemy_data[i].strip())
                new_enemy_data[i] = new_enemy_data[i].strip()
            else:
                i += 1
                failed = False
                diff = i
                for stat in all_stats:
                    if stat == Stats.HP:
                        print(build_entity(new_enemy_data).get_stat(Stats.HP))
                        if build_entity(new_enemy_data).get_stat(Stats.HP) <= 0:
                            Sg.popup_error(f"HP must be higher than 0!")
                            failed = True
                            break
                    if new_enemy_data[i] != '':
                        try:
                            int(new_enemy_data[i])
                        except ValueError:
                            Sg.popup_error(f"Stat {all_stats[i - diff].abv} must be empty or an int above 0")
                            failed = True
                            break
                    i += 1
                if not failed:
                    Sg.popup_ok("Saved successfully")
                    window.close()
                    return new_enemy_data
        elif event.startswith('Changed'):
            new_enemy_data = [enemy_data[0]] + list(values.values())
            for x in values.values():
                if x.isnumeric():
                    new_enemy_data.append(int(x))
                else:
                    new_enemy_data.append(x)
            window['Ability'].update(build_entity(new_enemy_data).print())

    window.close()

    return None


def enemies_window():
    changes: bool = False
    contains: str = ''
    last_index: int = 0

    with open('enemies.json', 'r') as json_file:
        loaded_json = json.load(json_file)

    enemy_rows: list[list[Any]] = []
    modified: set[str] = set()

    for item_id in sorted(loaded_json):
        enemy_rows.append(enemy_dict_to_row(item_id, loaded_json[item_id]))
        if item_id.isnumeric():
            last_index = max(int(item_id), last_index)

    current_item_rows = [x for x in enemy_rows]

    table = Sg.Table(enemy_rows, ['Id', 'Name'] + [x.abv for x in Stats.get_all()], key='Table',
                     col_widths=[4, 20] + [5 for _ in Stats.get_all()],
                     justification='center', bind_return_key=True, auto_size_columns=False,
                     alternating_row_color='#AACCAA', num_rows=50)

    def update_table():
        nonlocal current_item_rows, table
        current_item_rows = [x for x in enemy_rows]
        table.update([x for x in current_item_rows if contains.lower() in x[1].lower()])

    gui = [
        [Sg.Text("Contains:"),
         Sg.InputText('', size=(20, 1), enable_events=True, key='Contains'),
         Sg.HSeparator(),
         Sg.Button("Consolidate", key='Cons'),
         Sg.Button("(+) Add new Enemy", key='Add'),
         Sg.Button("SAVE ALL", key='Save', disabled=True)],
        [table]
    ]

    window = Sg.Window("Enemies", gui, modal=True, size=(960, 640), font=("Helvetica", 11), finalize=True)
    window['Table'].expand(expand_x=True, expand_y=True, expand_row=True)

    while True:
        event, values = window.read()
        if event == 'Table':
            if values['Table']:
                index = values['Table'][0]
                new_row = modify_enemy_row(enemy_rows[index])
                if new_row is not None:
                    enemy_rows[index] = new_row
                    modified.add(new_row[0])
                    changes = True
                    update_table()
        elif event == 'Add':
            new_row = modify_enemy_row(enemy_dict_to_row('', {
                'Name': "",
                'Stats': {},
                'Type': ItemType.BOOT.get_name()
            }))
            if new_row is not None:
                new_row[0] = 'X\n' + str(random.random())
                enemy_rows.append(new_row)
                changes = True
                update_table()
        elif event == 'Save':
            saving = Sg.Window("Saving", [[Sg.Text("Saving...", key="Saving", size=(20, 1))],
                                          [Sg.HSeparator(), Sg.Button("OK", disabled=True), Sg.HSeparator()]],
                               modal=True, size=(240, 64), finalize=True, enable_close_attempted_event=True)
            for row in enemy_rows:
                if (loaded_json.get(row[0]) is None) or (row[0] in modified):
                    _, loaded_json[row[0]] = enemy_row_to_dict(row)
            with open("enemies.json", "w") as f:
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
                for row in enemy_rows:
                    if row[0].startswith('X'):
                        del loaded_json[row[0]]
                        _, loaded_json[last_index] = enemy_row_to_dict(row)
                        last_index += 1
                with open("enemies.json", "w") as f:
                    json.dump(loaded_json, f, indent=2)

                saving["Saving"].update("JSON Consolidated!")
                saving["OK"].update(disabled=False)
                while True:
                    event2, value2 = saving.read()
                    if event2 == 'OK' or event2 == Sg.WINDOW_CLOSED or event2 == Sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                        break

                saving.close()
                break
        elif event == 'Contains':
            contains = values['Contains']
            update_table()
        elif event == Sg.WINDOW_CLOSED:
            break

        if changes:
            window["Save"].update(disabled=False)
            window["Cons"].update(disabled=True)

    window.close()

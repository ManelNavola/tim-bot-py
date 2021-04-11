# import PySimpleGUI as Sg
#
# from game_data.enemy_editor import enemies_window
# from game_data.items_editor import items_window
#
# Sg.theme('LightGreen3')
#
# main_window = Sg.Window("Game Data Editor", [
#     [Sg.Text("Choose game data to edit:")],
#     [Sg.Button("Items"), Sg.Button("Enemies")]
# ], size=(640, 240), font=("Helvetica", 13))
#
# while True:
#     m_event, m_values = main_window.read()
#     if m_event == Sg.WINDOW_CLOSED:
#         break
#     if m_event == "Items":
#         items_window()
#     elif m_event == "Enemies":
#         enemies_window()

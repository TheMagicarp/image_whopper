import PySimpleGUI as sg
import button_functions
import main_functions
import picture_works

symbol_right = '►'
symbol_down = '▼'
SYMBOL_ANTICLOCKWISE = "\N{Anticlockwise Open Circle Arrow}"

"""
------------------------------------------OKNA-------------------------------------------------------------------------------------------------------
"""


def similar_pic_choose(package):
    package["current_list_number"] = 0
    package["current_image_number"] = 0

    for sub_list in package["list_of_similars"]:
        for image in sub_list:
            package["tick_boxes"].update({image: False})

    numbering_layout = [
        [sg.Text("Group: "), sg.Text("1", key="-CGROUP-", size=(2, 1)), sg.Text("/", size=(1, 1)),
         sg.Text(len(package["list_of_similars"]), key="-AGROUP-")],
        [sg.Text("Image: "), sg.Text("", key="-IMGNAME-", size=(30, 1)), sg.Text("| Sharpness: "),
         sg.Text("", key="-SHARPNESS_INFO-", size=(4, 1))],
        [sg.Text("", key="-CNUM-", size=(2, 1)), sg.Text("/", size=(1, 1)), sg.Text("", key="-ANUM-", size=(2, 1))]
    ]
    pic_frame_layout = [
        [sg.Frame("", [[sg.Image(key="-IMAGE-")]], size=(1000, 500), key="-PIC_HOLDER-", border_width=0)]
    ]
    checkboxes_layout = [
        [sg.Checkbox("keep", default=False, enable_events=True, key="-CHECKBOX-"),
         sg.Checkbox("keep all", default=False, enable_events=True, key="-KEEPALL-")]
    ]
    navigation_layout = [
        [sg.Button("<"),
         sg.Slider(range=(1, len(package["list_of_similars"][package["current_list_number"]])), orientation='h',
                   size=(100, 20), enable_events=True, default_value=1, key="-SLIDER-"), sg.Button(">")]
    ]
    menu_layout = [
        [sg.Button("Save", key="-SAVE_BUTTON-"), sg.Button("Auto-pick all", key="-AUTOPICK_ALL_BUTTON-"),
         sg.Button("Exit", key="-EXIT_BUTTON-")]
    ]

    layout = [[sg.Column(numbering_layout)],
              [sg.Column(pic_frame_layout)],
              [sg.Column(checkboxes_layout)],
              [sg.Column(navigation_layout)],
              [sg.Column(menu_layout)]
              ]

    window = sg.Window("Picking out similarities", layout, size=(1200, 800), modal=True, resizable=False,
                       element_justification="c", finalize=True, return_keyboard_events=True, use_default_focus=False)

    package["window"] = window
    print("kontrola 1")
    main_functions.jump_to_image(package)
    print("kontrola 2")
    main_functions.reset_slider(package)
    print("kontrola 3")

    while True:
        event, values = window.read()
        package["values"] = values
        package["window"] = window

        if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == "-EXIT_BUTTON-" or event == sg.WINDOW_CLOSED:
            break

        if event == event == "-SAVE_BUTTON-":
            main_functions.sort_manually_ticked_imgs(package)
            break

        if event == "-CHECKBOX-":
            button_functions.checkbox_tick(package)
        if event == "-KEEPALL-":
            button_functions.keep_all_button(package)

        if event == "-SLIDER-":
            button_functions.slider_change(package)
        if event == "Up:38":
            button_functions.keypress_up(package)
        if event == "Down:40":
            button_functions.keypress_down(package)

        if event == ">" or event == "Right:39":
            button_functions.next_group(package)
        if event == "<" or event == "Left:37":
            button_functions.previous_group(package)

        if event == "-AUTOPICK_ALL_BUTTON-":
            main_functions.autopick(package)
            break

    window.close()


def manual_pic_sort(package, image_group):
    package["current_image_number"] = 0
    ok_button_visibility = True
    blurry_button_visibility = True
    if image_group == "OK":
        package["working_images"] = package["ok_list"]
        ok_button_visibility = False
    elif image_group == "Unsure":
        package["working_images"] = package["unsure_list"]
    elif image_group == "Blurry":
        package["working_images"] = package["blurry_list"]
        blurry_button_visibility = False
    elif image_group == "Rotated":
        package["working_images"] = package["rotated"]
        ok_button_visibility = False
        blurry_button_visibility = False
    else:
        assert "ERROR, WRONG TYPE"

    layout = [
        [sg.Text("Image: "), sg.Text("", key="-IMGNAME-", size=(20, 1)), sg.Text("| Sharpness: "),
         sg.Text("", key="-SHARPNESS_INFO-", size=(4, 1))],
        [sg.Text("", key="-CNUM-", size=(3, 1)), sg.Text("/", size=(1, 1)),
         sg.Text("", key="-ANUM-", size=(3, 1))],
        [sg.Frame("", [[sg.Image(key="-IMAGE-")]], size=(1000, 500), key="-PIC_HOLDER-", border_width=0)],
        [sg.Button("Exit", key="-EXIT_BUTTON-"),
         sg.Button("OK", key="-OK_BUTTON-", visible=ok_button_visibility),
         sg.Button("Blurry", key="-BLURRY_BUTTON-", visible=blurry_button_visibility),
         sg.Button("<<"),
         sg.Button(">>"),
         sg.Button(SYMBOL_ANTICLOCKWISE, size=(2, 1), font=("Helvetica", 15))]
    ]

    window = sg.Window(f"Manual sorting of {image_group} images", layout, size=(1200, 650), modal=True, resizable=False,
                       element_justification="c", finalize=True, return_keyboard_events=True,
                       use_default_focus=False)  # modal zaručí že lze interagovat pouze s tímto oknem
    package["window"] = window
    main_functions.show_image(package, package["working_images"])

    while True:
        event, values = window.read()
        package["values"] = values
        package["window"] = window

        if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == "-EXIT_BUTTON-" or event == sg.WINDOW_CLOSED:
            break

        if event == ">>" or event == "Right:39":
            button_functions.forward(package)

        if event == "<<" or event == "Left:37":
            button_functions.backward(package)

        if event == "\N{Anticlockwise Open Circle Arrow}":
            button_functions.rotate(package)

        if event == "-OK_BUTTON-" or event == "-BLURRY_BUTTON-":
            if event == "-OK_BUTTON-":
                package["ok_list"].append(package["working_images"].pop(package["current_image_number"]))
            if event == "-BLURRY_BUTTON-":
                package["blurry_list"].append(package["working_images"].pop(package["current_image_number"]))
            if len(package["working_images"]) != 0:
                button_functions.change_img(package)
            else:
                sg.popup_auto_close("All images have been sorted!")
                break
    package["working_images"] = []
    window.close()


def main():
    package = {"chosen_from_similar": [], "to_be_deleted": [], "tick_boxes": dict(), "rotated": [], "faces": {},
               "done": {"blurryness": False, "similarity": False, "load": False},"list_of_images": [], "subdirs": [],
               "orientation_checked": [], "working_images": []}

    # Různé layouts
    preferences_layout = [
        [sg.Checkbox("Include subfolders", key="-INCLUDE_SUBFOLDERS-")],
        [sg.Checkbox("Try to auto-rotate (experimental)", key="-AUTO_ROTATE-")]
    ]
    head_layout = [
        [sg.Text("Path:"), sg.InputText(size=(35, 1), enable_events=True, key="-DIR-"), sg.FolderBrowse(),
         sg.Button("Load")],
        [sg.T(symbol_right, enable_events=True, key="-OPEN_PREFERENCES-"),
         sg.T("Preferences", enable_events=True, key="-OPEN_PREFERENCES-TEXT")],
        [sg.pin(sg.Column(preferences_layout, key="-PREFERENCES-", visible=False))],
        [sg.Text("", key="-PROGRESS-", size=(55, 0))],
        [sg.ProgressBar(1000, key="-PROG-", orientation="h", size=(41, 20))],
    ]
    quality_of_imgs_layout = [
        [sg.Text("", key="-OK_NUM-", size=(15, 1)),
         sg.Button("Check OKs", key="-SORT_OK_BUTTON-")],
        [sg.Text("", key="-UNSURE_NUM-", size=(15, 1)),
         sg.Button("Check Unsures", key="-SORT_UNSURE_BUTTON-")],
        [sg.Text("", key="-BLURRY_NUM-", size=(15, 1)),
         sg.Button("Check Blurryes", key="-SORT_BLURRY_BUTTON-")],
        [sg.Text("", key="-SIMILAR_NUM-", size=(15, 1)),
         sg.Button("Check Similar", key="-SIMILAR_BUTTON-", visible=False)],
        [sg.Text("", key="-ROTATED_NUM-", size=(15, 1)),
         sg.Button("Check Rotated", key="-ROTATED_BUTTON-", visible=False)]
    ]
    action_buttons_layout = [
        [sg.Button("Look for similarities", key="-START_SIM_BUTTON-")],
        [sg.Button("Auto-rotate", key="-AUTO_ROTATE_BUTTON-")]
    ]

    body_layout = [
        [sg.Frame("Action Buttons", action_buttons_layout, key="-ACTION_BUTTONS_LAYOUT-", size=(30, 50)),
         sg.VSeparator(color=sg.DEFAULT_BACKGROUND_COLOR),
         sg.Column(quality_of_imgs_layout, key="-QUALITY_OF_PICS_LAYOUT-")]
    ]

    footer_layout = [
        [sg.Button("Save", key="-SAVE_BUTTON-", visible=False), sg.Button("Exit")]
    ]

    # Main window layout
    layout = [
        [sg.Frame("", head_layout)],
        [sg.Column(body_layout, key="-BODY_LAYOUT-", visible=False)],
        [sg.Column(footer_layout)]
    ]

    window = sg.Window("ThanosPhotos", layout, enable_close_attempted_event=True)
    opened1 = True
    while True:
        event, values = window.read()
        package["values"] = values
        package["window"] = window

        if (event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == "Exit") and sg.popup_yes_no(
                "Do you really want to exit?") == "Yes":
            break

        if event.startswith("-OPEN_PREFERENCES-"):
            opened1 = not opened1
            window["-OPEN_PREFERENCES-"].update(symbol_down if opened1 else symbol_right)
            window['-PREFERENCES-'].update(visible=opened1)

        if event == "Load":
            button_functions.load_pictures(package)

        if event == "-AUTO_ROTATE_BUTTON-":
            button_functions.auto_rotate_button(package)
        if event == "-ROTATED_BUTTON-" and len(package["rotated"]) > 0:
            manual_pic_sort(package, "Rotated")
        if event == "-CLARITY_CHECK_BUTTON-" and package["done"]["blurryness"] == False:
            button_functions.clarity_check_button(package)

        if event == "-SAVE_BUTTON-":
            if sg.popup_yes_no("Are you sure you are done sorting your pictures?") == "Yes":
                button_functions.save_button(package)
                break

        if event == "-START_SIM_BUTTON-" and package["done"]["similarity"] == False:
            button_functions.start_sim_button(package)

        if event == "-DO_IT_ALL_BUTTON-":
            button_functions.do_it_all_button(package)

        if event == "-SORT_OK_BUTTON-" or event == "-SORT_UNSURE_BUTTON-" or event == "-SORT_BLURRY_BUTTON-" or event == "-SIMILAR_BUTTON-":
            if event == "-SORT_OK_BUTTON-" and len(package["ok_list"]) > 0:
                manual_pic_sort(package, "OK")
            if event == "-SORT_UNSURE_BUTTON-" and len(package["unsure_list"]) > 0:
                manual_pic_sort(package, "Unsure")
            if event == "-SORT_BLURRY_BUTTON-" and len(package["blurry_list"]) > 0:
                manual_pic_sort(package, "Blurry")
            if event == "-SIMILAR_BUTTON-" and len(package["list_of_similars"]) > 0:
                try:
                    similar_pic_choose(package)
                    main_functions.integrate_chosen_images(package)
                    package["window"] = window
                    main_functions.update_state_of_pic_sort_message(package)
                except:
                    pass
            package["window"] = window
            main_functions.update_state_of_pic_sort_message(package)

    window.close()


if __name__ == "__main__":
    main()

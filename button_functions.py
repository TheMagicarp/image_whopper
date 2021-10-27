import PySimpleGUI as sg
import os.path
import os
import shutil
import cv2
import time

from PIL import Image

import main_functions
import picture_works
from main_functions import show_image, jump_to_image, update_check_box, change_group


def load_pictures(package):
    if not package["done"]["load"]:
        try:
            package["root_dir"] = package["values"].get("-DIR-").replace("\\", "/") + "/"
            main_functions.load_pictures(package)

            if len(package["list_of_images"][0]) > 0:
                ammount_of_images = len(package["list_of_images"])
                package["window"]["-PROGRESS-"].update(
                    f"Loaded {ammount_of_images} images, estimated processing time is {round(ammount_of_images * 0.12, 2)}s")
                package["window"]["-BODY_LAYOUT-"].update(visible=True)
                clarity_check_button(package)
                if package["values"]["-AUTO_ROTATE-"]:
                    picture_works.auto_rotate(package)

                package["done"]["load"] = True
                package["window"]["-BODY_LAYOUT-"].update(visible=True)
            else:
                package["window"]["-PROGRESS-"].update(f"There are no images in selected directory")
        except OSError:
            package["window"]["-PROGRESS-"].update("Invalid directory")
        except IndexError:
            package["window"]["-PROGRESS-"].update("There are no image in selected directory")
    else:
        package["window"]["-PROGRESS-"].update("You have already loaded images!")

def clarity_check_button(package):
    try:
        picture_works.blurry(package)
        main_functions.update_state_of_pic_sort_message(package)
        package["window"]["-SAVE_BUTTON-"].Update(visible=True)
        package["done"]["blurryness"] = True
    except NameError:
        package["window"]["-PROGRESS-"].update("No images loaded!")


def start_sim_button(package):
    try:
        picture_works.similarity(package)
        if len(package["list_of_similars"]) > 0:
            len_of_similars = len(package["list_of_similars"])
            package["window"]["-SIMILAR_NUM-"].update(f"Similarities: {len_of_similars}")
            package["window"]["-SIMILAR_BUTTON-"].update(visible=True)
        else:
            package["window"]["-SIMILAR_NUM-"].update("0 (No need to sort)")
        package["done"]["similarity"] = True
    except UnboundLocalError:
        package["window"]["-PROGRESS-"].update("First you have to sort Blurry images out!")


def auto_rotate_button(package):
    if len(package["orientation_checked"]) > 0:
        if sg.popup_yes_no("Do you want to remove last rotated images from the result?") == "Yes":
            picture_works.auto_rotate(package, True)
        else:
            picture_works.auto_rotate(package)
    else:
        picture_works.auto_rotate(package)
def do_it_all_button(package):
    clarity_check_button(package)
    start_sim_button(package)


def save_button(package):
    def save_sorted(image):
        shutil.move(os.path.join(package["root_dir"], image), os.path.join(package["root_dir"], "sorted/" + image))

    def save_trash(image):
        shutil.move(os.path.join(package["root_dir"], image), os.path.join(package["root_dir"], "trash_can/" + image))

    try:
        os.mkdir(os.path.join(package["root_dir"], "sorted"))
    except FileExistsError:
        pass
    try:
        os.mkdir(os.path.join(package["root_dir"], "trash_can"))
    except FileExistsError:
        pass
    for subdir in package["subdirs"]:
        try:
            os.mkdir(os.path.join(package["root_dir"], "sorted/" + subdir))
        except FileExistsError:
            pass
        try:
            os.mkdir(os.path.join(package["root_dir"], "trash_can/" + subdir))
        except FileExistsError:
            pass

    for image in package["list_of_images"]:
        if image in package["chosen_from_similar"] or (
                image in package["ok_list"] + package["unsure_list"] and image not in package["all_similar"]):
            save_sorted(main_functions.get_correct_filename(image))
        else:
            save_trash(main_functions.get_correct_filename(image))

    sg.popup_auto_close("Thank you for using my program!")


# -------------------------------------------MANUAL PIC SORT---------------------------------
def rotate(package):
    image = Image.open(package["root_dir"] + "/" + package["working_images"][package["current_image_number"]])
    image = image.rotate(90, expand=1)
    image.save(package["root_dir"] + "/" + package["working_images"][package["current_image_number"]])
    show_image(package, package["working_images"])


def forward(package):
    if package["current_image_number"] != len(package["working_images"]) - 1:
        package["current_image_number"] += 1
        show_image(package, package["working_images"])


def backward(package):
    if package["current_image_number"] > 0:
        package["current_image_number"] -= 1
        show_image(package, package["working_images"])


def change_img(package):
    if package["current_image_number"] + 1 <= len(package["working_images"]):
        package["current_image_number"] -= 1
        forward(package)
    else:
        backward(package)


# -------------------------------------------SIMILAR PIC CHOOSE---------------------------------

def checkbox_tick(package):
    package["tick_boxes"].update({package["list_of_similars"][package["current_list_number"]]
                                  [package["current_image_number"]]: package["values"]["-CHECKBOX-"]})

def keep_all_button(package):
    for image in package["list_of_similars"][package["current_list_number"]]:
        package["tick_boxes"][image] = package["values"]["-KEEPALL-"]
    main_functions.update_check_box(package)

def slider_change(package):
    package["current_image_number"] = int(package["values"]["-SLIDER-"] - 1)
    jump_to_image(package)
    update_check_box(package)

def keypress_up(package):
    if package["values"]["-SLIDER-"] < len(package["list_of_similars"][package["current_list_number"]]):
        package["window"]["-SLIDER-"].update(package["values"]["-SLIDER-"] + 1)
        package["values"]["-SLIDER-"] += 1
        slider_change(package)

def keypress_down(package):
    if package["values"]["-SLIDER-"] > 1:
        package["window"]["-SLIDER-"].update(package["values"]["-SLIDER-"] - 1)
        package["values"]["-SLIDER-"] -= 1
        slider_change(package)


def next_group(package):
    if package["current_list_number"] < len(package["list_of_similars"]) - 1:
        package["current_list_number"] += 1
        change_group(package)


def previous_group(package):
    if package["current_list_number"] > 0:
        package["current_list_number"] -= 1
        change_group(package)


def autopick(package):
    for sub_list in package["list_of_similars"]:
        max_value = 0
        for image in sub_list:
            if package["blurryness_info"][image] > max_value:
                max_value = package["blurryness_info"][image]
                top_image = image
        package["tick_boxes"][top_image] = True

    for list in package["list_of_similars"]:
        for image in list:
            if package["tick_boxes"][image]:
                package["chosen_from_similar"].append(image)
                break
            else:
                package["to_be_deleted"].append(image)
    package["list_of_similars"] = []
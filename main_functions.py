import os
import unicodedata
import picture_works


def get_correct_filename(file):
    return file.replace("*", "\\")


def strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text) if unicodedata.category(c) != "Mn")

def is_image(picture):
    formats = [".jpg", ".jpeg"]
    fn, fext = os.path.splitext(picture) #filename, file extension
    return str.lower(fext) in formats

def load_pictures(package):
    i = 0
    # na odstranění všech národních znaků z cesty
    while i != len(package["root_dir"]):
        path = ""
        for character in package["root_dir"]:
            if character != "/" and character != "\\":
                path += character
            else:
                path += character
                if i > 3 and path != strip_accents(path):
                    os.rename(path, strip_accents(path))
                    path = strip_accents(path)
            i += 1
        package["root_dir"] = path

    def hledej_subfoldery(cesta):
        relativni_cesta = (cesta.replace(package["root_dir"], "") + "/")

        #Procházení zadané cesty
        for file in os.listdir(cesta):

            # jestli je to obrázek
            if is_image(file):
                if relativni_cesta == "/":
                    relativni_cesta = ""
                package["list_of_images"].append(relativni_cesta + file)

            # jestli je to adresář
            if os.path.isdir(os.path.join(cesta, file)):
                package["subdirs"].append(os.path.join(relativni_cesta, file))
                hledej_subfoldery(os.path.join(cesta, file))

    # Pokud chceme i sub-dirs
    if package["values"]["-INCLUDE_SUBFOLDERS-"]:
        hledej_subfoldery(package["root_dir"])
    # Jen v zadaném adresáři
    else:
        for image in os.listdir(package["root_dir"]):
            if is_image(image):
                package["list_of_images"].append(strip_accents(image))


def auto_rotate(package):
    pass
def update_state_of_pic_sort_message(package):
    ok_list_len = len(package["ok_list"])
    unsure_list_len = len(package["unsure_list"])
    blurry_list_len = len(package["blurry_list"])
    package["window"]["-OK_NUM-"].update(f"OK: {ok_list_len}")
    package["window"]["-UNSURE_NUM-"].update(f"Unsure: {unsure_list_len}")
    package["window"]["-BLURRY_NUM-"].update(f"Blurry: {blurry_list_len}")
    try:
        sim_list_len = len(package["list_of_similars"])
        package["window"]["-SIMILAR_NUM-"].update(f"Similarities: {sim_list_len}")
    except:
        pass

def update_progress_bar(package, num, total, process_name):
    package["window"]["-PROGRESS-"].update(f"Running: {process_name} {num}/{total}")
    package["window"]["-PROG-"].update(num * (1000 / total))
    package["window"].refresh()


def show_image(package, imgs):
    keep_up_count(package, imgs)
    filename = (package["root_dir"] + get_correct_filename(imgs[package["current_image_number"]]))
    img_data, img_size = picture_works.convert_to_bytes(filename, package)
    package["window"]["-IMAGE-"].update(data=img_data)
    package["window"]["-IMAGE-"].set_size((img_size[0], 500))


def keep_up_count(package, imgs):
    package["window"]["-CNUM-"].update(package["current_image_number"] + 1)
    package["window"]["-ANUM-"].update(len(imgs))
    try:
        package["window"]["-SHARPNESS_INFO-"].update(package["blurryness_info"][imgs[package["current_image_number"]]])
    except KeyError:
        pass
    package["window"]["-IMGNAME-"].set_size((len(imgs[package["current_image_number"]]), 1))
    package["window"]["-IMGNAME-"].update(get_correct_filename(imgs[package["current_image_number"]]))


"""-----------SIMILAR_PIC_CHOOSE----------- """


def jump_to_image(package):
    show_image(package, package["list_of_similars"][package["current_list_number"]])
    keep_up_count(package, package["list_of_similars"][package["current_list_number"]])
    package["window"]["-IMGNAME-"].set_size(
        (len(package["list_of_similars"][package["current_list_number"]][package["current_image_number"]]), 1))


def reset_slider(package):
    package["window"]["-SLIDER-"].update(range=(1, len(package["list_of_similars"][package["current_list_number"]])))
    package["window"]["-SLIDER-"].set_size((20, len(package["list_of_similars"][package["current_list_number"]]) * 25))


def change_group(package):
    package["window"]["-CGROUP-"].update(package["current_list_number"] + 1)
    package["window"]["-SLIDER-"].set_size((20, len(package["list_of_similars"][package["current_list_number"]]) * 25))
    package["window"]["-SLIDER-"].update(1)
    package["current_image_number"] = 0
    reset_slider(package)
    update_check_box(package)
    jump_to_image(package)


def update_check_box(package):
    package["window"]["-CHECKBOX-"].update(package["tick_boxes"][
                                               package["list_of_similars"][package["current_list_number"]][
                                                   package["current_image_number"]]])


def integrate_chosen_images(package):
    if len(package["list_of_similars"]) > 0:
        package["to_be_deleted"] = []
        for list in package["list_of_similars"]:
            for image in list:
                if image in package["chosen_from_similar"]:
                    for image in list:
                        if image not in package["chosen_from_similar"]:
                            package["to_be_deleted"].append(image)
                    for image in package["to_be_deleted"]:
                        if image in list:
                            list.pop(list.index(image))
                    if len(list) < 2:
                        package["list_of_similars"].pop(package["list_of_similars"].index(list))
                    break


def sort_manually_ticked_imgs(package):
    for list in package["list_of_similars"]:
        for image in list:
            if package["tick_boxes"][image]:
                package["chosen_from_similar"].append(image)
                if image in package["to_be_deleted"]:
                    package["to_be_deleted"].pop(package["to_be_deleted"].index(image))
            else:
                package["to_be_deleted"].append(image)
            if not package["tick_boxes"][image] and image in package["chosen_from_similar"]:
                package["chosen_from_similar"].pop(package["chosen_from_similar"].index(image))
import cv2
import io
import time
import os
import exifread
import main_functions
import math
from PIL import Image, ImageStat
from skimage.metrics import structural_similarity


def convert_to_bytes(input_image, package):
    """
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    """
    image_cv = cv2.imread(input_image)
    if package["working_images"] == package["rotated"] and package["working_images"] != []:
        for (x, y, w, h) in package["faces"][package["working_images"][package["current_image_number"]]]:
            cv2.rectangle(image_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)
        image_cv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_cv)

    if not "image_pil" in locals():
        image_pil = Image.open(input_image)
    source_width, source_height = image_pil.size
    # Resize process
    new_width, new_height = (1000, 500)
    scale = min(new_height / source_height, new_width / source_width)
    image_pil = image_pil.resize((int(source_width * scale), int(source_height * scale)), Image.ANTIALIAS)
    cur_size = image_pil.size

    bio = io.BytesIO()
    image_pil.save(bio, format="PNG")
    del image_pil
    return bio.getvalue(), cur_size


def blurry(package):
    package["window"]["-PROGRESS-"].update(f"Process: Blurryness 0/" + str(len(package["list_of_images"])))
    num = 0
    start_time = time.time()
    package["blurryness_info"] = dict()
    package["ok_list"] = []
    package["blurry_list"] = []
    package["unsure_list"] = []

    for fotka in package["list_of_images"]:
        num += 1
        total = len(package["list_of_images"])
        real_fotka = main_functions.get_correct_filename(fotka)
        cesta = package["root_dir"] + real_fotka

        # update zprávy a progress baru
        main_functions.update_progress_bar(package, num, total, "Blurryness")

        # čtení fotky v černobílé
        img = cv2.imread(cesta, cv2.IMREAD_GRAYSCALE)

        # Změna velikosti kvůli rychlosti
        img = resize_image(img)


        try: # velmi vzácně některé fotky způsobí při čtení zvláštní error. Nejspíš pokud jsou nějak poškozené...
            # získání hodnoty ostrosti
            blurryness_value = cv2.Laplacian(img, cv2.CV_64F).var()

            if 549 < blurryness_value < 650:
                rozmazanost = "Margin of error"
                package["unsure_list"].append(fotka)
            elif blurryness_value < 550:
                rozmazanost = "Rozmazaný"
                package["blurry_list"].append(fotka)
            else:
                rozmazanost = "V pořádku"
                package["ok_list"].append(fotka)

            package["blurryness_info"][fotka] = round(blurryness_value)
            #print(f"Obrázek {fotka} je {rozmazanost} s hodnotou {blurryness_value}")
            package["window"].refresh()
        except:
            print("ERROR")
    print(f"čas: {round(time.time() - start_time, 2)}s")


def similarity(package):
    package["all_similar"] = []
    package["list_of_similars"] = []
    source_images = [image for image in package["list_of_images"] if image not in package["blurry_list"]]

    start_time = time.time()

    def img_size(img):
        return tuple(img.shape[1::-1])

    def orb_sim(img1, img2):
        orb = cv2.ORB_create()  # dá nám základní body a popíše je

        # Detects keypoints and descriptors
        kp_a, desc_a = orb.detectAndCompute(img1, None)  # Keypoint (kp), descriptors (desc)
        kp_b, desc_b = orb.detectAndCompute(img2, None)

        # define the bruteforce matcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  # použije se na descriptory

        # perform matches
        try:
            matches = bf.match(desc_a, desc_b)

            # Look for similar regions with distance. (Můžu dát od 0 do 100)
            similar_regions = [i for i in matches if i.distance < 60]
            if len(matches) == 0:
                return 0
            return len(similar_regions) / len(matches)
        except:
            print("ORB ERROR")
            return 0
    # Needs images to be same dimensions
    def structural_sim(img1, img2):
        # Kontrola velikosti
        try:
            if img_size(img1) != img_size(img2):
                img2 = cv2.resize(img2, img_size(img1))
            sim, diff = structural_similarity(img1, img2, full=True)
            return sim
        except:
            print("STRUCTURAL ERROR")
            return 0

    def are_these_similar(img1, img2):
        print(img1, img2)
        img1 = cv2.imread(package["root_dir"] + main_functions.get_correct_filename(img1), 0)
        img2 = cv2.imread(package["root_dir"] + main_functions.get_correct_filename(img2), 0)

        img1 = resize_image(img1)
        img2 = resize_image(img2)
        orb_similarity = orb_sim(img1, img2)  # Získá hodnotu podobnsti podle orbů
        struct_similarity = structural_sim(img1, img2)  # Získá hodnotu podobnosti podle structrualní podobnosti
        vysledek = round(orb_similarity + struct_similarity, 2)
        print(f"OrbSim = {orb_similarity}")
        print(f"struct_similarity = {struct_similarity}")
        print(f"Celkem = {vysledek}")
        if vysledek >= 0.9 and orb_similarity >= 0.6:
            return True
        else:
            return False

    i = 1
    total_images = len(source_images)
    pomocny_list = []
    # CHOD FUNKCE
    while len(source_images) > 1:
        i += 1
        main_functions.update_progress_bar(package, i, total_images, "Similarity")
        package["window"].refresh()
        # print(f"Porovnávám {source_images[0]} a {source_images[1]}")
        if are_these_similar(source_images[0], source_images[1]):
            # print("Nalezena podobnost, dávám do Listu")
            pomocny_list.append(source_images.pop(0))
            if len(source_images) == 1:
                # print("Už je tam poeslední obrázek, přidávám a vyhazuju")
                pomocny_list.append(source_images.pop(0))
                package["list_of_similars"].append(list(pomocny_list))
        else:
            # print("Podobnost nenalezena")
            if len(pomocny_list) != 0:
                # print("V Listu něco je, přidávám ho sem a vyhazuju")
                pomocny_list.append(source_images.pop(0))
                # print(List)
                package["list_of_similars"].append(list(pomocny_list))
                pomocny_list = []
            else:
                # print("List je prázdný -> vyhazuju obrazek")
                source_images.pop(0)

    for sub_list in package["list_of_similars"]:
        for image in sub_list:
            package["all_similar"].append(image)
    del pomocny_list, source_images
    print(f"čas: {round(time.time() - start_time, 2)}s")

def auto_rotate(package, remove_last_results=False):
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def rotate(cesta):
        img = Image.open(cesta)
        img = img.rotate(90, expand=1)
        img.save(cesta)

    def process_itself(image, scaleFactor, minNeighbors):
        rotated = False
        full_path = package["root_dir"] + image
        for n in range(4):
            faces = face_cascade.detectMultiScale(cv2.imread(full_path), scaleFactor=scaleFactor, minNeighbors=minNeighbors)

            if len(faces) > 0:
                print(f"V {image} nalezen ksicht, Rotated: ", rotated)
                if rotated:
                    print("Byl otočen strojem, ukládám do rotated")
                    package["faces"].update({image: []})
                    package["rotated"].append(image)
                    for (x, y, w, h) in faces:
                        package["faces"][image].append((x, y, w, h))

                # Code for debugging, tuning face finding. Gives a preview of pic with found face
                """image_cv = cv2.imread(full_path)
                for (x, y, w, h) in faces:
                    cv2.rectangle(image_cv, (x, y), (x + w, y + h), (0, 255, 0), 5)
                image_cv = resize_image(image_cv)
                cv2.imshow("Faces found", image_cv)
                cv2.waitKey(0)
                del image_cv"""

                break
            else:
                rotated = True
                print("otáčím")
                rotate(full_path)

    # Remove last results
    if remove_last_results:
        package["rotated"] = []

    work_images = [image for image in package["ok_list"]+package["unsure_list"] if image not in package["orientation_checked"]+package["rotated"]]

    # Function itself
    for i, image in enumerate(work_images):
        main_functions.update_progress_bar(package, i+1, len(work_images), "Auto-rotate")
        process_itself(image, 1.3, 5)

    # Show buttons and text
    rotated_num = len(package["rotated"])
    package["window"]["-ROTATED_NUM-"].update(f"Rotated: {rotated_num}")
    package["window"]["-ROTATED_BUTTON-"].update(visible=True)

def resize_image(img):
    try:
        if img.shape[0] > 500:
            rate = 1 / (img.shape[0] / 500)
            img = cv2.resize(img, None, fx=rate, fy=rate, interpolation=cv2.INTER_CUBIC)
    except AttributeError:
        print("ATRIBURE ERROR")
    return img

# not yet used funcion -> maybe a calendar of photos?
def day_taken(directory, img1, img2):
    fh1 = open(str(directory + "\\" + img1))
    fh2 = open(str(directory + "\\" + img2))
    tags1 = exifread.process_file(fh1, stop_tag="EXIF DateTimeOriginal")
    tags2 = exifread.process_file(fh2, stop_tag="EXIF DateTimeOriginal")
    fh1.close()
    fh2.close()


def brightness(image):
    im = Image.open(image)
    stat = ImageStat.Stat(im)
    r, g, b = stat.mean
    return math.sqrt(0.241 * (r ** 2) + 0.691 * (g ** 2) + 0.068 * (b ** 2))

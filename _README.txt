To clarify, this is my very first python project, second project in total. I had no previous experiences with none of the functions I used, especially the image work. The code could be written definitely much better, dont judge.


All important data, lists of photos are saved and passed by dict package. Content of package is in file "package.txt".

GUI:
- The whole GUI is written using PySimpleGUI in main().

funcions:
 - similar_pic_choose - opens a window for sorting out photos found as similar
 - manual_pic_sort - mannualy sorting pictures, if they are not sure if they are blurry etc ...

button_functions
core funcions:
 - load_pictures - gets "root_dir", gets all the photos and sub-dirs, starts blurry detection and if user wants, also auto-rotate 
 - save_button - saves the work, in "root_dir" creates new directories "sorted" and "trash_can". To each one, the photos are moved even in the subdirs they were in. No photos are deleted.

main_functions():
-sidefunctions, that dont have theyr own button, just so that main() isnt so crowded

picture_works():
-functions that work the picture magic

    funkce:
        -blurry
            -using opencv library, Laplacian() gets a numeric value of how sharp an image is according to number of sharp edges.
        -similarity
            -library opencv, function ORB_create, creates "orbs" for which it is looking for in the other image I guess
            -library skimage.metrics -> structural_similarity finds similarities in exposure, brightness etc.
            These 2 funcions are used to get the best result possible. Each method gives different result and are accurate in different situations.
        -auto_rotate
            - very not ready and too unnecessarily complicated. Using face-detection.
            - Rotates image 4x by 90°, if it finds a face in the process, it stops, because the photo should be ok. If no face is detected -> image is not changed
        convert_to_bytes - necessary to show images in used GUI. It Has problems showing jpgs.



    
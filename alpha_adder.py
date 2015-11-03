# Bash code to clip name prefixes:
#  let "prefix = <PREFIX>"; 
#  for x in $(ls | grep <PREFIX>); 
#      do mv $x $(echo $x | python -c "print raw_input()[len('$prefix'):]"); 
#  done

import os
import glob

import gimpcolor


WWIU_COLOR = gimpcolor.RGB(1.0, 0.0, 1.0, 1.0)


def convert_png(filename):
    pdb.gimp_context_push()
    
    image = pdb.file_png_load(filename, filename)
    
    pdb.gimp_image_convert_rgb(image)
    
    active_layer = pdb.gimp_image_get_active_layer(image)
    pdb.gimp_layer_add_alpha(active_layer)
    
    pdb.gimp_image_select_color(image, CHANNEL_OP_REPLACE, active_layer, WWIU_COLOR)
    
    pdb.gimp_context_set_foreground(WWIU_COLOR)
    pdb.gimp_edit_bucket_fill(active_layer, FG_BUCKET_FILL, COLOR_ERASE_MODE, 100, 0, False, 0, 0)
    
    pdb.file_png_save_defaults(image, active_layer, filename, filename)
    
    pdb.gimp_context_pop()


def convert_directory(dirpath, regex='*.png'):
    files = glob.glob(os.path.join(dirpath, regex))
    for f in files:
        convert_png(f)


if __name__ == '__main__':
    d = raw_input('Directory to convert: ') or '.'
    convert_directory(d)

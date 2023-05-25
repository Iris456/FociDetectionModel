#In this script the sematic segmentations of the DAPI and 53BP1 channel are combined with the input 53BP1 images into
# images with three channels. The resulting images are the input for the ImageJ macro that does the postprocessing on
# the nuclei segmentations and calculates the foci number and size.


import os
import cv2
from PIL import Image
import numpy as np

def combineIM(path_DAPI_pred, path_foci_pred, path_foci_inp, out_path, name_path):
    # Get a list of all images
    images_DAPI = os.listdir(path_DAPI_pred)
    images_pfoci = os.listdir(path_foci_pred)
    images_ifoci = os.listdir(path_foci_inp)
    images_names = os.listdir(name_path)

    images_DAPI.sort()
    images_pfoci.sort()
    images_ifoci.sort()
    images_names.sort()


    SIZE = 1024

    for i, image_name in enumerate(images_pfoci):
        # read the image, resize the dapi images and combining the in one numpy array
        image = cv2.imread((path_DAPI_pred + images_DAPI[i]), 0)
        image = Image.fromarray(image)
        image = image.resize((SIZE, SIZE))
        image = np.array(image)
        #image = image *255 #If you use 0 and 1 in your predictions. This line can be used to convert it to black and white.
        print('Dp: ', images_DAPI[i])
        image2 = cv2.imread((path_foci_pred + images_pfoci[i]), 0)
        #image2 = image2 * 255 #If you use 0 and 1 in your predictions. This line can be used to convert it to black and white.
        print('Fp: ', images_pfoci[i])
        image3 = cv2.imread((path_foci_inp + images_ifoci[i]), 0)
        print('Fi: ', images_ifoci[i])
        stack = np.dstack((image, image2, image3))

        imname = images_names[i]
        imname = imname.split(".")

        #Convert the 3D np array to an images with three channels and save the image
        fo = Image.fromarray(stack)
        fo.save(out_path+imname[0] + '.tif')

if __name__ == "__main__":
    # Input directories
    path_DAPI_pred = '' #Path to a folder with predictions of sematic DAPI segmentations
    path_foci_pred = '' #Path to a folder with predictions of sematic 53BP1 foci segmentations
    path_foci_inp = '' #Path to a folder with foci input images

    #Note consistent naming should be used in the folders mentioned above because the code is based on the assumption
    # the images are in the same order.

    # Output directory
    path_prediction = ''

    # Run the function to combine the images into a tiff with three channels
    combineIM(path_DAPI_pred, path_foci_pred, path_foci_inp, path_prediction, path_DAPI_pred)


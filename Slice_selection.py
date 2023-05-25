# This script read lif files. Per image stack it selects the image with the highest average intensity in the DAPI
# channel. Subsequently, it saves this DAPI image (and the corresponding EdU image). It then selects the corresponding
# image in the 53BP1 channel, as well as the two adjacent images. It saves the maximum projection of the three 53BP1
# images. The images will be order per channel in a subfolder. The corresponding images will have the same name.

import numpy as np
from readlif.reader import LifFile
from PIL import Image
import os

inp_path = ""  # path to folder with lif files that should be analysed
path = ""  # path to output folder where you want to store the selected slice images
outfile = ['EdU/', 'DAPI/', 'foci/']  # names of subfolders in the output folder where you want to store the (EdU), DAPI
# and 53BP1 foci images
EdUs = True  # Set this to True of you have three channels (EdU, DAPI and foci). Set it to False if you have two channels  (DAPI and foci)


def LIFsliceselection(inp_path, path, outfile, EdUs=True):
    images = os.listdir(inp_path)
    images.sort()

    for image in images:
        if (image.split('.')[1] == 'lif'):  # loop over lif files in folder
            new = LifFile(inp_path + image)  # read lif file
            print(new)
            print(image)
            img_list = [i for i in new.get_iter_image()]
            im = image.split('.')
            all_pos = []

            for n, image in enumerate(img_list):  # loop over image stacks in lif file
                # split channel
                if EdUs == False:
                    z_list = [i for i in image.get_iter_z(t=0, c=1)]  # DAPI channel
                    z_list_foci = [i for i in image.get_iter_z(t=0, c=0)]  # 53BP1 channel
                else:
                    z_list = [i for i in image.get_iter_z(t=0, c=2)]  # DAPI channel
                    z_list_foci = [i for i in image.get_iter_z(t=0, c=1)]  # 53BP1 channel
                    z_list_EdU = [i for i in image.get_iter_z(t=0, c=0)]  # EdU channel
                ave_val = []
                for slice in z_list:  # loop over image in image stack in the DAPI channel and calculate average intesity per image
                    img_array = np.array(slice)
                    ave_val.append(np.mean(img_array))
                pos = np.where(
                    ave_val == np.amax(ave_val))  # Find the dapi image in stack with the highest average intensity
                nul = pos[0]
                if nul[0] != len(ave_val) - 1:
                    # select and save image from DAPI stack with the highest intensity
                    ncl = z_list[nul[0]]
                    filename = im[0] + '_' + str(n) + ".tiff"
                    path_nuclei = path + outfile[1] + filename
                    ncl.save(path_nuclei)

                    if EdUs == True:  # select and save corresponding EdU image from stack
                        EdU = z_list_EdU[nul[0]]
                        path_EdU = path + outfile[0] + filename
                        EdU.save(path_EdU)

                    # select corresponding and adjacent foci images from stack
                    foci = np.zeros((img_array.shape[0], img_array.shape[1], 3))
                    foci[:, :, 0] = z_list_foci[nul[0] - 1]
                    foci[:, :, 1] = z_list_foci[nul[0]]
                    foci[:, :, 0] = z_list_foci[nul[0] + 1]

                    # create maximum projection based on the three selected foci images
                    foc = np.zeros((img_array.shape[0], img_array.shape[1]))
                    for x in range(img_array.shape[0]):
                        for y in range(img_array.shape[1]):
                            all_val = np.array([foci[x, y, 0], foci[x, y, 1], foci[x, y, 2]])
                            foc[x, y] = np.amax(all_val)
                    fo = Image.fromarray(foc)
                    if fo.mode != 'L':
                        fo = fo.convert('L')  # make the image greyscale
                    # save foci maximum projection
                    path_foci = path + outfile[2] + filename
                    fo.save(path_foci)
                all_pos.append(pos[0][0])
            print(all_pos)


LIFsliceselection(inp_path, path, outfile)

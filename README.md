# FociDetectionModel
This project can be used to analyze the foci count in head and neck tumor tissue cultures. This project is the complete pipeline from multi-channel lif files (DAPI and 53BP1 stainings) to csv files with the foci count and properties.

Manual foci analysis is labor intensive and can be influenced by inter observer variability. Available automatic foci analysis tools are often focused on cell cultures and are not usable for tissue cultures because the images are more challenging to automatically analyze. This presented pipeline can be used for automatic foci analysis is tissue culture.

The project exists of multiple steps:
Slice selection: the input is a folder with lif files with multiple multi-channel Z-stacks. The code loops over all lif files in a folder. It opens the lif file and loops over all tiles in the lif file. For each tile, the slice with the highest average intensity is selected from the DAPI channel and saves as a tiff file. The corresponding slices from the 53BP1 channel is selected and a maximum projection is created of that slice and the two adjacent slices. This maximum projection is saved a tiff file.

Prediction: the input is a folder with tiff files of the de DAPI or 53BP1 foci channel. The code loops over the tiffs and predict what the foci and nuclei segmentation would look like. These predictions are save in a different folder.

Combine nuclei foci: the input is a folder with DAPI segment, one with 53BP1 foci segmentations and one with the foci input images. These are combined to one multi-channel image and saved as tiff files.

Foci analysis: this Fiji macro uses the multichannel images of the nuclei and foci segmentation to improve the segmentations of the nuclei (hole filling and size exclusion) and analyze the number of foci and foci properties. These are saved in csv files.

If you have any questions please contact Iris Lauwers: i.lauwers@erasmusmc.nl

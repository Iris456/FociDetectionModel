#This script can be use to create semantic segementation of 53BP1 foci and DAPI channel.

#This code is based on the code of github code of: https://github.com/bnsreenu/python_for_microscopists

import os
import cv2
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, concatenate, Conv2DTranspose, BatchNormalization, Dropout, Lambda
from tensorflow.keras.layers import Activation, MaxPool2D, Concatenate
from tensorflow.keras import backend as K
from PIL import Image


def conv_block(input, num_filters):
    x = Conv2D(num_filters, 3, padding="same")(input)
    x = BatchNormalization()(x)   #Not in the original network.
    x = Activation("relu")(x)

    x = Conv2D(num_filters, 3, padding="same")(x)
    x = BatchNormalization()(x)  #Not in the original network
    x = Activation("relu")(x)

    return x

#Encoder block: Conv block followed by maxpooling
def encoder_block(input, num_filters):
    x = conv_block(input, num_filters)
    p = MaxPool2D((2, 2))(x)
    return x, p

#Decoder block
#skip features gets input from encoder for concatenation
def decoder_block(input, skip_features, num_filters):
    x = Conv2DTranspose(num_filters, (2, 2), strides=2, padding="same")(input)
    x = Concatenate()([x, skip_features])
    x = conv_block(x, num_filters)
    return x

#Build Unet using the blocks
def build_unet(input_shape):
    inputs = Input(input_shape)

    s1, p1 = encoder_block(inputs, 64)
    s2, p2 = encoder_block(p1, 128)
    s3, p3 = encoder_block(p2, 256)
    s4, p4 = encoder_block(p3, 512)

    b1 = conv_block(p4, 1024) #Bridge

    d1 = decoder_block(b1, s4, 512)
    d2 = decoder_block(d1, s3, 256)
    d3 = decoder_block(d2, s2, 128)
    d4 = decoder_block(d3, s1, 64)

    outputs = Conv2D(1, (1, 1), activation="sigmoid")(d4)  #Binary (can be multiclass)

    model = Model(inputs, outputs, name="U-Net")
    return model

def normalize(img):
    min = img.min()
    print(min)
    max = img.max()
    print(max)
    x = 2.0 * (img - min) / (max - min) - 1.0
    return x

def jacard_coef(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (intersection + 1.0) / (K.sum(y_true_f) + K.sum(y_pred_f) - intersection + 1.0)

def jacard_coef_loss(y_true, y_pred):
    return -jacard_coef(y_true, y_pred)

def fol_pred(inp_dic, out_dic, weigths, SIZE):
    IMG_HEIGHT = SIZE
    IMG_WIDTH = SIZE
    IMG_CHANNELS = 1

    #######################################################################
    # Predict on a few images
    model = build_unet([IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS])
    model.load_weights(weigths)

    images = os.listdir(inp_dic)
    images.sort()
    print(images)
    for i, image_name in enumerate(images):
        image = cv2.imread((inp_dic + image_name), 0)
        image = Image.fromarray(image)
        image = image.resize((SIZE, SIZE))
        image = np.array(image)
        test_img_input = np.expand_dims(np.array(normalize((image))),2)
        test_img_other_norm2 = test_img_input[:, :, 0][:, :, None]
        test_img_other_input2=np.expand_dims(test_img_other_norm2, 0)
        pred = (model.predict(test_img_other_input2)[0, :, :, 0] > 0.5).astype(np.uint8)
        pred = pred * 256 #This make the image black and white instead of using zeros and ones.
        pred = Image.fromarray(pred)
        if pred.mode != 'L':
            pred = pred.convert('L')
        path = out_dic + image_name
        pred.save(path)


################################################################################
if __name__ == "__main__":
    #read files
    input_path = ""  #Folder with all input images you want to segment
    output_path = "" #Folder in wich the sematic segementations are saved

    #path to weigths you want to use (note that different weigths should be used for the foci and nuclei segmentations
    final_weigths = ""

    SIZE = 512 #1024 #512 #use 512 for nuclei and 1024 for foci

    #read images as arrays and normalize them and predict
    X_test = fol_pred(input_path, output_path, final_weigths, SIZE)

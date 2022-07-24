# %%

import matplotlib.pyplot as plt
import numpy as np
import time
from PIL import Image
import math
import numpy as np
import json
import pickle
import matplotlib.cm as cm
import PIL.ImageOps
#from libtiff import TIFFfile, TIFFimage
import tifffile

def micronToStep(v):
    #approximately 62nm/step
    return round((v * 1000)/62)

def normalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def annot_max(x,y, ax=None):
    xmax = x[np.argmax(y)]
    ymax = y.max()
    text= "x={:.3f}, y={:.3f}".format(xmax, ymax)
    if not ax:
        ax=plt.gca()
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=60")
    kw = dict(xycoords='data',textcoords="axes fraction",
              arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
    ax.annotate(text, xy=(xmax, ymax), xytext=(0.94,0.96), **kw)


fo = open('saveData2.bin', 'rb')
data = pickle.load(fo)
fo.close()


print("xyStep: ", data['xyStep'])
print("xRange: ", data['xRange'])
print("yRange: ", data['yRange'])
print("zRange: ", data['zRange'])
print("zBase: ", data['zBase'])

dimX = math.ceil(data['xRange'] / data['xyStep'])
dimY = math.ceil(data['yRange'] / data['xyStep'])
print(dimX, dimY)
img = np.zeros((dimX, dimY)).astype('uint16')

zRange = data['zRange']
imgData = data['data']
minValue = 999999999
maxValue = -999999999




for i in range(0, dimX):
    for j in range(0, dimY):
        if type(imgData[i][j]) is np.ndarray:

            try:
                smoothed = moving_average(imgData[i][j], 10)
                height = smoothed.argmax() # / smoothed.shape[0]) * zRange
            except TypeError:
                height = 0

            #if imgData[i][j] is None:
            #    height = 0
            #    print("none", i,j)
            #else:
            #    height = imgData[i][j].argmax()

            img[i][j] = height
            minValue = min(minValue, height)
            maxValue = max(maxValue, height)
            
            #xs = np.linspace(data['zBase'], data['zBase'] + data['zRange'], imgData[i][j].shape[0])
            #plt.plot(xs, imgData[i][j], "o")
            #new_y = moving_average(imgData[i][j], 5)
            #new_x = np.linspace(data['zBase'], data['zBase'] + data['zRange'], new_y.shape[0])
            #plt.plot(new_x, new_y, "-r")
            #annot_max(new_x,new_y)
            #plt.show()
            



print("Min: ", minValue)
print("Max: ", maxValue)


tifffile.imwrite('saveData2.tif', img)




#img -= minValue
#img -= img.min()
#print(img)
#img_normalized = (256*(img - np.min(img))/np.ptp(img)).astype(int)     
#print(img_normalized)

#im = Image.fromarray(np.uint8(img_normalized), 'L')
#im.save("out_big.png")
#im.show()

#final = np.zeros([dimX, dimY], dtype=np.uint16)
#for x, i in enumerate(img):
#    for y, j in enumerate(i):
#        final[x][y] = j
        
#tiff = TIFFimage(final, description='')
#tiff.write_file('saveData3.tif', compression='lzw')




#final = np.zeros([dimX,dimY,3])
#img = normalizeData(img)
#for x, i in enumerate(img):
#    for y, j in enumerate(i):
#        v = cm.BuPu(j)

#        final[x][y][0] = round(v[0] * 256)
#        final[x][y][1] = round(v[1] * 256)
#        final[x][y][2] = round(v[2] * 256)



#im = Image.fromarray(final, 'RGB')
#im = im.rotate(-90)
#im = im.transpose(Image.FLIP_LEFT_RIGHT)


#im = PIL.ImageOps.invert(im)
#im.save("bupu.png")
#im.show()
# %%

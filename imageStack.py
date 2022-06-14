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
    return ((data - np.min(data)) / (np.max(data) - np.min(data))) *  32767

def moving_average(x, w):
    if type(x) is np.ndarray and np.ndim(x) > 0:
        return np.convolve(x, np.ones(w), 'valid') / w
    
    return None

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


fo = open('ccard.bin', 'rb')
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

zRange = data['zRange']
imgData = data['data']
minValue = 999999999
maxValue = -999999999
minLength = 99999





def foo():
        

    for x in range(0, dimX):
        for y in range(0, dimY):
            if type(imgData[x][y]) is np.ndarray:
                    smoothed = moving_average(imgData[x][y], 10)
                    if smoothed is None:
                        print("missing:", x, y)
                        continue
                    minLength = min(minLength, len(smoothed))


    print(dimX, dimY, minLength)

    final = np.zeros((minLength, dimX, dimY)).astype('uint16')


    for x in range(0, dimX):
        for y in range(0, dimY):
            if type(imgData[x][y]) is np.ndarray:
                smoothed = moving_average(imgData[x][y], 10)
                if smoothed is None:
                    smoothed = np.zeros((minLength))
                else:
                    smoothed = normalizeData(smoothed)


                #smoothed = imgData[x][y][0:minLength]
            
                #print("smoothed length: ", len(smoothed))

                #xs = np.linspace(data['zBase'], data['zBase'] + data['zRange'], imgData[x][y].shape[0])
                #plt.plot(xs, imgData[x][y], "o")
                #new_y = moving_average(imgData[x][y], 10)
                #new_x = np.linspace(data['zBase'], data['zBase'] + data['zRange'], new_y.shape[0])
                #plt.plot(new_x, new_y, "-r")
                #annot_max(new_x,new_y)
                #plt.show()


                #xs = np.linspace(0, values.shape[0], values.shape[0])
                #coef = np.polyfit(xs, values, 1)
                #poly1d_fn = np.poly1d(coef)
                #localMax = smoothed.max()
                #threshold = localMax * 0.9
                #if (smoothed.max() < 10000):
                    #xs = np.linspace(data['zBase'], data['zBase'] + data['zRange'], imgData[x][y].shape[0])
                    #plt.plot(xs, imgData[x][y], "o")
                    #new_y = smoothed
                    #new_x = np.linspace(data['zBase'], data['zBase'] + data['zRange'], new_y.shape[0])
                    #plt.plot(new_x, new_y, "-r")
                    #annot_max(new_x,new_y)
                    #plt.show()
                
                # ------ output "local" points  around max point
                localMax = smoothed.argmax()
                rangeMin = max(0,localMax - 10)
                rangeMax = min(minLength, localMax + 10)
                for i in range(rangeMin, rangeMax):
                    value = 32767 - abs(localMax - i) * 500 
                    final[i][x][y] = value
                # ------


                # ------ output binary based on threshold
                #for z in range(0, len(smoothed) - 1):
                    #if (localMax > 7000):
                    #    if (smoothed[z] > threshold):
                    #        final[z][x][y] = 1.0
                    #    else:
                    #        final[z][x][y] = 0
                    #else:
                    #    if smoothed[z] == localMax:
                    #        final[z][x][y] = 1.0
                # ------

                # ------ output full greyscale stack
                #for z in range(0, minLength):
                #    final[z][x][y] = smoothed[z]
                # ------
                
            


    #tifffile.imwrite('stack.tif', final, photometric='minisblack')

    for i in range(0, minLength):
        #tifffile.imwrite('stack\stack' + str(i) + '.tif', final[i], imagej=True, resolution=(1./30., 1./30.),
        #     metadata={'spacing': 1./(1000.0/minLength), 'unit': 'um', 'axes': 'ZXY'})
        tifffile.imwrite('penny_first_local\\' + str(i) + '.tif', final[i], photometric='minisblack')


    print("done")


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

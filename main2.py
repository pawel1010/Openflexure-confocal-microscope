# %%
import openflexure_microscope_client as ofm_client
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

import numpy as np
import time
from math import ceil
from skimage import io, img_as_float, color
import numpy as np
import json
import pickle
from scipy.stats.mstats import winsorize
from timeit import default_timer as timer

def getPinholeIntensity():
    image = io.imread('http://192.168.0.226:5001')
    return np.mean(image)

def micronToStep(v):
    #approximately 62nm/step
    return round((v * 1000)/62)

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


def mm(self, position, measurements, absolute=True):
    """Move the stage to a given position.

    WARNING! If you specify zeros, the stage might move a long way, as
    the default is absolute moves.  Position should be a dictionary
    with keys called "x", "y", and "z", although we will (for now) also
    accept an iterable of three numbers.
    """
    try:
        pos = {k: int(position[k]) for k in ["x", "y", "z"]}
    except:
        pos = {k: int(position[i]) for i, k in enumerate(["x", "y", "z"][:len(position)])}
    pos['absolute'] = absolute
    pos['measurements'] = measurements
    response = self.post_json("/extensions/com.openflexure.stage-mapping/actions/stage/move-measure/MoveMeasureAPI", pos)
    return response

def mz(self, position, absolute=True):
    """Move the stage to a given position.

    WARNING! If you specify zeros, the stage might move a long way, as
    the default is absolute moves.  Position should be a dictionary
    with keys called "x", "y", and "z", although we will (for now) also
    accept an iterable of three numbers.
    """
    try:
        pos = {k: int(position[k]) for k in ["x", "y", "z", "z2"]}
    except:
        pos = {k: int(position[i]) for i, k in enumerate(["x", "y", "z", "z2"][:len(position)])}
    pos['absolute'] = absolute
    response = self.post_json("/extensions/com.openflexure.stage-mapping/actions/stage/move-measure/MeasureZAPI", pos)
    return response

#microscope = ofm_client.find_first_microscope()
microscope = ofm_client.MicroscopeClient("192.168.0.226")
microscope.moveMeasure = mm
microscope.measureZ = mz

# homing routine
pos = microscope.position
print("Current position: " + json.dumps(pos))
print("Homing")
pos['x'] = 0
pos['y'] = 0
pos['z'] = 0
#microscope.move(pos)

#zStep = 20
#maxValue = -1
#maxPosition = -1
#for z in range(micronToStep(-2000), micronToStep(2000), micronToStep(zStep)):
#    pos = microscope.position
#    pos['x'] = 0
#    pos['y'] = 0
#    pos['z'] = z
#    values = microscope.moveMeasure(microscope, pos, 1)
#    #values = [a for a in values if a >= 0 ]
#    values = np.asarray(values)
#    value = np.median(values)
#    if (value > maxValue):
#        maxValue = value
#        maxPosition = z
#    print(value, maxValue, maxPosition)

#print("Final values:", maxValue, maxPosition)


# units in microns
xyStep = 20
xRange = 2000
yRange = 2000
zRange = 400
#zBase = maxPosition - micronToStep(zRange/2)
#zBase = -((30000 - 15000)/2)
zBase = -3926

saveData = {
    "xyStep": xyStep,
    "xRange": xRange,
    "yRange": yRange,
    "zRange": zRange,
    "zBase": zBase,
    "data": [[0] * ceil(xRange/xyStep) for i in range(ceil(yRange/xyStep))],
}

measurements = 1
pos = microscope.position
print("Current position: " + json.dumps(pos))

starting_pos = microscope.position
#figure(figsize=(20,5))

ix = 0
iy = 0

totalElapsed = 0
stepsTaken = 1
maxSteps = (xRange/xyStep) * (yRange/xyStep)
up = True

ix = 0
for x in range(-micronToStep(xRange/2), micronToStep(xRange/2) - micronToStep(xyStep), micronToStep(xyStep)):
    iy = 0
    for y in range(-micronToStep(yRange/2), micronToStep(yRange/2) - micronToStep(xyStep), micronToStep(xyStep)):
        start = timer()
        values = []
        if (up):
            pos = {}
            pos['x'] = x
            pos['y'] = y
            pos['z'] = zBase - micronToStep(zRange/2)
            pos['z2'] = zBase + micronToStep(zRange/2)
            print("Scanning up to position:", pos)

            values = microscope.measureZ(microscope, pos)
            values = np.asarray(values)
            thisTime =  timer() - start
            totalElapsed += thisTime
            up = False
        else:
            pos = {}
            pos['x'] = x
            pos['y'] = y
            pos['z'] = zBase + micronToStep(zRange/2)
            pos['z2'] = zBase - micronToStep(zRange/2)
            print("Scanning to position:", pos)

            values = microscope.measureZ(microscope, pos)
            values = np.asarray(values)
            values = np.flip(values)
            thisTime =  timer() - start
            totalElapsed += thisTime
            up = True



        #xs = np.linspace(zBase - micronToStep(zRange/2), zBase + micronToStep(zRange/2), values.shape[0])
        #coef = np.polyfit(xs, values, 1)
        #poly1d_fn = np.poly1d(coef)
        #plt.plot(xs, values, '-ok')
        #plt.axhline(y=np.median(values), color='r', linestyle='-')
        #plt.xlim(0, values.shape[0])
        #annot_max(xs,values)
        #plt.show()



        print(pos)
        saveData['data'][ix][iy] = values

        iy += 1
        timeLeft = (maxSteps - stepsTaken) * (totalElapsed / stepsTaken) / 60 / 60
        print(">>>>>>>>>>>> Estimated time left: [" + str(timeLeft) + "hr], Per Scan: [" + str(totalElapsed / stepsTaken) + "s][" + str(thisTime) + "], Total Elapsed: [" + str(totalElapsed) + "s], Scans taken: [" + str(stepsTaken) + "] out of: [" + str(maxSteps) + "]")
        stepsTaken += 1
        pickle.dump(saveData, open('saveData.bin', 'wb'))

    ix += 1



pickle.dump(saveData, open('saveData.bin', 'wb'))
#pickle.dump(dataMaxPositions, open('dataMaxPositions.bin', 'wb'))

print("Homing")
pos['x'] = 0
pos['y'] = 0
pos['z'] = 0

microscope.move(pos)

# %%

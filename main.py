# %%
import openflexure_microscope_client as ofm_client
import matplotlib.pyplot as plt
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
    response = self.post_json("/extensions/com.openflexure.stage-mapping/actions/stage/move-measure", pos)
    return response


microscope = ofm_client.find_first_microscope()
microscope = ofm_client.MicroscopeClient("192.168.0.226")
microscope.moveMeasure = mm


# homing routine
pos = microscope.position
print("Current position: " + json.dumps(pos))
print("Homing")
pos['x'] = 0
pos['y'] = 0
pos['z'] = 0
#microscope.move(pos)

zStep = 10
zRange = 1500
maxValue = -1
maxPosition = -1
for z in range(-micronToStep(zRange/2), micronToStep(zRange/2) - micronToStep(zStep), micronToStep(zStep)):
    pos = microscope.position
    pos['x'] = 0
    pos['y'] = 0
    pos['z'] = z
    values = microscope.moveMeasure(microscope, pos, 5)
    values = [a for a in values if a >= 0 ]
    values = np.asarray(values)
    value = np.median(values)
    if (value > maxValue):
        maxValue = value
        maxPosition = z
    print(value, maxValue, maxPosition)

print("Final values:", maxValue, maxPosition)

# units in microns
xyStep = 10
zStep = 5
xRange = 1000
yRange = 1000
zRange = 50
zBase = maxPosition


measurements = 1
measurementTime = 0.012*measurements + 0.169

dataValues = np.zeros((ceil(xRange/xyStep), ceil(yRange/xyStep), ceil(zRange/zStep)))
print(dataValues.shape)

estimatedTime = ((xRange/xyStep) * (yRange/xyStep) * (zRange/zStep) * measurementTime)/60
print("Estimated time:  %5.2f min (%5.2f hours)" % (estimatedTime, estimatedTime / 60))

pos = microscope.position
print("Current position: " + json.dumps(pos))

starting_pos = microscope.position

ix = 0
iy = 0
iz = 0
totalElapsed = 0
stepsTaken = 1
maxSteps = (xRange/xyStep) * (yRange/xyStep) * (zRange/zStep)
for z in range(zBase-micronToStep(zRange/2), zBase+micronToStep(zRange/2) - micronToStep(zStep), micronToStep(zStep)):
    ix = 0
    for x in range(-micronToStep(xRange/2), micronToStep(xRange/2) - micronToStep(xyStep), micronToStep(xyStep)):
        iy = 0
        for y in range(-micronToStep(yRange/2), micronToStep(yRange/2) - micronToStep(xyStep), micronToStep(xyStep)):
            pos = microscope.position
            pos['x'] = x
            pos['y'] = y
            pos['z'] = z
            
            start = timer()
            values = microscope.moveMeasure(microscope, pos, measurements)
            thisTime =  timer() - start
            totalElapsed += thisTime

            # remove negative values
            #values = [a for a in values if a >= 0 ]
            #values = np.asarray(values)
            
            #xs = np.linspace(0, values.shape[0], values.shape[0])
            #coef = np.polyfit(xs, values, 1)
            #poly1d_fn = np.poly1d(coef)
            #plt.plot(xs, values, 'yo', xs)
            #plt.axhline(y=np.median(values), color='r', linestyle='-')
            #plt.xlim(0, values.shape[0])
            #plt.show()


            #value = np.median(values)
            value = values[0]
            print(pos, ix, iy, iz, value, thisTime)
            dataValues[ix][iy][iz] = value
            iy += 1
            timeLeft = (maxSteps - stepsTaken) * (totalElapsed / stepsTaken) / 60 / 60
            print(">>>>>>>>>>>> Estimated time left: [" + str(timeLeft) + "hr], Per Step: [" + str(totalElapsed / stepsTaken) + "s][" + str(thisTime) + "], Total Elapsed: [" + str(totalElapsed) + "s], Steps taken: [" + str(stepsTaken) + "] out of: [" + str(maxSteps) + "]")
            stepsTaken += 1

        ix += 1
        pickle.dump(dataValues, open('dataValues.bin', 'wb'))
    iz += 1    
    
    
pickle.dump(dataValues, open('dataValues.bin', 'wb'))
#pickle.dump(dataMaxPositions, open('dataMaxPositions.bin', 'wb'))

print("Homing")
pos['x'] = 0
pos['y'] = 0
pos['z'] = 0

microscope.move(pos)

# %%

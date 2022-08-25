import logging
from typing import List, Tuple

from labthings import fields, find_component
from labthings.extensions import BaseExtension
from labthings.views import ActionView

from openflexure_microscope.utilities import axes_to_array

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
import collections
from multiprocessing import Process, Pipe

# Create the extension class
class MyExtension(BaseExtension):
    def __init__(self):
        # Superclass init function
        super().__init__("com.openflexure.stage-mapping", version="0.0.0")

        # Add our API Views (defined below MyExtension)
        self.add_view(MeasureZAPI, "/actions/stage/move-measure/MeasureZAPI")
        self.add_view(MoveMeasureAPI, "/actions/stage/move-measure/MoveMeasureAPI")
        self.add_view(MoveStageAPI, "/actions/stage/move-measure/MoveStageAPI")
        self.add_view(ZeroStageAPI, "/actions/stage/move-measure/ZeroStageAPI")

def adcMonitor(conn):
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    ads.gain = 2
    ads.mode = ADS.Mode.CONTINUOUS
    ads.data_rate = 860
    chan = AnalogIn(ads, ADS.P0)

    while True:
        if (conn.recv() == "start"):
            running = True
            buffer = []
            lastValue = 0
            while (running == True):

                # Should we stop?
                if (conn.poll()):
                    if (conn.recv() == "stop"):
                        running = False

                # Get value and make sure it's unique
               	nextValue = chan.value
                if (nextValue != lastValue):
                    buffer.append(chan.value)

            # Send back the ADC readings
            conn.send(buffer)


parent_conn, child_conn = Pipe()
p = Process(target=adcMonitor, args=(child_conn,))
p.start()

class MeasureZAPI(ActionView):
    args = {
        "absolute": fields.Boolean(
            missing=False, example=False, description="Move to an absolute position"
        ),
        "x": fields.Int(missing=0, example=100),
        "y": fields.Int(missing=0, example=100),
        "z": fields.Int(missing=0, example=20),
        "z2": fields.Int(missing=0, example=100),
    }

    def post(self, args):
        """
        Move the microscope stage in x, y, z
        """
        microscope = find_component("org.openflexure.microscope")
        # Handle absolute positioning (calculate a relative move from current position and target)
        if (args.get("absolute")) and (microscope.stage):  # Only if stage exists
            target_position: List[int] = axes_to_array(args, ["x", "y", "z"])
            logging.debug("TARGET: %s", (target_position))
            position: Tuple[int, int, int] = (
                target_position[i] - microscope.stage.position[i] for i in range(3)
            )

            logging.debug("DELTA: %s", (position))

        else:
            # Get coordinates from payload
            position = axes_to_array(args, ["x", "y", "z"], [0, 0, 0])

        # Get second coordinate position
        if (args.get("absolute")) and (microscope.stage):  # Only if stage exists
            target_position: List[int] = axes_to_array(args, ["x", "y", "z2"])
            logging.debug("TARGET: %s", (target_position))
            position2: Tuple[int, int, int] = Tuple(
                target_position[i] - microscope.stage.position[i] for i in range(3)
            )

            logging.debug("DELTA: %s", (position2))

        else:
            # Get coordinates from payload
            position2 = axes_to_array(args, ["x", "y", "z2"], [0, 0, 0])

        logging.debug(position)
        logging.debug(position2)

        # Move if stage exists
        if microscope.stage:
            # Explicitally acquire lock with 1s timeout
            with microscope.stage.lock(timeout=1):
                microscope.stage.move_rel(position)

            # start the measurement
            parent_conn.send("start")
            with microscope.stage.lock(timeout=1):
                microscope.stage.move_rel(position2)
            parent_conn.send("stop")

        else:
            logging.warning("Unable to move. No stage found.")

        return parent_conn.recv()



i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 2
ads.mode = ADS.Mode.SINGLE

chan = AnalogIn(ads, ADS.P0)

class MoveMeasureAPI(ActionView):
    args = {
        "absolute": fields.Boolean(
            missing=False, example=False, description="Move to an absolute position"
        ),
        "x": fields.Int(missing=0, example=100),
        "y": fields.Int(missing=0, example=100),
        "z": fields.Int(missing=0, example=20),
        "measurements": fields.Int(missing=0, example=100),
    }

    def post(self, args):
        """
        Move the microscope stage in x, y, z
        """
        microscope = find_component("org.openflexure.microscope")
        # Handle absolute positioning (calculate a relative move from current position and target)
        if (args.get("absolute")) and (microscope.stage):  # Only if stage exists
            target_position: List[int] = axes_to_array(args, ["x", "y", "z"])
            logging.debug("TARGET: %s", (target_position))
            position: Tuple[int, int, int] = (
                target_position[i] - microscope.stage.position[i] for i in range(3)
            )

            logging.debug("DELTA: %s", (position))

        else:
            # Get coordinates from payload
            position = axes_to_array(args, ["x", "y", "z"], [0, 0, 0])

        logging.debug(position)

        # Move if stage exists
        if microscope.stage:
            # Explicitally acquire lock with 1s timeout
            with microscope.stage.lock(timeout=1):
                microscope.stage.move_rel(position)
        else:
            logging.warning("Unable to move. No stage found.")

        v=[]
        for i in range(0, args['measurements']):
            v.append(chan.value)
            print(v)
        return v

class MoveStageAPI(ActionView):
    args = {
        "absolute": fields.Boolean(
            missing=False, example=False, description="Move to an absolute position"
        ),
        "x": fields.Int(missing=0, example=100),
        "y": fields.Int(missing=0, example=100),
        "z": fields.Int(missing=0, example=20),
    }

    def post(self, args):
        """
        Move the microscope stage in x, y, z
        """
        microscope = find_component("org.openflexure.microscope")

        # Handle absolute positioning (calculate a relative move from current position and target)
        if (args.get("absolute")) and (microscope.stage):  # Only if stage exists
            target_position: List[int] = axes_to_array(args, ["x", "y", "z"])
            logging.debug("TARGET: %s", (target_position))
            position: Tuple[int, int, int] = (
                target_position[i] - microscope.stage.position[i] for i in range(3)
            )
            logging.debug("DELTA: %s", (position))

        else:
            # Get coordinates from payload
            position = axes_to_array(args, ["x", "y", "z"], [0, 0, 0])

        logging.debug(position)

        # Move if stage exists
        if microscope.stage:
            # Explicitally acquire lock with 1s timeout
            with microscope.stage.lock(timeout=1):
                microscope.stage.move_rel(position)
        else:
            logging.warning("Unable to move. No stage found.")

        return microscope.state["stage"]["position"]

class ZeroStageAPI(ActionView):
    def post(self):
        """
        Zero the stage coordinates.
        Does not move the stage, but rather makes the current position read as [0, 0, 0]
        """
        microscope = find_component("org.openflexure.microscope")

        with microscope.stage.lock(timeout=1):
            microscope.stage.zero_position()

        return microscope.state["stage"]

LABTHINGS_EXTENSIONS = (MyExtension,)


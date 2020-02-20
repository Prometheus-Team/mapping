import numpy as np
import math

def worldCoords(width, height):
        hfov_degrees, vfov_degrees = 57, 43
        hFov = math.radians(hfov_degrees)
        vFov = math.radians(vfov_degrees)
        cx, cy = width/2, height/2
        fx = width/(2*math.tan(hFov/2))
        fy = height/(2*math.tan(vFov/2))
        xx, yy = np.tile(range(width), height), np.repeat(range(height), width)
        xx = (xx-cx)/fx
        yy = (yy-cy)/fy
        return list(xx), yy


print(worldCoords(57, 43))
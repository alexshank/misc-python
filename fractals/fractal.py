import svgwrite
import math

# SVG parameters (so image scales to any size)
MIN_SEG_LENGTH = 10  # drawing units, not pixels

# create drawing object that represents entire SVG
dwg = svgwrite.Drawing('test.svg', profile='tiny')


# TODO function for drawing at a specified coordinate
def generateFractalPoints(startPoint, startLength, startDirection, reductionFactor):
    # for cycling through left, right, up, and down directions
    xVals = [1, 0, -1, 0]
    yVals = [0, 1, 0, -1]
    currentVal = 0

    # variables needed for looping
    x = startPoint[0]
    y = startPoint[1]
    fractal_points = [(x, y)]
    iterations = math.floor(
        math.log(MIN_SEG_LENGTH / startLength, reductionFactor))

    # add calculated point to list
    for i in range(0, iterations):
        x = startLength * xVals[currentVal % 4]
        y = startLength * yVals[currentVal % 4]
        fractal_points.append((x, y))
        startLength = math.floor(startLength * reductionFactor)
        currentVal = currentVal + 1

    # return list of fractal points
    return fractal_points


# draw a path through the specified points
def createPathCommand(coordinates, closePath=False):
   # add all coordinates to path
    path_command = 'm'
    for coordinate in coordinates:
        path_command = path_command + \
            str(coordinate[0]) + ',' + str(coordinate[1]) + ' '

    # will make the path a closed shape
    if(closePath):
        path_command = path_command + 'z'
    return path_command


# create an SVG image with fractal designs
if __name__ == "__main__":
    coordinates = generateFractalPoints((240, 240), 500, 'r', 0.80)
    path_command = createPathCommand(coordinates)
    dwg.add(dwg.path(d=path_command,
                     stroke="#F8B195",
                     fill="none",
                     stroke_width=4)
            )
    dwg.save()

from coordinates import Coordinates
import math

class Airfoil:

    # N1 and N2 parameters (N1 = 0.5 and N2 = 1 for airfoil shape)
    N1 = 0.5
    N2 = 1

    # Number of iterations for processing data
    # Max iterations for inner convergence (reaching surfaces)
    maxInnerIterations = 20

    # Max iterations for converging mean camber line
    maxMeanCamberLineIterations = 30

    # Convergence threshold in thickness direction
    thicknessConvergenceThreshold = 0.0001

    # Non-dimensionalized Airfoil
    # @param: name        = name for creation of files this Airfoil is based on
    #         coordinates = Coordinates
    def __init__(self, name, coordinates = None):
        self.name = name

        if (coordinates != None):

            self.coordinates = coordinates

        else:

            self.coordinates = Airfoil.loadCoordinates(name)

    # Save this airfoil's coordinates to a .dat file
    # Use formatting with commas between coordinates
    def saveCoordinates(self):

        # Take all coordinates and format them
        formattedXVals = []
        formattedYVals = []

        for i in range(len(self.coordinates.xVals)):

            formattedXVals.append("{0:.6f}".format(self.coordinates.xVals[i]))
            formattedYVals.append("{0:.6f}".format(self.coordinates.yVals[i]))

        with open("Airfoil/" + self.name + ".dat", "w") as file:

            for i in range(len(formattedXVals)):

                file.write(str(formattedXVals[i]) + "," + str(formattedYVals[i]) + "\n")

            # Add extra line at end to fit past formatting
            file.write(str(formattedXVals[0]) + "," + str(formattedYVals[0]) + "\n")

    # Load a set of airfoil coordinates from a .dat file
    # @param:  name = name of airfoil for .dat file
    # @return: Coordinates
    @staticmethod
    def loadCoordinates(name):

        # Open file
        file = open("Airfoil/" + name + ".dat", "r")

        # Create a new Coordinates object
        coordinates = Coordinates()

        # Add coordinates from file to coordinates object
        # Do not read last line because it is a repeat
        for line in file:

            title = False

            for letter in line:
                if letter.isalpha():
                    title = True

            if not title:

                possibleValues = line.split(" ")

                # Get numbers from line
                values = []

                for possibleValue in possibleValues:
                    if possibleValue != "":
                        values.append(possibleValue)

                # Check if value connected by comma
                if len(values) == 1:
                    values = values[0].split(",")

                # Check if value connected by tab
                if len(values) == 1:
                    values = values[0].split("\t")

                coordinates.addCoordinate(float(values[0]), float(values[1]))

        # If last coordinate is repeat of first coordinate remove it
        if coordinates.xVals[0] == coordinates.xVals[-1]:
            coordinates.xVals.pop()
            coordinates.yVals.pop()

        return coordinates

    # Process an airfoil for characteristics
    # @param:  airfoil               = Airfoil object to be processed
    #          numberChordwisePoints = Integer number of points wanted on chord
    # @return: AirfoilData object
    @staticmethod
    def process(airfoil, numberChordwisePoints):

        # Coordinate values for reference
        xValsRef = airfoil.coordinates.xVals
        yValsRef = airfoil.coordinates.yVals

        # Used to separate lower and upper surfaces
        zeroIndex = -1

        for i in range(len(xValsRef)):

            if xValsRef[i] == 0:
                zeroIndex = i
                break

        # Assign x upper and lower values for reference
        xUpperValsRef = xValsRef[zeroIndex:]
        xUpperValsRef.append(xValsRef[0])
        xLowerValsRef = xValsRef[zeroIndex::-1]

        # Assign y upper and lower values for reference
        yUpperValsRef = yValsRef[zeroIndex:]
        yUpperValsRef.append(yValsRef[0])
        yLowerValsRef = yValsRef[zeroIndex::-1]

        # Upper and lower coordinates for reference
        upperCoordinatesRef = Coordinates(xUpperValsRef, yUpperValsRef)
        lowerCoordinatesRef = Coordinates(xLowerValsRef, yLowerValsRef)

        # Generate x values to output, number given as parameter
        # Equally spaced x values from 0 to 1
        xVals = []

        spacing = 1 / (numberChordwisePoints - 1)

        for i in range(numberChordwisePoints):

            xVals.append(spacing * i)

        # Generate interpolated y values based on reference coordinates
        # Uses linear interpolation to estimate y values in between
        # known reference y values
        yUpperVals = []
        yLowerVals = []

        for i in range(len(xVals)):

            yUpperVals.append(upperCoordinatesRef.interpolate(xVals[i]))
            yLowerVals.append(lowerCoordinatesRef.interpolate(xVals[i]))

        # Create copy of xVals for mean camber line to be refined
        xMeanCamberLineVals = xVals

        # Initial estimate for mean camber line to be refined
        # Uses average of top and bottom surface
        yMeanCamberLineVals = []

        for i in range(len(xVals)):

            yMeanCamberLineVals.append((yUpperVals[i] + yLowerVals[i]) / 2)

        # Initial estimate for upper and lower
        # semi-thicknesses to be refined
        # Uses half difference between top and bottom surface
        # Lower semi-thicknesses are negated so when added to
        # mean camber line it goes down instead
        upperSemiThicknesses = []
        lowerSemiThicknesses = []

        for i in range(len(xVals)):
            upperSemiThicknesses.append((yUpperVals[i] - yLowerVals[i]) / 2)
            lowerSemiThicknesses.append((yLowerVals[i] - yUpperVals[i]) / 2)

        # Boolean if converged on mean camber line
        converged = False

        # How many times the outer loop has run, to see if reached max
        iterations = 0

        while iterations < Airfoil.maxMeanCamberLineIterations and not converged:

            iterations += 1

            # Perpendicular angles from mean camber line
            # Starts with value for beginning
            meanCamberLineAngles = [math.pi / 2]

            # Estimates of upper and lower surface points for current iteration
            # Start with values for beginnings
            xUpperValsEst = [0]
            yUpperValsEst = [0]

            xLowerValsEst = [0]
            yLowerValsEst = [0]

            # For each non-end coordinate on surfaces
            # create new points by going a semi-thickness distance
            # perpendicularly away from the mean camber line
            for i in range(len(xVals) - 2):

                index = i + 1

                # Estimate slope for this point on the mean camber line
                # based on points before and after
                slope = (yMeanCamberLineVals[index + 1] - yMeanCamberLineVals[index - 1]) / (xMeanCamberLineVals[index + 1] - xMeanCamberLineVals[index - 1])

                # Find perpendicular angle to point based on the slope
                angle = math.atan(slope) + (math.pi / 2)
                meanCamberLineAngles.append(angle)

                # Estimate upper and lower surface based on this angle
                xUpperValsEst.append(xMeanCamberLineVals[index] + (upperSemiThicknesses[index] * math.cos(angle)))
                yUpperValsEst.append(yMeanCamberLineVals[index] + (upperSemiThicknesses[index] * math.sin(angle)))

                xLowerValsEst.append(xMeanCamberLineVals[index] + (lowerSemiThicknesses[index] * math.cos(angle)))
                yLowerValsEst.append(yMeanCamberLineVals[index] + (lowerSemiThicknesses[index] * math.sin(angle)))

            # Add end values
            meanCamberLineAngles.append(math.pi / 2)

            xUpperValsEst.append(1)
            yUpperValsEst.append(0)

            xLowerValsEst.append(1)
            yLowerValsEst.append(0)

            # Converge upper and lower surface
            Airfoil.convergeSurface(xUpperValsEst, yUpperValsEst, upperCoordinatesRef, meanCamberLineAngles,
                                    upperSemiThicknesses, xMeanCamberLineVals, yMeanCamberLineVals)
            Airfoil.convergeSurface(xLowerValsEst, yLowerValsEst, lowerCoordinatesRef, meanCamberLineAngles,
                                    lowerSemiThicknesses, xMeanCamberLineVals, yMeanCamberLineVals)

            # Find largest difference between upper and lower semiThicknesses
            # If less then threshold then done converging
            largestDifference = 0

            for i in range(len(upperSemiThicknesses)):

                if abs(upperSemiThicknesses[i] - lowerSemiThicknesses[i]) > largestDifference:

                    largestDifference = abs(upperSemiThicknesses[i] - lowerSemiThicknesses[i])

            if largestDifference < Airfoil.thicknessConvergenceThreshold:
                converged = True

            # Set new mean camber line to be average of
            # of upper and lower surfaces
            for i in range(len(xVals)):
                xMeanCamberLineVals[i] = (xUpperValsEst[i] + xLowerValsEst[i]) / 2
                yMeanCamberLineVals[i] = (yUpperValsEst[i] + yLowerValsEst[i]) / 2

        # Create coordinates for interpolation of mean camber line
        meanCamberLineCoordinates = Coordinates(xMeanCamberLineVals, yMeanCamberLineVals)

        # Find y values on mean camber line for each x value
        yFinalMeanCamberLineVals = []

        for xVal in xVals:

            yFinalMeanCamberLineVals.append(meanCamberLineCoordinates.interpolate(xVal))

        # Create coordinates for interpolation of thicknesses
        thicknessCoordinates = Coordinates()

        # Adding upper and lower semiThicknesses to get thicknesses
        # Lower semiThickness are subtracted because they are negated
        for i in range(len(xVals)):
            thicknessCoordinates.addCoordinate(xMeanCamberLineVals[i], upperSemiThicknesses[i] - lowerSemiThicknesses[i])

        # Find thickness values for each x value
        # Multiplied by 100 to make percentage since chord length is 1
        thicknesses = []

        for xVal in xVals:
            thicknesses.append(abs(100 * thicknessCoordinates.interpolate(xVal)))

        # Find camber percentages by multiplying camber line y values
        # by 100 since chord length is 1
        cambers = []

        for yVal in yFinalMeanCamberLineVals:
            cambers.append(100 * yVal)

        # Find index of maximum thickness and maximum camber
        maxThicknessIndex = 0
        maxCamberIndex = 0

        for i in range(len(xVals)):

            if thicknesses[i] > thicknesses[maxThicknessIndex]:
                maxThicknessIndex = i

            if cambers[i] > cambers[maxCamberIndex]:
                maxCamberIndex = i

        # Return data object with found values
        return AirfoilData(airfoil, xVals, yUpperVals, yLowerVals,
                           yFinalMeanCamberLineVals, thicknesses, cambers,
                           maxThicknessIndex, maxCamberIndex)

    # Converge estimates onto a surface
    # @param: xValsEst = estimated x values to converge
    #         yValsESt = estimated y values to converge
    #         coordinatesRef       = reference coordinates to interpolate on
    #         meanCamberLineAngles = tangent angles to mean camber line
    #         semiThicknesses      = distance from mean camber line to surface
    #         xMeanCamberLinesVals = x values of current mean camber line
    #         yMeanCamberLinesVals = y values of current mean camber line
    @staticmethod
    def convergeSurface(xValsEst, yValsEst, coordinatesRef, meanCamberLineAngles, semiThicknesses,
                        xMeanCamberLinesVals, yMeanCamberLinesVals):

        iteration = 0
        converged = False

        while iteration < Airfoil.maxInnerIterations and not converged:

            iteration += 1

            # Used for perturbance
            dt = 0.0001

            # Find largest delta y value to see if under threshold
            largestDeltaYVal = -math.inf

            # Perturb values and apply gradient to modify semiThickness
            for i in range(len(xValsEst)):

                oldYVal = coordinatesRef.interpolate(xValsEst[i])
                deltaYVal = oldYVal - yValsEst[i]

                # Check if delta y value is larger than largest found
                if deltaYVal > largestDeltaYVal:
                    largestDeltaYVal = deltaYVal

                # Perturb positions slightly
                xValPert = xMeanCamberLinesVals[i] + ((semiThicknesses[i] + dt) * math.cos(meanCamberLineAngles[i]))
                yValPert = yMeanCamberLinesVals[i] + ((semiThicknesses[i] + dt) * math.sin(meanCamberLineAngles[i]))

                # Find change between what y would be on old curve and new y
                oldYValPert   = coordinatesRef.interpolate(xValPert)
                deltaYValPert = oldYValPert - yValPert

                # Gradient
                gradient = (deltaYValPert - deltaYVal) / dt

                # Update semiThickness
                semiThicknesses[i] = semiThicknesses[i] - (deltaYVal / gradient)

                # Update coordinate estimates
                xValsEst[i] = xMeanCamberLinesVals[i] + (semiThicknesses[i] * math.cos(meanCamberLineAngles[i]))
                yValsEst[i] = yMeanCamberLinesVals[i] + (semiThicknesses[i] * math.sin(meanCamberLineAngles[i]))

            # If largest change in a y value is less than threshold
            # then done converging
            if largestDeltaYVal < Airfoil.thicknessConvergenceThreshold:
                converged = True

class AirfoilData:

    # Data for an Airfoil
    # @param: airfoil             = Airfoil this data represents
    #         xVals               = List of x values
    #         yUpperVals          = List of y upper values
    #         yLowerVals          = List of y lower values
    #         yMeanCamberLineVals = List of y values for MCL
    #         thicknesses         = List of thickness as percentages
    #         cambers             = List of camber percentages
    #         maxThicknessIndex   = index for largest thickness
    #         maxCamberIndex      = index for largest camber
    def __init__(self, airfoil, xVals, yUpperVals, yLowerVals, yMeanCamberLineVals, thicknesses, cambers, maxThicknessIndex, maxCamberIndex):
        self.airfoil             = airfoil
        self.xVals               = xVals
        self.yUpperVals          = yUpperVals
        self.yLowerVals          = yLowerVals
        self.yMeanCamberLineVals = yMeanCamberLineVals
        self.thicknesses         = thicknesses
        self.cambers             = cambers
        self.maxThicknessIndex   = maxThicknessIndex
        self.maxCamberIndex      = maxCamberIndex
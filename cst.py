import math
from coordinates import Coordinates
from airfoil import Airfoil

class CST:

    # Create a set of airfoil coordinates using CST (Class-Shape Transformation)
    # parametrization method
    # @param:  weightsLower = list of CST weights for lower surface
    #          weightsUpper = list of CST weights for upper surface
    #          dz           = trailing edge thickness
    #          numVals      = number of unique values to find
    #          xVals        = list of x values to find y values for
    # @return: Coordinates
    @staticmethod
    def genCoordinates(weightsLower, weightsUpper, dz, numVals, xVals=[]):

        if len(xVals) == 0:

            for i in range(numVals):
                zeta = (2 * math.pi / numVals) * i
                xVals.append(0.5 * (math.cos(zeta) + 1))

        # Used to separate lower and upper surfaces
        zeroIndex = -1

        for i in range(numVals):

            if xVals[i] == 0:
                zeroIndex = i
                break

        if zeroIndex == -1:
            raise NameError("No zero value found in x values")

        # Lower and upper values of x
        xValsLower = xVals[:zeroIndex]
        xValsUpper = xVals[zeroIndex:]

        # Find surface y coordinates
        yLowerVals = CST.classShape(weightsLower, dz, xValsLower)
        yUpperVals = CST.classShape(weightsUpper, dz, xValsUpper)

        # Negate y lower values
        for i in range(len(yLowerVals)):
            yLowerVals[i] = -yLowerVals[i]

        # Combine all y values
        yVals = yLowerVals + yUpperVals

        # Return coordinates
        return Coordinates(xVals, yVals)

    # Calculates class and shape functions
    # @param:  weights = list CST weights for
    #          dz      = trailing edge thickness
    #          xVals   = list of x values to find y values for
    # @return: yVals   = list of y values
    @staticmethod
    def classShape(weights, dz, xVals):

        # Class function; taking N1 and N2
        classList = []

        for i in range(len(xVals)):
            classList.append((xVals[i] ** Airfoil.N1) * ((1 - xVals[i]) ** Airfoil.N2))

        # Shape function; using Bernstein Polynomials
        # Order of Bernstein Polynomials
        n = len(weights) - 1

        kVals = []

        for i in range(n + 1):
            kVals.append(math.factorial(n) / (math.factorial(i) * (math.factorial(n - i))))

        shapeList = []

        for i in range(len(xVals)):

            shapeList.append(0)

            for j in range(n + 1):
                shapeList[i] = shapeList[i] + weights[j] * kVals[j] * (xVals[i] ** j) * ((1 - xVals[i]) ** (n - j))

        # Calculate y output
        yVals = []

        for i in range(len(xVals)):
            yVals.append((classList[i] * shapeList[i]) + (xVals[i] * dz))

        return yVals
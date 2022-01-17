class Coordinates:

    # @param: xVals = list of x values
    #         yVals = list of y values
    def __init__(self, xVals = None, yVals = None):
        if xVals is None:
            xVals = []
            yVals = []

        self.xVals = xVals
        self.yVals = yVals

    def addCoordinate(self, xVal, yVal):

        self.xVals.append(xVal)
        self.yVals.append(yVal)

    # Estimate point with linear interpolation
    # Requires ordered coordinates
    # @param:  xVal = number to plug in and estimate y for
    # @return: estimated y value
    def interpolate(self, targetX):

        # Find index of smallest x value that is bigger
        upperBoundIndex = 0

        # Exception for target x being equal to first value
        if targetX == self.xVals[0]:

            upperBoundIndex = 1

        # Exception for x being less than 0
        elif targetX < 0:

            upperBoundIndex = 1

        # Exception for x being greater than 1
        elif targetX > 1:

            upperBoundIndex = len(self.xVals) - 1

        else:

            for i in range(len(self.xVals)):

                if targetX <= self.xVals[i]:

                    upperBoundIndex = i
                    break

        # Upper and lower bound x values
        upperBoundX = self.xVals[upperBoundIndex]
        lowerBoundX = self.xVals[upperBoundIndex - 1]

        # Upper and lower bound y values
        upperBoundY = self.yVals[upperBoundIndex]
        lowerBoundY = self.yVals[upperBoundIndex - 1]

        # Find slope between upper and lower bound x values
        slope = (upperBoundY - lowerBoundY) / (upperBoundX - lowerBoundX)

        # Return y value if there was a line between upper and lower bound
        return lowerBoundY + ((targetX - lowerBoundX) * slope)
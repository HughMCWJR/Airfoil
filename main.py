from airfoil import Airfoil
from cst import CST
import tkinter as tk
import sys
import os
from os import listdir
from os.path import isfile, join

# Possible source for fmincon alternative: https://github.com/xuy/pyipopt
# tkinter type modules may have solution too
# fmincon alternatives would look for local solutions

# Constants
DISPLAY_WIDTH = 30
BUTTON_WIDTH = 15
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 200

# Airfoil being looked at
airfoil = None

# Clear display
def clearDisplay():

    for widget in displayFrame.winfo_children():
        widget.destroy()

# Load airfoil and assign it
# Update label
def loadAirfoil(airfoilName):

    global airfoil

    airfoil = Airfoil(airfoilName)
    airfoilLabel.config(text="Current Airfoil: " + airfoil.name)

# Show buttons for loading airfoils
def displayLoadAirfoil():

    clearDisplay()

    # Save created button widgets
    buttonWidgets = []

    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    # See possible airfoils to load
    path = os.path.join(application_path, 'Airfoil/')
    onlyFiles = [f for f in listdir(path) if isfile(join(path, f))]

    # Load and pack airfoil frame widgets
    for file in onlyFiles:

        # Check file is a .dat file
        if file[-4:] == ".dat":

            buttonWidgets.append(tk.Button(text=file[:-4], master=displayFrame, width=DISPLAY_WIDTH,
                                           command=lambda file=file: loadAirfoil(file[:-4])))
            buttonWidgets[-1].pack()

# Save airfoil at given file if exists
def saveAirfoil(airfoilName):

    global airfoil

    if airfoil is not None and len(airfoilName) != 0:
        airfoil = Airfoil(airfoilName, airfoil.coordinates)
        airfoilLabel.config(text="Current Airfoil: " + airfoil.name)

        airfoil.saveCoordinates()

# Show display for saving current airfoil
def displaySaveAirfoil():

    clearDisplay()

    # Entry for typing name of file for airfoil to be saved to
    airfoilNameEntry = tk.Entry(width=DISPLAY_WIDTH, master=displayFrame)
    airfoilNameEntry.pack()

    # Button to save airfoil at file
    airfoilSaveButton = tk.Button(text="Save", width=DISPLAY_WIDTH, master=displayFrame,
                                  command=lambda: saveAirfoil(airfoilNameEntry.get()))
    airfoilSaveButton.pack()

# Draw an airfoil
# @param: canvas object to draw on to
def drawAirfoil(canvas):

    # Clear canvas
    canvas.delete("all")

    if airfoil is not None:

        for i in range(len(airfoil.coordinates.xVals)):

            # Translate coordinate to canvas coordinates
            canvasXVal = CANVAS_WIDTH * airfoil.coordinates.xVals[i]
            canvasYVal = (CANVAS_HEIGHT * (-airfoil.coordinates.yVals[i])) + (CANVAS_HEIGHT / 2)

            # Convert coordinates to opposite corners of circle to draw
            # Make circle have diameter equal to canvas width / 100
            radius = CANVAS_WIDTH / 200
            coord = canvasXVal - radius, canvasYVal - radius, canvasXVal + radius, canvasYVal + radius

            # Draw circle at location
            canvas.create_arc(coord, start=0, extent=359, fill="black", outline="")

# Draw the mean camber line
# @param: canvas object to draw on to
def drawMeanCamberLine(canvas, data):

    if data is not None:

        for i in range(len(data.yMeanCamberLineVals)):

            # Translate coordinate to canvas coordinates
            canvasXVal = CANVAS_WIDTH * data.xVals[i]
            canvasYVal = (CANVAS_HEIGHT * (-data.yMeanCamberLineVals[i])) + (CANVAS_HEIGHT / 2)

            # Convert coordinates to opposite corners of circle to draw
            # Make circle have diameter equal to canvas width / 100
            radius = CANVAS_WIDTH / 200
            coord = canvasXVal - radius, canvasYVal - radius, canvasXVal + radius, canvasYVal + radius

            # Draw circle at location
            canvas.create_arc(coord, start=0, extent=359, fill="red", outline="")

# Show display for drawing airfoil
def displayAirfoilInformation():

    clearDisplay()

    # Draw airfoil
    airfoilCanvas = tk.Canvas(bg="white", height=CANVAS_HEIGHT, width=CANVAS_WIDTH, master=displayFrame)
    drawAirfoil(airfoilCanvas)
    airfoilCanvas.pack()

    # Get data on airfoil
    # Require number of coordinates equal to current amount
    data = Airfoil.process(airfoil, len(airfoil.coordinates.xVals))

    # Give user option to draw mean camber line
    meanCamberLineButton = tk.Button(text="Draw Mean Camber Line", master=displayFrame, width=DISPLAY_WIDTH,
                                     command=lambda: drawMeanCamberLine(airfoilCanvas, data))
    meanCamberLineButton.pack()

    # Display information
    tk.Label(
        text="Max Thickness " + str("{0:.2f}".format(data.thicknesses[data.maxThicknessIndex])) + "% at " +
        str("{0:.2f}".format(100 * data.maxThicknessIndex / len(data.xVals))) + "% chord",
        width=DISPLAY_WIDTH, master=displayFrame).pack()
    tk.Label(
        text="Max Camber " + str("{0:.2f}".format(data.cambers[data.maxCamberIndex])) + "% at " +
        str("{0:.2f}".format(100 * data.maxCamberIndex / len(data.xVals))) + "% chord",
        width=DISPLAY_WIDTH, master=displayFrame).pack()

    # print(data.thicknesses[data.maxThicknessIndex])
    # print(data.maxThicknessIndex)
    # print(data.cambers[data.maxCamberIndex])
    # print(data.maxCamberIndex)

# Show display for editing airfoil
def displayEditAirfoil():

    clearDisplay()

    # TEST
    # Button to save airfoil at file
    testButton = tk.Button(text="TEST", width=DISPLAY_WIDTH, master=displayFrame)
    testButton.pack()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    #weightsLower = [0.102333995082718,0.138209581186333,0.049306525213022,-0.082982724998046]
    #weightsUpper = [0.164917727527345,0.320594819913800,0.203199258463692,0.297424182497028]

    #dz = 0

    #numVals = 66

    #xVals = [1,0.996280000000000,0.985230000000000,0.967149000000000,0.942419000000000,0.911508000000000,0.874947000000000,0.833447000000000,0.787766000000000,0.738715000000000,0.687134000000000,0.633893000000000,0.579832000000000,0.525760000000000,0.472439000000000,0.420578000000000,0.370477000000000,0.322126000000000,0.275695000000000,0.231455000000000,0.189764000000000,0.151143000000000,0.116072000000000,0.0850020000000000,0.0583510000000000,0.0364210000000000,0.0193900000000000,0.00954000000000000,0.00422000000000000,0.00175000000000000,0.000520000000000000,9.00000000000000e-05,0,0.000340000000000000,0.00152000000000000,0.00468000000000000,0.00619000000000000,0.0160300000000000,0.0302810000000000,0.0488510000000000,0.0715910000000000,0.0982920000000000,0.128633000000000,0.162303000000000,0.198944000000000,0.238185000000000,0.279606000000000,0.322776000000000,0.367427000000000,0.413418000000000,0.460549000000000,0.508600000000000,0.557221000000000,0.605902000000000,0.654083000000000,0.701214000000000,0.746685000000000,0.789936000000000,0.830367000000000,0.867427000000000,0.900588000000000,0.929358000000000,0.953279000000000,0.972329000000000,0.986860000000000,0.996520000000000]

    #airfoil = Airfoil("CSTtext", CST.genCoordinates(weightsLower, weightsUpper, dz, numVals, xVals))

    #for i in range(len(xVals)):

        #print(airfoil.coordinates.yVals[i])

    #data = Airfoil.process(airfoil, 51)

    #print(data.thicknesses[data.maxThicknessIndex])
    #print(data.maxThicknessIndex)
    #print(data.cambers[data.maxCamberIndex])
    #print(data.maxCamberIndex)

    #for i in range(len(data.xVals)):
        #print(str(data.xVals[i]) + "/" + str(data.thicknesses[i]))
        #print(str(data.yUpperVals[i]) + " and " + str(data.yLowerVals[i]))
        #print(str(data.xVals[i]) + "/" + str(data.cambers[i]))

    # Create global widgets
    global displayFrame
    global airfoilLabel

    # Create window
    window = tk.Tk()

    # Create widgets
    airfoilLabel = tk.Label(text="Current Airfoil: ")

    # Create display frame for information
    # Add default widget to fill space
    displayFrame = tk.Frame()
    defaultLabel = tk.Label(text="Click a button on the left.", width=DISPLAY_WIDTH, master=displayFrame)

    buttonFrame = tk.Frame()
    buttons = []
    buttons.append(tk.Button(master=buttonFrame, text="Load Airfoil", command=displayLoadAirfoil, width=BUTTON_WIDTH))
    buttons.append(tk.Button(master=buttonFrame, text="Save Airfoil", command=displaySaveAirfoil, width=BUTTON_WIDTH))
    buttons.append(tk.Button(master=buttonFrame, text="Airfoil Information", command=displayAirfoilInformation,
                             width=BUTTON_WIDTH))
    buttons.append(tk.Button(master=buttonFrame, text="Edit Airfoil", command=displayEditAirfoil,
                             width=BUTTON_WIDTH))

    # Pack widgets
    airfoilLabel.pack()
    buttonFrame.pack(side=tk.LEFT)
    for button in buttons:
        button.pack()
    displayFrame.pack(side=tk.RIGHT)
    defaultLabel.pack()

    # Initiate main loop
    window.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

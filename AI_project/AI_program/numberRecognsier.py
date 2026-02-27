import time
import random
import os
import sys
import math

from PIL import Image
import numpy as np
import cupy as cp
print("libraries imported")

#chooses a random item from an array
def RandomFromArray(array):
    choice = random.randint(0, len(array) - 1)
    item = array[choice]
    return item

#gets the path of the folder
pathSteps = __file__.split("\\")

pathSteps.pop(len(pathSteps) - 1)
        
path = ""
for step in pathSteps:
    if step != pathSteps[len(pathSteps) - 1]:
            path = path + step + "\\"
    else:
        path = path + step

#creates an array of all available folders
folders = os.listdir(path)

for item in folders:
    if '.' in item:
        folders.remove(item)

#returns the chosen image as a matrix and the correct matrix alongside it
def getRandomInputs():

    #picks a random folder
    folder = RandomFromArray(folders)
    folderPath = path + "\\" + folder

    #creates the correct matrix using the folder
    correctMatrix = cp.zeros((1, 10))
    try:
        folderInt = int(folder)
        correctMatrix[0][folderInt] = 1

    except ValueError:
        print("error in initialising folders, likely that an additional folder is polluting the selection")
        raise ValueError
    
    #picks a random image
    image = RandomFromArray(os.listdir(folderPath))
    imagePath = folderPath + "\\" + image
    print(folder)

    openImage = Image.open(imagePath)

    #the maths to calculate the cropping box
    #cropping box paramaters are (topleft.x, topleft.y, bottomright.x, bottomright.y)
    height = openImage.height
    width = openImage.width

    if height > width:
        yDiff = height - width
        yDiff = yDiff / 2
        box = (0, yDiff, width, width + yDiff)

    else:
        xDiff = width - height
        xDiff = xDiff / 2
        box = (xDiff, 0, height + xDiff, height)

    #the cropping, downgrading and greyscaling of the image
    openImage = openImage.crop(box)
    openImage.thumbnail((15, 15), resample=Image.Resampling.NEAREST)
    openImage = openImage.convert("L") 

    #creates the input matrix
    inputMat = cp.array(openImage)
    inputMat = inputMat / 255

    return inputMat, correctMatrix

def leakyRelU(mat):
    preAccs.append(mat)
    mat = cp.where(mat > 0, mat, mat * 0.01)
    postAccs.append(mat)
    return mat

def softMax(mat):
    preAccs.append(mat)
    mat = cp.exp(mat - cp.max(mat))
    mat = mat / cp.sum(mat)
    postAccs.append(mat)
    return mat

def calculateLoss(predicted, correct):
    lossMat = -(correct * cp.log(predicted))
    return cp.sum(lossMat)

def networkIsCorrect(predicted, correctMat):
    return cp.argmax(predicted) == cp.argmax(correctMat)

#forward propogates through the network automatically with the layers added
def forwardPropogate(input):
    for i in range(0, len(weights)):
        input = cp.dot(input, weights[i])
        input = input + biases[i]

        if i == len(weights) - 1:
            input = softMax(input)

        else:
            input = leakyRelU(input)

        if i == len(weights) - 2:
            global preFlatten
            preFlatten = cp.shape(input)

            input = cp.reshape(input, (1, cp.size(input)))
            postAccs.pop()
            postAccs.append(input)

    return input

def delta(predicted, correct):
    deltas = []
    outputError = predicted - correct
    deltas.append(outputError)

    for i in range(len(weights) - 1, 0, -1):
        weight = weights[i]
        preActivation = preAccs[i - 1]
        nextError = deltas[0]
        dotProduct = cp.dot(nextError, weight.T)

        if cp.shape(dotProduct)[0] == 1:
            dotProduct = cp.reshape(dotProduct, preFlatten)

        layerDelta = dotProduct * np.where(preActivation > 0, 1.0, 0.01)
        deltas.insert(0, layerDelta)
    return deltas
        
def updateLayers(deltas):
    for i in range(len(weights) -1, -1, -1):
        postActivation = postAccs[i]
        delta = deltas[i]

        weightChange = cp.dot(postActivation.T, delta) * learningRate
        weights[i] = weights[i] - weightChange

        biasChange = cp.sum(delta, axis=0) * learningRate
        biases[i] = biases[i] - biasChange



learningRate = 0.01

global weights
weights = []

global biases
biases = []

global preAccs
preAccs = []

global postAccs
postAccs = []

#creates a new layer for the network.
#initialises the weight with He init and the bias as a zero matrix
def addLayer(rows, columns):
    weight = cp.random.randn(rows, columns) * math.sqrt(2 / rows)
    bias = cp.zeros((1, columns))

    weights.append(weight)
    biases.append(bias)

addLayer(15,15)
addLayer(15,15)
addLayer(15, 15)
addLayer(15,15)
addLayer(15,15)
addLayer(15,15)
addLayer(225,10)

#training loop
while True:

    approved = False
    while not approved:
        try:
            trainingAmount = int(input("how many times would you like to train?: "))
            approved = True
        except ValueError:
            print("please enter an integer value")

    correct = 0
    attempts = 0
    for i in range(trainingAmount):
        inputMat, correctMat = getRandomInputs()

        preAccs = []
        postAccs = [inputMat]

        predicted = forwardPropogate(inputMat)
        loss = calculateLoss(predicted, correctMat)
        print("loss:", loss)
        print("----------------")

        if networkIsCorrect(predicted, correctMat):
            correct = correct + 1
        attempts = attempts + 1

        deltas = delta(predicted, correctMat)
        updateLayers(deltas)


    accuracy = (correct / attempts) * 100
    accuracy = round(accuracy, 2)
    print("the accuracy of the network is: " + str(accuracy) + "%")
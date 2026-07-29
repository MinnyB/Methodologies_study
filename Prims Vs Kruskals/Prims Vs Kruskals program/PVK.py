import mouse
import tkinter as tk
import keyboard
import randomcolor
import copy

window = tk.Tk()
window.geometry("1400x700+55+50")
window.title("MST demonstration")

canvas = tk.Canvas(window, background="white")
canvas.pack(fill="both", expand=True)

#informative labels in the top left of the screen
tk.Label(text="press K to run Kruskal's MST", background="white").place(x=0, y=0)
tk.Label(text="press P to run Prim's MST", background="white").place(x=0, y=20)
tk.Label(text="press S to save the current screen", background="white").place(x=0, y=50)
tk.Label(text="press L to load the saved screen", background="white").place(x=0, y=70)
tk.Label(text="press C to clear the screen", background="white").place(x=0, y=90)


#additional labels used to tell the user to advance forwards through algorithms or select a starting node
#they are only set to a value when they are needed
advanceLabel = None
startingNodeLabel = None

#stores information about each circular node on the screen
class node:
    def __init__(self, relPos):
        self.position = relPos

#used when handling nodes on the screen, will check if the mouse is on the screen before placing the node as to not cause errors
def mouseIsInScreen(mousePos, positions, size):

    #guard clause to not place nodes if the tkinter window is not the top window
    if(window != window.focus_displayof()):
        return False
    
    #checking left and right
    if not (positions[0] < mousePos[0] < positions[0] + size[0]):
        return False
    
    #checking up and down
    if not (positions[1] < mousePos[1] < positions[1] + size[1]):
        return False
    
    return True

radius = 50 #the base radius without scaling of a node when at a resolution of 1400x700
currentNodes = [] #all nodes currently on the screen
connections = [] #all connections between nodes and their distance
selectedNode = None #the current node that has been selected with a right click

#used when selecting nodes via a right click
def selectNode():

    #position and size of the window
    positions = (window.winfo_x(), window.winfo_y())
    size = (window.winfo_width(), window.winfo_height())
    
    #gets the mouse position
    mousePos = mouse.get_position()
    mousePos = (mousePos[0] - 7, mousePos[1] - 30) #shifted slightly, as the mouse position is always off somewhat

    #returns if the mouse is not in the screen
    if not mouseIsInScreen(mousePos, positions, size):
        return

    #will only allow nodes to be selected if the algorithms are not running
    if runningKruskals or (runningPrims and len(visitedNodes) > 0):
        return
        
    #calculates what the circle radius should be and gets the screen bounds for calculating the nodes relative position
    bounds, scaledRadius = getScreenSize(size)
        
    #calculates the position of the mosue on the screen to compare to the node
    screenMousePos = ( (mousePos[0] - positions[0]), (mousePos[1] - positions[1]) )

    #loops through all nodes and checks their distance from the mouse, if the mouse is within the nodes radius then it is considered clicked on
    global selectedNode
    clickedNode = None
    for node in currentNodes:
        nodePos = getNodeScreenPos(bounds, node)

        Xdistance = nodePos[0] - screenMousePos[0]
        Ydistance = nodePos[1] - screenMousePos[1]

        distance =  ((Xdistance ** 2) + (Ydistance ** 2)) ** 0.5
        
        if distance < scaledRadius:
            clickedNode = node

    #if no node is clicked on, reset the selected node
    if clickedNode == None:
        selectedNode = None
    
    #if a node is clicked on and a node is already selected, connect them together
    if selectedNode != None:
        clickedPos = clickedNode.position
        selectedPos = selectedNode.position

        Xdistance = clickedPos[0] - selectedPos[0]
        Ydistance = clickedPos[1] - selectedPos[1]

        distance =  ((Xdistance ** 2) + (Ydistance ** 2)) ** 0.5

        toAdd = [clickedNode, selectedNode, distance]

        #this if statement confirms that the connection is not already in the connections array from one node to another both ways
        if not toAdd in connections and not [selectedNode, clickedNode, distance] in connections:
            connections.append(toAdd)

        selectedNode = None

    #if a node is clicked on and no node is selected, select that node
    else:
        selectedNode = clickedNode

    #logic that allows for a starting node to be picked in Prim's
    if runningPrims:
        visitedNodes.append(selectedNode)
        selectedNode = None

        resize(None)

        global advanceLabel, startingNodeLabel
        advanceLabel = tk.Label(text="press right arrow to advance Prim's", background="white", foreground="red")
        advanceLabel.place(x=0, y=150)

        startingNodeLabel.destroy()
                
    resize(None)
            
        
        
def placeNode():
    mousePos = mouse.get_position()
    mousePos = (mousePos[0] - 7, mousePos[1] - 30) #shifted slightly, as the mouse position is always off somewhat

    #position and size of the window
    positions = (window.winfo_x(), window.winfo_y())
    size = (window.winfo_width(), window.winfo_height())

    #returns if the mouse is not in the screen
    if not mouseIsInScreen(mousePos, positions, size):
        return

    #will only allow nodes to be placed if the algorithms are not running
    if runningKruskals or runningPrims:
        return
    
    #calculates what the circle radius should be and gets the screen bounds for calculating the nodes relative position
    bounds, scaledRadius = getScreenSize(size)
    
    #calculates the relative position of a node on the screen bounds - creating a new node by using it
    relativeMousePos = ( (mousePos[0] - (positions[0] + bounds[0])), (mousePos[1] - (positions[1] + bounds[1])) )
    boundWidth = (bounds[2] - bounds[0])
    boundHeight = (bounds[3] - bounds[1])

    #clamps the two positions to be in between 0.95 and 0.05
    relx = max(0.05, min(relativeMousePos[0] / boundWidth, 0.95))
    rely = max(0.05, min(relativeMousePos[1] / boundHeight, 0.95))

    newNode = node( (relx, rely) )
    currentNodes.append(newNode)

    resize(None)
#used in scaling, will output the biggest rectangle that can be made on the screen that is of 2:1 aspect ratio    
def getScreenSize(size):
    aspectRatio = size[0] / size[1]
    newScreenBounds = (0, 0, size[0], size[1]) #initially set to the window size

    #if the height of the screen is greater than the width
    if(aspectRatio > 2): 

        #calculates the largest width of the box that is possible whilst keeping it at a 2:1 ratio
        newWidth = 2 * size[1]
        distanceX = (size[0] - newWidth) / 2
        newScreenBounds =  (distanceX, 0, size[0] - distanceX, size[1]) 

    #if the width of the screen is greater than the height
    if(aspectRatio < 2):

        #calculates the largest height of the box that is possible whilst keeping it at a 2:1 ratio
        newHeight = 0.5 * size[0]
        distanceY = (size[1] - newHeight) / 2
        newScreenBounds =  (0 , distanceY, size[0], size[1] - distanceY)

    #scales the radius by checking the width of the box and dividing it by 1400 - the starting width of the window
    scaledRadius = radius * ((newScreenBounds[2] - newScreenBounds[0]) / 1400)

    return newScreenBounds, scaledRadius

#used to get the position of the node in the bounds of the screen
def getNodeScreenPos(newScreenBounds, node):

    #calulates the width / height of the bounding box by taking the lowest x / y position away from the highest
    screenWidth = newScreenBounds[2] - newScreenBounds[0]
    screenHeight = newScreenBounds[3] - newScreenBounds[1]

    #finds the relative position of the node on the box
    Xposition = newScreenBounds[0] + (screenWidth * node.position[0]) 
    Yposition = newScreenBounds[1] + (screenHeight * node.position[1])

    return (Xposition, Yposition)

#runs every time the canvas is configured (resized)
def resize(self):
    canvas.delete("all") #deletes all current nodes

    size = (window.winfo_width(), window.winfo_height())

    newScreenBounds, scaledRadius = getScreenSize(size)

    #draws the lines between every node in the connections array
    #this must be done before placing nodes to ensure that nodes are placed above the lines
    for connection in connections:

        #ensures that the MST starts with no connections and only places the ones that have been visited in an algorithm
        if runningKruskals or runningPrims:
            if not connection in visited:
                continue

        nodePos1 = getNodeScreenPos(newScreenBounds, connection[0])
        nodePos2 = getNodeScreenPos(newScreenBounds, connection[1])

        #will highlight the connection in the highlightedConnection variable
        if len(highlightedConnection) == 2:
            if connection == highlightedConnection[0]:
                canvas.create_line(nodePos1[0], nodePos1[1], nodePos2[0], nodePos2[1], fill=highlightedConnection[1], width=3)
                continue
        
        canvas.create_line(nodePos1[0], nodePos1[1], nodePos2[0], nodePos2[1])
    
    for node in currentNodes:

        nodePos = getNodeScreenPos(newScreenBounds, node)
        Xposition = nodePos[0]
        Yposition = nodePos[1]

        #creates the new node, changing its colour depending on may situations
        if node == selectedNode: #yellow if selected
            canvas.create_oval(Xposition + scaledRadius,
                            Yposition + scaledRadius,
                            Xposition - scaledRadius,
                            Yposition - scaledRadius,
                            fill="yellow"
                            )
        elif runningKruskals: #colour of the group if Kruskal's is running
            canvas.create_oval(Xposition + scaledRadius,
                            Yposition + scaledRadius,
                            Xposition - scaledRadius,
                            Yposition - scaledRadius,
                            fill=groupColours[groups[node]]
                            )
        elif runningPrims and node in visitedNodes: #light gray if Prim's is running and node has veen visited
            canvas.create_oval(Xposition + scaledRadius,
                                        Yposition + scaledRadius,
                                        Xposition - scaledRadius,
                                        Yposition - scaledRadius,
                                        fill="#dcdcdc"
                                        )
        else: #white if none of the other situations
            canvas.create_oval(Xposition + scaledRadius,
                            Yposition + scaledRadius,
                            Xposition - scaledRadius,
                            Yposition - scaledRadius,
                            fill="white"
            )

    #may be removed later, used to show the bounds of the screen for debugging
    canvas.create_rectangle(newScreenBounds[0], newScreenBounds[1], newScreenBounds[2], newScreenBounds[3])

runningKruskals = False 
connectionIndex = 0 #stores the current connection that Kruskal's is on when looping through them all
groups = {} #stores every node and the group they are a part of
groupColours = {} #stores every group and the colour that matches it

#starts the process of Kruskal's
def initKruskals():
    global runningKruskals, runningPrims, connectionIndex, advanceLabel

    if runningPrims or len(connections) == 0: 
        return

    #sorts the connections in ascending order
    connections.sort(key= lambda x: x[2])
    print(connections)

    runningKruskals = True

    #sets every node to an initial group
    for i in range(len(currentNodes)):
        currentNode = currentNodes[i]
        groups[currentNode] = i

    #gives every group a random colour
    for node in groups:
        rand = randomcolor.RandomColor()
        groupColours[groups[node]] = rand.generate()

    advanceLabel = tk.Label(text="press right arrow to advance Kruskal's", background="white", foreground="red")
    advanceLabel.place(x=0, y=150)

    stepKruskals()

runningPrims = False
visitedNodes = [] #stores any nodes that have become part of the MST already

#starts the process of Prim's
def initPrims():
    global runningPrims, runningKruskals, startingNodeLabel

    if runningKruskals or len(connections) == 0:
        return

    startingNodeLabel = tk.Label(text="Select a starting node", background="white", foreground="red")
    startingNodeLabel.place(x=0, y=150)
    
    runningPrims = True

highlightedConnection = [] #stores the current connection that is highlighted alongside its colour
visited = [] #stores all connections that have become part of the tree

#progresses Kruskal's algorithm
def stepKruskals():
    global highlightedConnection, connectionIndex, runningKruskals, visited

    #gets the two nodes in the connection
    connection = connections[connectionIndex]
    node1 = connection[0]
    node2 = connection[1]

    # UNION-FIND

    #if two nodes are the same group, the connection would fornm a cycle and the connection is highlighted red
    if groups[node1] == groups[node2]:
        highlightedConnection = [connection, "red"]

    #if two nodes are not in the same group the connection would not form a cycle and the connection is highlighted green
    if groups[node1] != groups[node2]:
        highlightedConnection = [connection, "green"]

        #sets any instances of a node with the group of the first node to the group of the second node
        toChange = groups[node1]
        for node in groups:
            if groups[node] == toChange:
                groups[node] = groups[node2]

    visited.append(connection)
    connectionIndex += 1

    resize(None)

#progresses Prim's algorithm
def stepPrims():
    global connections, visited, visitedNodes, runningPrims

    #gets the smallest connection that connects a visited node to a non-visited node

    smallestConnection = [None, None, 10]
    newNode = None
    for connection in connections:
        if connection[2] > smallestConnection[2]:
            continue

        if connection[0] in visitedNodes and not (connection[1] in visitedNodes):
            newNode = connection[1]
        elif connection[1] in visitedNodes and not (connection[0] in visitedNodes):
            newNode = connection[0]
        else:
            continue

        smallestConnection = connection

    #if there is no valid new node, then Prim's ends and everything resets
    if newNode == None:
        runningPrims = False
        connections = visited
        visited = []
        visitedNodes = []
        advanceLabel.destroy()
        resize(None)
        return

    visited.append(smallestConnection)
    visitedNodes.append(newNode)

    resize(None)

#ran every time the right arrow is pressed
def rightArrowInput():
    global highlightedConnection, connectionIndex, runningKruskals, visited, advanceLabel

    #Kruskals code that can still be ran when Kruksal's has ended

    #will remove the current red connection from connections, changing the connectionIndex to work with this
    if len(highlightedConnection) == 2:
        if highlightedConnection[1] == "red":
            connections.remove(highlightedConnection[0])
            connectionIndex -= 1

    #will end Kruskals if the connection index has reached the end of the connections array
    if connectionIndex == len(connections):
        runningKruskals = False
        visited = []
        highlightedConnection = []
        connectionIndex = 0
        resize(None)
        advanceLabel.destroy()
        return

    if runningKruskals:
        stepKruskals()

    #ensures that prim's can only be advanced once a starting node is selected
    if runningPrims and len(visitedNodes) != 0:
        stepPrims()


savedConnections = [] #stores a saved version of all connections
savedNodes = [] #stores a saved version of all nodes

#process to save the screen by setting all saved nodes and connections to their current counterparts
def saveScreen():
    global savedConnections, currentNodes, connections, savedNodes, runningPrims, runningKruskals

    if runningPrims or runningKruskals:
        return

    #sets the variables by value by using the copy method
    savedConnections = copy.copy(connections)    
    savedNodes = copy.copy(currentNodes)

#process to load the screen by setting nodes and connections to their saved counterparts
def loadScreen():
    global savedConnections, currentNodes, connections, savedNodes, runningPrims, runningKruskals
    
    if runningPrims or runningKruskals:
        return

    print("loaded")

    #sets the variables by value by using the copy method
    connections = copy.copy(savedConnections)
    currentNodes = copy.copy(savedNodes)

    resize(None)

def clearScreen():
    global connections, currentNodes
    connections = []
    currentNodes = []

    resize(None)



canvas.bind("<Configure>", resize) #binds the canvas changing shape to the resize method
mouse.on_click(placeNode) #binds the mouse clicking to the place node method
mouse.on_right_click(selectNode) #binds the mouse right clicking to the select node method

keyboard.add_hotkey("K", initKruskals) #runs the kruskals algorithm when K is pressed
keyboard.add_hotkey("P", initPrims) #runs the Prims algorithm when P is pressed

keyboard.add_hotkey("S", saveScreen) #saves the screen state
keyboard.add_hotkey("L", loadScreen) #loads the screen state
keyboard.add_hotkey("C", clearScreen) #clears the screen


keyboard.add_hotkey("right", rightArrowInput) #progresses Kruskals by a single step

window.mainloop()
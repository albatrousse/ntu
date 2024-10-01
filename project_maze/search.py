# search.py
# ---------------
# Licensing Information:  You are free to use or extend this projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to the University of Illinois at Urbana-Champaign
#
# Created by Michael Abir (abir2@illinois.edu) on 08/28/2018
# Modified by Shang-Tse Chen (stchen@csie.ntu.edu.tw) on 03/03/2022

"""
This is the main entry point for HW1. You should only modify code
within this file -- the unrevised staff files will be used for all other
files and classes when code is run, so be careful to not modify anything else.
"""
# Search should return the path.
# The path should be a list of tuples in the form (row, col) that correspond
# to the positions of the path taken by your search algorithm.
# maze is a Maze object based on the maze from the file specified by input filename
# searchMethod is the search method specified by --method flag (bfs,dfs,astar,astar_multi,fast)
from maze import Maze
from queue import PriorityQueue
from math import sqrt, floor
import operator

def search(maze, searchMethod):
    return {
        "bfs": bfs,
        "astar": astar,
        "astar_corner": astar_corner,
        "astar_multi": astar_multi,
        "fast": fast,
    }.get(searchMethod)(maze)

# Return the Manhattan distance between to 2-uple
def manhattanDistance(a, b) :
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# Return the Euclidean distance between to 2-uple
def euclideanDistance(a, b) :
    return floor(sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2))

# Return the Chebyshev distance between to 2-uple
def chebyshevDistance(a, b) :
     return min(abs(a[0]-b[0]), abs(a[1]-b[1]))

# Heuristic "min" 
# Return the index of the closest objective from a position 
# OR 
# Return the index of the closest position to a target position 
# distance is a function which calculate the distance between two t-uple
def closestObjective(currentPosition, objectivePositions, distance):
    closestIndex = 0
    closestValue = distance(currentPosition, objectivePositions[0])
    for i in range(1, len(objectivePositions)) :
        newValue = distance(currentPosition, objectivePositions[i])
        if newValue < closestValue :
            closestValue = newValue
            closestIndex = i
    return closestIndex, closestValue

# Heuristic "sum"
def sumObjective(currentPosition, objectivePositions, distance):
    sumValue = 0
    for i in range(len(objectivePositions)) :
        sumValue = sumValue + distance(currentPosition, objectivePositions[i])
    return sumValue


# Return a boolean indicating if we achieved all the objetives
def objectiveAchieved(objectivePositions, reachedObjective):
    for (r,c) in objectivePositions :
        if (r, c) not in reachedObjective : 
            return False
    return True

# Return a tuple t indicating if an element (integer, t-uple (r,c), t-uple (r,c) ancestor)is in a queue
# t[0] = is the element in the queue | t[1] = integer associated with the element 
def queueContains(queue, element):
    for item in queue:
        if item[1] == element :
            return True, item[0], item[2]
    return False, -1, (-1,-1)

# Return the position if a position is in a (position, ancestorPosition) list
# else return -1
def containsPosition(currentPosition, positionList):
    for i in range(len(positionList)) : 
        if currentPosition == positionList[i][0] :
            return positionList[i]
    return -1

# Reconstruct a path from a position to the start position
def reconstructPath(finishPosition, startPosition, exploredPositionList, objectivePositions):
    path = [finishPosition[0]]
    currentPosition = finishPosition
    while (startPosition not in path):
        for i in range(len(exploredPositionList)):
            if exploredPositionList[i][0] == currentPosition[1] :
                #print("We found the acestor of " + str(currentPosition[0]))
                path.insert(0, currentPosition[1])
                currentPosition = exploredPositionList[i]
    return path

def bfs(maze):
    """
    Runs BFS for part 1 of the assignment.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
    """

    # Retrieving the starting position
    startPosition = Maze.getStart(maze)

    # Retrieving the objectives position
    objectivePositions = Maze.getObjectives(maze)

    # Declaring reached objectives
    reachedObjectives = []

    # Not explored yet position
    notExploredPositionList = []

    # Already explored position
    exploredPositionList = [(startPosition, (-1,-1))]

    # Path list
    pathList = [startPosition]
    
    # Adding the first neighbors in the unexplored positions
    positionNeighbors = Maze.getNeighbors(maze, startPosition[0], startPosition[1])
    for r, c in positionNeighbors:
        notExploredPositionList.append(((r,c), startPosition))

    # Iterating while **the** objective (used only for a maze with one objective) is not in the path
    while (True):
        # Verify that there is a solution
        if (len(notExploredPositionList) == 0):
            return []
        nextPosition = notExploredPositionList.pop(0)
        exploredPositionList.append(nextPosition)
        # If the next position is an objective then add it to the list of reached objectives
        if (nextPosition[0] in objectivePositions) and not(nextPosition[0] in reachedObjectives):
            reachedObjectives.append(nextPosition[0])
            newPath = reconstructPath(nextPosition, startPosition, exploredPositionList, objectivePositions)
            newPath.pop(0)
            pathList = pathList + newPath
            # We reached an objectif, now we have to reach another one
            startPosition = nextPosition[0]
            notExploredPositionList = []
            exploredPositionList = [(nextPosition[0], (-1,-1))]
        # The objectives are all reached return the pathList
        if objectiveAchieved(objectivePositions, reachedObjectives) :
            return pathList
        newNeighbors = Maze.getNeighbors(maze, nextPosition[0][0], nextPosition[0][1])
        for r, c in newNeighbors:
            if (containsPosition((r,c), exploredPositionList) == -1) and (containsPosition((r,c), notExploredPositionList) == -1):
                notExploredPositionList.append(((r,c), nextPosition[0]))


def astar(maze):
    """
    Runs A star for part 1 of the assignment.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
    """
    ## Retrieving the starting position 
    startPosition = Maze.getStart(maze)

    # Retrieving the objectives position
    objectivePositions = Maze.getObjectives(maze)

    # Declaring reached objectives
    reachedObjectives = []

    # Not explored yet position
    fringePriorityQueue = PriorityQueue()

    # Already explored position
    exploredPositionList = [(startPosition, (-1,-1))]
    
    # Declaring the pathList 
    pathList = [startPosition]

    # Adding the first neighbors in the unexplored position
    positionNeighbors = Maze.getNeighbors(maze, startPosition[0], startPosition[1])
    for r, c in positionNeighbors:
            fValueNeighbor = closestObjective((r,c), objectivePositions, manhattanDistance)[1] + 1
            fringePriorityQueue.put((fValueNeighbor, (r,c), startPosition))
    # Iterating till all the objectives are in the path
    while (True):
        # Checking if there is a solution
        if (fringePriorityQueue.empty()):
            return []
        # Retrieving the next position 
        nextPosition = fringePriorityQueue.get()
        # g-value of the next position
        gValueNextPosition = nextPosition[0] - closestObjective(nextPosition[1], objectivePositions, manhattanDistance)[1]
        # Adding the next position in the explored
        exploredPositionList.append((nextPosition[1], nextPosition[2]))
        # If the next position is an objective then add it to the list of reached objectives
        if (nextPosition[1] in objectivePositions) and not(nextPosition[1] in reachedObjectives):
            reachedObjectives.append(nextPosition[1])
            newPath = reconstructPath((nextPosition[1], nextPosition[2]), startPosition, exploredPositionList, objectivePositions)
            newPath.pop(0)
            pathList = pathList + newPath
            # We reached an objectif, now we have to reach another one
            startPosition = nextPosition[1]
            fringePriorityQueue = PriorityQueue()
            exploredPositionList = [(nextPosition[1], (-1,-1))]
        # The objectives are all reached track back the path
        if objectiveAchieved(objectivePositions, reachedObjectives) :
            return pathList
        # Retrieving all the neighbors of the next position
        newNeighbors = Maze.getNeighbors(maze, nextPosition[1][0], nextPosition[1][1])
        # Adding the neighbors to the fringe 
        for r,c in newNeighbors :
            if containsPosition((r,c), exploredPositionList) == -1:
                isInFringe, fValueInFringe, ancestorPosition = queueContains(fringePriorityQueue.queue, (r,c))
                fValueNeighbor = closestObjective((r,c), objectivePositions, manhattanDistance)[1] + gValueNextPosition + 1
                if isInFringe and (fValueNeighbor < fValueInFringe) :
                    fringePriorityQueue.queue.remove((fValueInFringe, (r,c), ancestorPosition))
                    fringePriorityQueue.put((fValueNeighbor, (r,c), nextPosition[1]))
                else :
                    fringePriorityQueue.put((fValueNeighbor, (r,c), nextPosition[1]))

def astar_corner(maze):
    """
    Runs A star for part 2 of the assignment in the case where there are four corner objectives.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
        """
    
    ## Retrieving the starting position 
    startPosition = Maze.getStart(maze)

    # Retrieving the objectives position
    objectivePositions = Maze.getObjectives(maze)

    # Declaring reached objectives
    reachedObjectives = []

    # Not explored yet position
    fringePriorityQueue = PriorityQueue()

    # Already explored position
    exploredPositionList = [(startPosition, (-1,-1))]
    
    # Declaring the pathList 
    pathList = [startPosition]

    # Adding the first neighbors in the unexplored position
    positionNeighbors = Maze.getNeighbors(maze, startPosition[0], startPosition[1])
    for r, c in positionNeighbors:
            fValueNeighbor = closestObjective((r,c), objectivePositions, manhattanDistance)[1] + 1
            fringePriorityQueue.put((fValueNeighbor, (r,c), startPosition))
    # Iterating till all the objectives are in the path
    while (True):
        # Checking if there is a solution
        if (fringePriorityQueue.empty()):
            return []
        # Retrieving the next position 
        nextPosition = fringePriorityQueue.get()
        # g-value of the next position
        gValueNextPosition = nextPosition[0] - closestObjective(nextPosition[1], objectivePositions, manhattanDistance)[1]
        # Adding the next position in the explored
        exploredPositionList.append((nextPosition[1], nextPosition[2]))
        # If the next position is an objective then add it to the list of reached objectives
        if (nextPosition[1] in objectivePositions) and not(nextPosition[1] in reachedObjectives):
            reachedObjectives.append(nextPosition[1])
            newPath = reconstructPath((nextPosition[1], nextPosition[2]), startPosition, exploredPositionList, objectivePositions)
            newPath.pop(0)
            pathList = pathList + newPath
            # We reached an objectif, now we have to reach another one
            startPosition = nextPosition[1]
            fringePriorityQueue = PriorityQueue()
            exploredPositionList = [(nextPosition[1], (-1,-1))]
            objectivePositions.remove(nextPosition[1])
        # The objectives are all reached return the pathList
        if len(objectivePositions) == 0 :
            return pathList
        # Retrieving all the neighbors of the next position
        newNeighbors = Maze.getNeighbors(maze, nextPosition[1][0], nextPosition[1][1])
        # Adding the neighbors to the fringe 
        for r,c in newNeighbors :
            if containsPosition((r,c), exploredPositionList) == -1:
                isInFringe, fValueInFringe, ancestorPosition = queueContains(fringePriorityQueue.queue, (r,c))
                fValueNeighbor = closestObjective((r,c), objectivePositions, manhattanDistance)[1] + gValueNextPosition + 1
                if isInFringe and (fValueNeighbor < fValueInFringe) :
                    fringePriorityQueue.queue.remove((fValueInFringe, (r,c), ancestorPosition))
                    fringePriorityQueue.put((fValueNeighbor, (r,c), nextPosition[1]))
                else :
                    fringePriorityQueue.put((fValueNeighbor, (r,c), nextPosition[1]))


def astar_multi(maze):
    """
    Runs A star for part 3 of the assignment in the case where there are
    multiple objectives.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
    """
    return astar_corner(maze)


def fast(maze):
    """
    Runs suboptimal search algorithm for part 4.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
    """

    return astar_corner(maze)

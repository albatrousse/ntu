# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util
import numpy as np

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best
        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        oldFood = currentGameState.getFood().asList()
        oldCapsule = currentGameState.getCapsules()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        newScore = 0

        # Look for the closest food
        minDistanceToFood = float("inf")
        for oldF in oldFood:
            distanceFromFood = util.manhattanDistance(newPos, oldF)
            if (minDistanceToFood > distanceFromFood) :
                minDistanceToFood = distanceFromFood
        
        # Make it negative because we are choosing the best score
        newScore -= minDistanceToFood

        # Reacting if thereis a ghost too close but tend to the ghost if they are "scared"
        for i in range(len(newGhostStates)): 
            distancePosFromGhost = util.manhattanDistance(newPos, newGhostStates[i].getPosition())
            if (distancePosFromGhost < newScaredTimes[i]):
                newScore += distancePosFromGhost
            elif (distancePosFromGhost <= 1):
                newScore = float("-inf")

        return newScore

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """
        
    def maxAgent(self, gameState, depth):
        # If the game is either winning or loosing or we reached asked depth return the score of the state.
        if (gameState.isWin() or gameState.isLose() or depth == self.depth):
            return (self.evaluationFunction(gameState), None)
        # Initializing useful variables.
        legalActions = gameState.getLegalActions(0)
        bestScore = float("-inf")
        currentScore = bestScore
        # We also want to return the best action from the best evaluating state.
        bestAction = None
        for action in legalActions:
            # The next agent is always the agent 1 (because maxAgent refers to Pacman).
            currentScore = self.minAgent(gameState.generateSuccessor(0, action), depth, 1)[0]
            # Look for the max "best" score and associated best action.
            if (currentScore > bestScore):
                bestScore = currentScore
                bestAction = action
        # We iterated through everything, return the t-uple with the best score and the best action.
        return (bestScore, bestAction)

    def minAgent(self, gameState, depth, agent):
        # If the game is either winning or loosing or we reached asked depth return the score of the state.
        if (gameState.isLose() or gameState.isWin() or depth == self.depth):
            return (self.evaluationFunction(gameState), None)
        # Initializing useful variables
        legalActions = gameState.getLegalActions(agent)
        bestScore = float("inf")
        currentScore = bestScore
        # We also want the best action even if it's not required since we choose the action of agent 0.
        bestAction = None
        for action in legalActions:
            # We are on the last ghost and it will be Pacman's turn next.
            if (agent == gameState.getNumAgents() - 1): 
                currentScore = self.maxAgent(gameState.generateSuccessor(agent, action), depth + 1)[0]
            # The next agent is still a ghost.
            else:
                currentScore = self.minAgent(gameState.generateSuccessor(agent, action), depth, agent + 1)[0]
            # Look for the min "best" score and the associated best action.
            if (currentScore < bestScore):
                bestScore = currentScore
                bestAction = action
        # We iterated through everything, return the t-uple with the best score and the best action.        
        return (bestScore, bestAction)
        
    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        
        return self.maxAgent(gameState, 0)[1]

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def maxAgent(self, gameState, depth, alpha, beta):
        # If the game is either winning or loosing or we reached asked depth return the score of the state.
        if (gameState.isWin() or gameState.isLose() or depth == self.depth):
            return (self.evaluationFunction(gameState), None)
        # Initializing useful variables.
        legalActions = gameState.getLegalActions(0)
        bestScore = float("-inf")
        currentScore = bestScore
        # We also want to return the best action from the best evaluating state.
        bestAction = None
        for action in legalActions:
            # The next agent is always the agent 1 (because maxAgent refers to Pacman).
            currentScore = self.minAgent(gameState.generateSuccessor(0, action), depth, 1, alpha, beta)[0]
            # Look for the max "best" score and associated best action.
            if (currentScore > bestScore):
                bestScore = currentScore
                bestAction = action
            # Don't look at the other successors if the best score is higher than beta
            if (bestScore > beta):
                return (bestScore, bestAction)
            # Updating alpha for the next successors
            alpha = max(currentScore, alpha)

        # We iterated through everything, return the t-uple with the best score and the best action.
        return (bestScore, bestAction)

    def minAgent(self, gameState, depth, agent, alpha, beta):
        # If the game is either winning or loosing or we reached asked depth return the score of the state.
        if (gameState.isLose() or gameState.isWin() or depth == self.depth):
            return (self.evaluationFunction(gameState), None)
        # Initializing useful variables
        legalActions = gameState.getLegalActions(agent)
        bestScore = float("inf")
        currentScore = bestScore
        # We also want the best action even if it's not required since we choose the action of agent 0.
        bestAction = None
        for action in legalActions:
            # We are on the last ghost and it will be Pacman's turn next.
            if (agent == gameState.getNumAgents() - 1): 
                currentScore = self.maxAgent(gameState.generateSuccessor(agent, action), depth + 1, alpha, beta)[0]
            # The next agent is still a ghost.
            else:
                currentScore = self.minAgent(gameState.generateSuccessor(agent, action), depth, agent + 1, alpha, beta)[0]
            # Look for the min "best" score and the associated best action.
            if (currentScore < bestScore):
                bestScore = currentScore
                bestAction = action
            # Don't look at the other sucessors if the best score is less than alpha
            if (bestScore < alpha):
                return (bestScore, bestAction)
            # Update beta for the other successors
            beta = min(currentScore, beta)
        # We iterated through everything, return the t-uple with the best score and the best action.        
        return (bestScore, bestAction)

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"

        alpha = float("-inf")
        beta = float("inf")
        return self.maxAgent(gameState, 0, alpha, beta)[1]

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def maxAgent(self, gameState, depth):
        # If the game is either winning or loosing or we reached asked depth return the score of the state.
        if (gameState.isWin() or gameState.isLose() or depth == self.depth):
            return (self.evaluationFunction(gameState), None)
        # Initializing useful variables.
        legalActions = gameState.getLegalActions(0)
        bestScore = float("-inf")
        currentScore = bestScore
        # We also want to return the best action from the best evaluating state.
        bestAction = None
        for action in legalActions:
            # The next agent is always the agent 1 (because maxAgent refers to Pacman).
            currentScore = self.expAgent(gameState.generateSuccessor(0, action), depth, 1)
            # Look for the max "best" score and associated best action.
            if (currentScore > bestScore):
                bestScore = currentScore
                bestAction = action
        # We iterated through everything, return the t-uple with the best score and the best action.
        return (bestScore, bestAction)

    def expAgent(self, gameState, depth, agent):
        # If the game is either winning or loosing or we reached asked depth return the score of the state.
        if (gameState.isLose() or gameState.isWin() or depth == self.depth):
            return self.evaluationFunction(gameState)
        # Initializing useful variables
        legalActions = gameState.getLegalActions(agent)
        expValue = 0
        for action in legalActions:
            # We are on the last ghost and it will be Pacman's turn next.
            if (agent == gameState.getNumAgents() - 1): 
                currentScore = self.maxAgent(gameState.generateSuccessor(agent, action), depth + 1)[0]
            # The next agent is still a ghost.
            else:
                currentScore = self.expAgent(gameState.generateSuccessor(agent, action), depth, agent + 1)
            # Compute the expected utilities (average score from all the sucessors)
            expValue += currentScore / len(legalActions)
        # We iterated through everything, we now return the expected utilities of this agent    
        return expValue

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"

        return self.maxAgent(gameState, 0)[1]

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <This evaluation function will return an evaluation of the current game state.
    It first retrieves the important information from the state : Pacman position(pacmanPos), ghosts' state(ghostList),
    foods position (foodList) and capsules positions (capList).
    If the game is either winning or loosing : it will directly return a +infty or -infty score because there is nothing to evaluate
    Else : It will compute different useful variables such as : the distance from the closest food (minFoodDist), the distance from
    the closest ghost (minGhostDist) and the distance from the closest scared ghost (minScaredGhostDist).
    After computing all these variables it will just add/retrieve to the game score (currentState.getScore()) the different variables with a
    weight depending on how much they matters.>
    """
    "*** YOUR CODE HERE ***"
    # Return based on game state
    if currentGameState.isWin():
        return float("inf")
    if currentGameState.isLose():
        return float("-inf")
    
    # Retrieving the useful information
    pacmanPos = currentGameState.getPacmanPosition()
    ghostList = currentGameState.getGhostStates() 
    foodList = currentGameState.getFood().asList()
    capList = currentGameState.getCapsules()
    # Populate foodDistList and find minFoodDist
    foodDistList = []
    for food in foodList:
        foodDistList = foodDistList + [util.manhattanDistance(food, pacmanPos)]
    minFoodDist = min(foodDistList)
    # Populate ghostDistList and scaredGhostDistList, find minGhostDist and minScaredGhostDist
    ghostDistList = []
    scaredGhostDistList = []
    for ghost in ghostList:
        if ghost.scaredTimer == 0:
            ghostDistList = ghostDistList + [util.manhattanDistance(pacmanPos, ghost.getPosition())]
        elif ghost.scaredTimer > 0:
            scaredGhostDistList = scaredGhostDistList + [util.manhattanDistance(pacmanPos, ghost.getPosition())]
    minGhostDist = -1
    if len(ghostDistList) > 0:
        minGhostDist = min(ghostDistList)
    minScaredGhostDist = -1
    if len(scaredGhostDistList) > 0:
        minScaredGhostDist = min(scaredGhostDistList)

    # Evaluate score
    score = currentGameState.getScore();
    # Distance to closest food
    score = score + (-1.5 * minFoodDist)
    # Distance to closest ghost
    score = score + (-2 * (1.0 / minGhostDist))
    # Distance to closest scared ghost
    score = score + (-2 * minScaredGhostDist)
    # Number of capsules
    score = score + (-20 * len(capList))
    # Number of food
    score = score + (-4 * len(foodList))
    return score

# Abbreviation
better = betterEvaluationFunction
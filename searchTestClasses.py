# searchTestClasses.py
# --------------------
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


import re
import sys
import textwrap

# import project specific code
import layout
import pacman
import testClasses
from game import Actions
from search import SearchProblem


# helper function for printing solutions in solution files
def wrap_solution(solution):
    if isinstance(solution, list):
        return '\n'.join(textwrap.wrap(' '.join(solution)))
    else:
        return str(solution)


def followAction(state, action, problem):
    for successor1, action1, cost1 in problem.getSuccessors(state):
        if action == action1: return successor1
    return None


def followPath(path, problem):
    state = problem.getStartState()
    states = [state]
    for action in path:
        state = followAction(state, action, problem)
        states.append(state)
    return states


def checkSolution(problem, path):
    state = problem.getStartState()
    for action in path:
        state = followAction(state, action, problem)
    return problem.isGoalState(state)


# Search problem on a plain graph
class GraphSearch(SearchProblem):

    # Read in the state graph; define start/end states, edges and costs
    def __init__(self, graph_text):
        self.expanded_states = []
        lines = graph_text.split('\n')
        r = re.match('start_state:(.*)', lines[0])
        if r is None:
            print("Broken graph:")
            print(f'"""{graph_text}"""')
            raise Exception("GraphSearch graph specification start_state not found or incorrect on line 0")
        self.start_state = r.group(1).strip()
        r = re.match('goal_states:(.*)', lines[1])
        if r is None:
            print("Broken graph:")
            print(f'"""{graph_text}"""')
            raise Exception("GraphSearch graph specification goal_states not found or incorrect on line 1")
        goals = r.group(1).split()
        self.goals = [str.strip(g) for g in goals]
        self.successors = {}
        all_states = set()
        self.orderedSuccessorTuples = []
        for line in lines[2:]:
            if len(line.split()) == 3:
                start, action, next_state = line.split()
                cost = 1
            elif len(line.split()) == 4:
                start, action, next_state, cost = line.split()
            else:
                print("Broken graph:")
                print(f'"""{graph_text}"""')
                raise Exception(f"Invalid line in GraphSearch graph specification on line: {line}")
            cost = float(cost)
            self.orderedSuccessorTuples.append((start, action, next_state, cost))
            all_states.add(start)
            all_states.add(next_state)
            if start not in self.successors:
                self.successors[start] = []
            self.successors[start].append((next_state, action, cost))
        for s in all_states:
            if s not in self.successors:
                self.successors[s] = []

    # Get start state
    def getStartState(self):
        return self.start_state

    # Check if a state is a goal state
    def isGoalState(self, state):
        return state in self.goals

    # Get all successors of a state
    def getSuccessors(self, state):
        self.expanded_states.append(state)
        return list(self.successors[state])

    # Calculate total cost of a sequence of actions
    def getCostOfActions(self, actions):
        total_cost = 0
        state = self.start_state
        for a in actions:
            successors = self.successors[state]
            match = False
            for (next_state, action, cost) in successors:
                if a == action:
                    state = next_state
                    total_cost += cost
                    match = True
            if not match:
                print('invalid action sequence')
                sys.exit(1)
        return total_cost

    # Return a list of all states on which 'getSuccessors' was called
    def getExpandedStates(self):
        return self.expanded_states

    def __str__(self):
        print(self.successors)
        edges = ["%s %s %s %s" % t for t in self.orderedSuccessorTuples]
        return \
            """start_state: %s
            goal_states: %s
            %s""" % (self.start_state, " ".join(self.goals), "\n".join(edges))


def parseHeuristic(heuristicText):
    heuristic = {}
    for line in heuristicText.split('\n'):
        tokens = line.split()
        if len(tokens) != 2:
            print("Broken heuristic:")
            print(f'"""{heuristicText}"""')
            raise Exception("GraphSearch heuristic specification broken at tokens:" + str(tokens))
        state, h = tokens
        heuristic[state] = float(h)

    def graphHeuristic(state, problem=None):
        if state in heuristic:
            return heuristic[state]
        else:
            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            print("Heuristic:")
            pp.pprint(heuristic)
            raise Exception("Graph heuristic called with invalid state: " + str(state))

    return graphHeuristic


class GraphSearchTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(GraphSearchTest, self).__init__(question, testDict)
        self.graph_text = testDict['graph']
        self.alg = testDict['algorithm']
        self.diagram = testDict['diagram']
        self.exactExpansionOrder = testDict.get('exactExpansionOrder', 'True').lower() == "true"
        if 'heuristic' in testDict:
            self.heuristic = parseHeuristic(testDict['heuristic'])
        else:
            self.heuristic = None

    # Note that the return type of this function is a tripple:
    # (solution, expanded states, error message)
    def getSolInfo(self, search):
        alg = getattr(search, self.alg)
        problem = GraphSearch(self.graph_text)
        if self.heuristic is not None:
            solution = alg(problem, self.heuristic)
        else:
            solution = alg(problem)

        if not isinstance(solution, list):
            return None, None, f'The result of {self.alg} must be a list. (Instead, it is {type(solution)})'

        return solution, problem.getExpandedStates(), None

    # Run student code.  If an error message is returned, print error and return false.
    # If a good solution is returned, printn the solution and return true; otherwise,
    # print both the correct and student's solution and return false.
    def execute(self, grades, moduleDict, solutionDict):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        gold_solution = [str.split(solutionDict['solution']), str.split(solutionDict['rev_solution'])]
        gold_expanded_states = [str.split(solutionDict['expanded_states']), str.split(solutionDict['rev_expanded_states'])]

        solution, expanded_states, error = self.getSolInfo(search)
        if error is not None:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'\t{error}')
            return False

        if solution in gold_solution and (not self.exactExpansionOrder or expanded_states in gold_expanded_states):
            grades.addMessage(f'PASS: {self.path}')
            grades.addMessage(f'\tsolution:\t\t{solution}')
            grades.addMessage(f'\texpanded_states:\t{expanded_states}')
            return True
        else:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('\tgraph:')
            for line in self.diagram.split('\n'):
                grades.addMessage(f'\t    {line}')
            grades.addMessage(f'\tstudent solution:\t\t{solution}')
            grades.addMessage(f'\tstudent expanded_states:\t{expanded_states}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect solution:\t\t{gold_solution[0]}')
            grades.addMessage(f'\tcorrect expanded_states:\t{gold_expanded_states[0]}')
            grades.addMessage(f'\tcorrect rev_solution:\t\t{gold_solution[1]}')
            grades.addMessage(f'\tcorrect rev_expanded_states:\t{gold_expanded_states[1]}')
            return False

    def writeSolution(self, moduleDict, filePath):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        # open file and write comments
        handle = open(filePath, 'w')
        handle.write(f'# This is the solution file for {self.path}.\n')
        handle.write('# This solution is designed to support both right-to-left\n')
        handle.write('# and left-to-right implementations.\n')

        # write forward solution
        solution, expanded_states, error = self.getSolInfo(search)
        if error is not None: raise Exception(f"Error in solution code: {error}")
        handle.write(f'solution: "{" ".join(solution)}"\n')
        handle.write(f'expanded_states: "{" ".join(expanded_states)}"\n')

        # reverse and write backwards solution
        search.REVERSE_PUSH = not search.REVERSE_PUSH
        solution, expanded_states, error = self.getSolInfo(search)
        if error is not None: raise Exception(f"Error in solution code: {error}")
        handle.write(f'rev_solution: "{" ".join(solution)}"\n')
        handle.write(f'rev_expanded_states: "{" ".join(expanded_states)}"\n')

        # clean up
        search.REVERSE_PUSH = not search.REVERSE_PUSH
        handle.close()
        return True


class PacmanSearchTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(PacmanSearchTest, self).__init__(question, testDict)
        self.layout_text = testDict['layout']
        self.alg = testDict['algorithm']
        self.layoutName = testDict['layoutName']

        # TODO: sensible to have defaults like this?
        self.leewayFactor = float(testDict.get('leewayFactor', '1'))
        self.costFn = eval(testDict.get('costFn', 'None'))
        self.searchProblemClassName = testDict.get('searchProblemClass', 'PositionSearchProblem')
        self.heuristicName = testDict.get('heuristic', None)

    def getSolInfo(self, search, searchAgents):
        alg = getattr(search, self.alg)
        lay = layout.Layout([line.strip() for line in self.layout_text.split('\n')])
        start_state = pacman.GameState()
        start_state.initialize(lay, 0)

        problemClass = getattr(searchAgents, self.searchProblemClassName)
        problemOptions = {}
        if self.costFn is not None:
            problemOptions['costFn'] = self.costFn
        problem = problemClass(start_state, **problemOptions)
        heuristic = getattr(searchAgents, self.heuristicName) if self.heuristicName is not None else None

        if heuristic is not None:
            solution = alg(problem, heuristic)
        else:
            solution = alg(problem)

        if not isinstance(solution, list):
            return None, None, f'The result of {self.alg} must be a list. (Instead, it is {type(solution)})'

        from game import Directions
        dirs = Directions.LEFT.keys()
        if [el in dirs for el in solution].count(False) != 0:
            return None, None, f'Output of {self.alg} must be a list of actions from game.Directions'

        expanded = problem._expanded
        return solution, expanded, None

    def execute(self, grades, moduleDict, solutionDict):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        gold_solution = [str.split(solutionDict['solution']), str.split(solutionDict['rev_solution'])]
        gold_expanded = max(int(solutionDict['expanded_nodes']), int(solutionDict['rev_expanded_nodes']))

        solution, expanded, error = self.getSolInfo(search, searchAgents)
        if error is not None:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'\t{error}')
            return False

        # FIXME: do we want to standardize test output format?

        if solution not in gold_solution:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('Solution not correct.')
            grades.addMessage(f'\tstudent solution length: {len(solution)}')
            grades.addMessage(f'\tstudent solution:\n{wrap_solution(solution)}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect solution length: {len(gold_solution[0])}')
            grades.addMessage(f'\tcorrect (reversed) solution length: {len(gold_solution[1])}')
            grades.addMessage(f'\tcorrect solution:\n{wrap_solution(gold_solution[0])}')
            grades.addMessage(f'\tcorrect (reversed) solution:\n{wrap_solution(gold_solution[1])}')
            return False

        if expanded > self.leewayFactor * gold_expanded and expanded > gold_expanded + 1:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('Too many node expanded; are you expanding nodes twice?')
            grades.addMessage(f'\tstudent nodes expanded: {expanded}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect nodes expanded: {gold_expanded} (leewayFactor {self.leewayFactor})')
            return False

        grades.addMessage(f'PASS: {self.path}')
        grades.addMessage(f'\tpacman layout:\t\t{self.layoutName}')
        grades.addMessage(f'\tsolution length: {len(solution)}')
        grades.addMessage(f'\tnodes expanded:\t\t{expanded}')
        return True

    def writeSolution(self, moduleDict, filePath):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        # open file and write comments
        handle = open(filePath, 'w')
        handle.write(f'# This is the solution file for {self.path}.\n')
        handle.write('# This solution is designed to support both right-to-left\n')
        handle.write('# and left-to-right implementations.\n')
        handle.write(f'# Number of nodes expanded must be with a factor of {self.leewayFactor} of the numbers below.\n')

        # write forward solution
        solution, expanded, error = self.getSolInfo(search, searchAgents)
        if error is not None: raise Exception(f"Error in solution code: {error}")
        handle.write(f'solution: """\n{wrap_solution(solution)}\n"""\n')
        handle.write(f'expanded_nodes: "{expanded}"\n')

        # write backward solution
        search.REVERSE_PUSH = not search.REVERSE_PUSH
        solution, expanded, error = self.getSolInfo(search, searchAgents)
        if error is not None: raise Exception(f"Error in solution code: {error}")
        handle.write(f'rev_solution: """\n{wrap_solution(solution)}\n"""\n')
        handle.write(f'rev_expanded_nodes: "{expanded}"\n')

        # clean up
        search.REVERSE_PUSH = not search.REVERSE_PUSH
        handle.close()
        return True


def getStatesFromPath(start, path):
    """Returns the list of states visited along the path"""
    vis = [start]
    curr = start
    for a in path:
        x, y = curr
        dx, dy = Actions.directionToVector(a)
        curr = (int(x + dx), int(y + dy))
        vis.append(curr)
    return vis


class CornerProblemTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(CornerProblemTest, self).__init__(question, testDict)
        self.layoutText = testDict['layout']
        self.layoutName = testDict['layoutName']

    def solution(self, search, searchAgents):
        lay = layout.Layout([line.strip() for line in self.layoutText.split('\n')])
        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        problem = searchAgents.CornersProblem(gameState)
        path = search.bfs(problem)

        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        visited = getStatesFromPath(gameState.getPacmanPosition(), path)
        top, right = gameState.getWalls().height - 2, gameState.getWalls().width - 2
        missedCorners = [p for p in ((1, 1), (1, top), (right, 1), (right, top)) if p not in visited]

        return path, missedCorners

    def execute(self, grades, moduleDict, solutionDict):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        gold_length = int(solutionDict['solution_length'])
        solution, missedCorners = self.solution(search, searchAgents)

        if not isinstance(solution, list):
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'The result must be a list. (Instead, it is {type(solution)})')
            return False

        if len(missedCorners) != 0:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'Corners missed: {missedCorners}')
            return False

        if len(solution) != gold_length:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('Optimal solution not found.')
            grades.addMessage(f'\tstudent solution length:\n{len(solution)}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect solution length:\n{gold_length}')
            return False

        grades.addMessage(f'PASS: {self.path}')
        grades.addMessage(f'\tpacman layout:\t\t{self.layoutName}')
        grades.addMessage(f'\tsolution length:\t\t{len(solution)}')
        return True

    def writeSolution(self, moduleDict, filePath):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        # open file and write comments
        handle = open(filePath, 'w')
        handle.write(f'# This is the solution file for {self.path}.\n')

        print("Solving problem", self.layoutName)
        print(self.layoutText)

        path, _ = self.solution(search, searchAgents)
        length = len(path)
        print("Problem solved")

        handle.write(f'solution_length: "{length}"\n')
        handle.close()


# template = """class: "HeuristicTest"
#
# heuristic: "foodHeuristic"
# searchProblemClass: "FoodSearchProblem"
# layoutName: "Test %s"
# layout: \"\"\"
# %s
# \"\"\"
# """
#
# for i, (_, _, l) in enumerate(doneTests + foodTests):
#     f = open("food_heuristic_%s.test" % (i+1), "w")
#     f.write(template % (i+1, "\n".join(l)))
#     f.close()

class HeuristicTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(HeuristicTest, self).__init__(question, testDict)
        self.layoutText = testDict['layout']
        self.layoutName = testDict['layoutName']
        self.searchProblemClassName = testDict['searchProblemClass']
        self.heuristicName = testDict['heuristic']

    def setupProblem(self, searchAgents):
        lay = layout.Layout([line.strip() for line in self.layoutText.split('\n')])
        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        problemClass = getattr(searchAgents, self.searchProblemClassName)
        problem = problemClass(gameState)
        state = problem.getStartState()
        heuristic = getattr(searchAgents, self.heuristicName)

        return problem, state, heuristic

    def checkHeuristic(self, heuristic, problem, state, solutionCost):
        h0 = heuristic(state, problem)

        if solutionCost == 0:
            if h0 == 0:
                return True, ''
            else:
                return False, 'Heuristic failed H(goal) == 0 test'

        if h0 < 0:
            return False, 'Heuristic failed H >= 0 test'
        if not h0 > 0:
            return False, 'Heuristic failed non-triviality test'
        if not h0 <= solutionCost:
            return False, 'Heuristic failed admissibility test'

        for succ, action, stepCost in problem.getSuccessors(state):
            h1 = heuristic(succ, problem)
            if h1 < 0: return False, 'Heuristic failed H >= 0 test'
            if h0 - h1 > stepCost: return False, 'Heuristic failed consistency test'

        return True, ''

    def execute(self, grades, moduleDict, solutionDict):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        solutionCost = int(solutionDict['solution_cost'])
        problem, state, heuristic = self.setupProblem(searchAgents)

        passed, message = self.checkHeuristic(heuristic, problem, state, solutionCost)

        if not passed:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'{message}')
            return False
        else:
            grades.addMessage(f'PASS: {self.path}')
            return True

    def writeSolution(self, moduleDict, filePath):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        # open file and write comments
        handle = open(filePath, 'w')
        handle.write(f'# This is the solution file for {self.path}.\n')

        print("Solving problem", self.layoutName, self.heuristicName)
        print(self.layoutText)
        problem, _, heuristic = self.setupProblem(searchAgents)
        path = search.astar(problem, heuristic)
        cost = problem.getCostOfActions(path)
        print("Problem solved")

        handle.write(f'solution_cost: "{cost}"\n')
        handle.close()
        return True


class HeuristicGrade(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(HeuristicGrade, self).__init__(question, testDict)
        self.layoutText = testDict['layout']
        self.layoutName = testDict['layoutName']
        self.searchProblemClassName = testDict['searchProblemClass']
        self.heuristicName = testDict['heuristic']
        self.basePoints = int(testDict['basePoints'])
        self.thresholds = [int(t) for t in testDict['gradingThresholds'].split()]

    def setupProblem(self, searchAgents):
        lay = layout.Layout([line.strip() for line in self.layoutText.split('\n')])
        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        problemClass = getattr(searchAgents, self.searchProblemClassName)
        problem = problemClass(gameState)
        state = problem.getStartState()
        heuristic = getattr(searchAgents, self.heuristicName)

        return problem, state, heuristic

    def execute(self, grades, moduleDict, solutionDict):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        problem, _, heuristic = self.setupProblem(searchAgents)

        path = search.astar(problem, heuristic)

        expanded = problem._expanded

        if not checkSolution(problem, path):
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('\tReturned path is not a solution.')
            grades.addMessage(f'\tpath returned by astar: {expanded}')
            return False

        grades.addPoints(self.basePoints)
        points = 0
        for threshold in self.thresholds:
            if expanded <= threshold:
                points += 1
        grades.addPoints(points)
        if points >= len(self.thresholds):
            grades.addMessage(f'PASS: {self.path}')
        else:
            grades.addMessage(f'FAIL: {self.path}')
        grades.addMessage(f'\texpanded nodes: {expanded}')
        grades.addMessage(f'\tthresholds: {self.thresholds}')

        return True

    def writeSolution(self, moduleDict, filePath):
        handle = open(filePath, 'w')
        handle.write(f'# This is the solution file for {self.path}.\n')
        handle.write('# File intentionally blank.\n')
        handle.close()
        return True


# template = """class: "ClosestDotTest"
#
# layoutName: "Test %s"
# layout: \"\"\"
# %s
# \"\"\"
# """
#
# for i, (_, _, l) in enumerate(foodTests):
#     f = open("closest_dot_%s.test" % (i+1), "w")
#     f.write(template % (i+1, "\n".join(l)))
#     f.close()

class ClosestDotTest(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(ClosestDotTest, self).__init__(question, testDict)
        self.layoutText = testDict['layout']
        self.layoutName = testDict['layoutName']

    def solution(self, searchAgents):
        lay = layout.Layout([line.strip() for line in self.layoutText.split('\n')])
        gameState = pacman.GameState()
        gameState.initialize(lay, 0)
        path = searchAgents.ClosestDotSearchAgent().findPathToClosestDot(gameState)
        return path

    def execute(self, grades, moduleDict, solutionDict):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        gold_length = int(solutionDict['solution_length'])
        solution = self.solution(searchAgents)

        if not isinstance(solution, list):
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage(f'\tThe result must be a list. (Instead, it is {type(solution)})')
            return False

        if len(solution) != gold_length:
            grades.addMessage(f'FAIL: {self.path}')
            grades.addMessage('Closest dot not found.')
            grades.addMessage(f'\tstudent solution length:\n{len(solution)}')
            grades.addMessage('')
            grades.addMessage(f'\tcorrect solution length:\n{gold_length}')
            return False

        grades.addMessage(f'PASS: {self.path}')
        grades.addMessage(f'\tpacman layout:\t\t{self.layoutName}')
        grades.addMessage(f'\tsolution length:\t\t{len(solution)}')
        return True

    def writeSolution(self, moduleDict, filePath):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        # open file and write comments
        handle = open(filePath, 'w')
        handle.write(f'# This is the solution file for {self.path}.\n')

        print("Solving problem", self.layoutName)
        print(self.layoutText)

        length = len(self.solution(searchAgents))
        print("Problem solved")

        handle.write(f'solution_length: "{length}"\n')
        handle.close()
        return True


class CornerHeuristicSanity(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(CornerHeuristicSanity, self).__init__(question, testDict)
        self.layout_text = testDict['layout']

    def execute(self, grades, moduleDict, solutionDict):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        game_state = pacman.GameState()
        lay = layout.Layout([line.strip() for line in self.layout_text.split('\n')])
        game_state.initialize(lay, 0)
        problem = searchAgents.CornersProblem(game_state)
        start_state = problem.getStartState()
        h0 = searchAgents.cornersHeuristic(start_state, problem)
        succs = problem.getSuccessors(start_state)
        # cornerConsistencyA
        for succ in succs:
            h1 = searchAgents.cornersHeuristic(succ[0], problem)
            if h0 - h1 > 1:
                grades.addMessage('FAIL: inconsistent heuristic')
                return False
        heuristic_cost = searchAgents.cornersHeuristic(start_state, problem)
        true_cost = float(solutionDict['cost'])
        # cornerNontrivial
        if heuristic_cost == 0:
            grades.addMessage('FAIL: must use non-trivial heuristic')
            return False
        # cornerAdmissible
        if heuristic_cost > true_cost:
            grades.addMessage('FAIL: Inadmissible heuristic')
            return False
        path = solutionDict['path'].split()
        states = followPath(path, problem)
        heuristics = []
        for state in states:
            heuristics.append(searchAgents.cornersHeuristic(state, problem))
        for i in range(0, len(heuristics) - 1):
            h0 = heuristics[i]
            h1 = heuristics[i + 1]
            # cornerConsistencyB
            if h0 - h1 > 1:
                grades.addMessage('FAIL: inconsistent heuristic')
                return False
            # cornerPosH
            if h0 < 0 or h1 < 0:
                grades.addMessage('FAIL: non-positive heuristic')
                return False
        # cornerGoalH
        if heuristics[len(heuristics) - 1] != 0:
            grades.addMessage('FAIL: heuristic non-zero at goal')
            return False
        grades.addMessage('PASS: heuristic value less than true cost at start state')
        return True

    def writeSolution(self, moduleDict, filePath):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        # write comment
        handle = open(filePath, 'w')
        handle.write('# In order for a heuristic to be admissible, the value\n')
        handle.write('# of the heuristic must be less at each state than the\n')
        handle.write('# true cost of the optimal path from that state to a goal.\n')

        # solve problem and write solution
        lay = layout.Layout([line.strip() for line in self.layout_text.split('\n')])
        start_state = pacman.GameState()
        start_state.initialize(lay, 0)
        problem = searchAgents.CornersProblem(start_state)
        solution = search.astar(problem, searchAgents.cornersHeuristic)
        handle.write(f'cost: "{len(solution)}"\n')
        handle.write(f'path: """\n{wrap_solution(solution)}\n"""\n')
        handle.close()
        return True


class CornerHeuristicPacman(testClasses.TestCase):

    def __init__(self, question, testDict):
        super(CornerHeuristicPacman, self).__init__(question, testDict)
        self.layout_text = testDict['layout']

    def execute(self, grades, moduleDict, solutionDict):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        total = 0
        true_cost = float(solutionDict['cost'])
        thresholds = [int(x) for x in solutionDict['thresholds'].split()]
        game_state = pacman.GameState()
        lay = layout.Layout([line.strip() for line in self.layout_text.split('\n')])
        game_state.initialize(lay, 0)
        problem = searchAgents.CornersProblem(game_state)
        start_state = problem.getStartState()
        if searchAgents.cornersHeuristic(start_state, problem) > true_cost:
            grades.addMessage('FAIL: Inadmissible heuristic')
            return False
        path = search.astar(problem, searchAgents.cornersHeuristic)
        print("path:", path)
        print("path length:", len(path))
        cost = problem.getCostOfActions(path)
        if cost > true_cost:
            grades.addMessage('FAIL: Inconsistent heuristic')
            return False
        expanded = problem._expanded
        points = 0
        for threshold in thresholds:
            if expanded <= threshold:
                points += 1
        grades.addPoints(points)
        if points >= len(thresholds):
            grades.addMessage(f'PASS: Heuristic resulted in expansion of {expanded} nodes')
        else:
            grades.addMessage(f'FAIL: Heuristic resulted in expansion of {expanded} nodes')
        return True

    def writeSolution(self, moduleDict, filePath):
        search = moduleDict['search']
        searchAgents = moduleDict['searchAgents']
        # write comment
        handle = open(filePath, 'w')
        handle.write('# This solution file specifies the length of the optimal path\n')
        handle.write('# as well as the thresholds on number of nodes expanded to be\n')
        handle.write('# used in scoring.\n')

        # solve problem and write solution
        lay = layout.Layout([line.strip() for line in self.layout_text.split('\n')])
        start_state = pacman.GameState()
        start_state.initialize(lay, 0)
        problem = searchAgents.CornersProblem(start_state)
        solution = search.astar(problem, searchAgents.cornersHeuristic)
        handle.write(f'cost: "{len(solution)}"\n')
        handle.write(f'path: """\n{wrap_solution(solution)}\n"""\n')
        handle.write('thresholds: "2000 1600 1200"\n')
        handle.close()
        return True
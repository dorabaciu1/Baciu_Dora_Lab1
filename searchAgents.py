# -*- coding: utf-8 -*-
"""
searchAgents.py

Agenți de căutare pentru proiectul Pacman (Berkeley).
Autor(i): <completați aici numele membrilor echipei>
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
import sys

import util
from game import Directions
import search


class GoWestAgent:
    """Un agent foarte simplu care se deplasează mereu spre vest dacă poate."""

    def getAction(self, state):
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP


class SearchAgent:
    """
    Un agent generic de căutare care poate rula diferite strategii, de ex. DFS, BFS, UCS, A*.

    Se configurează cu parametrii:
    - fn: numele funcției de căutare din modulul `search` (dfs, bfs, ucs, astar)
    - heuristic: numele euristicii din modulul `search` (implicit nullHeuristic)

    Exemplu de rulare:
    python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
    """

    def __init__(self, fn: str = 'dfs', prob: str = 'PositionSearchProblem', heuristic: str = 'nullHeuristic') -> None:
        # Rezolvă funcția de căutare din modulul `search`
        if not hasattr(search, fn):
            raise AttributeError(f"Funcția de căutare '{fn}' nu a fost găsită în modulul search.")
        func = getattr(search, fn)

        # Rezolvă tipul problemei (din acest modul)
        try:
            self.searchType = globals()[prob]
        except KeyError:
            raise AttributeError(f"Tipul de problemă '{prob}' nu a fost găsit în searchAgents.")

        # Rezolvă euristica: mai întâi în acest modul, apoi în modulul `search`
        heuristic_fn = None
        if 'heuristic' in func.__code__.co_varnames:
            module_self = sys.modules[__name__]
            if hasattr(module_self, heuristic):
                heuristic_fn = getattr(module_self, heuristic)
            elif hasattr(search, heuristic):
                heuristic_fn = getattr(search, heuristic)
            else:
                raise AttributeError(
                    f"Euristica '{heuristic}' nu a fost găsită nici în searchAgents, nici în search."
                )
            self.searchFunction = lambda prob_instance: func(prob_instance, heuristic=heuristic_fn)
        else:
            self.searchFunction = func

        self.actions: List[Any] = []

    def registerInitialState(self, state) -> None:
        """
        Este apelată la începutul jocului. Aici rulăm căutarea pentru a obține
        lista de acțiuni pe care agentul le va executa.
        """
        problem = self.searchType(state)
        self.actions = self.searchFunction(problem)

    def getAction(self, state):
        if len(self.actions) == 0:
            return Directions.STOP
        return self.actions.pop(0)


class PositionSearchProblem(search.SearchProblem):
    """
    Problemă simplă: ajunge la poziția scop cu costul implicit 1 per pas.
    Folosită de SearchAgent ca wrapper peste starea jocului Pacman.
    """

    def __init__(self, gameState, costFn: Callable = lambda x: 1, goal: Optional[tuple] = (1, 1), start: Optional[tuple] = None, warn: bool = True, visualize: bool = True):
        from game import Actions

        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition() if start is None else start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize
        self._visited, self._visitedlist, self._expanded = {}, [], 0  # pentru vizualizare

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal
        return isGoal

    def getSuccessors(self, state):
        from game import Actions

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append((nextState, action, cost))
        self._expanded += 1  # doar pentru vizualizare
        return successors

    def getCostOfActions(self, actions):
        if actions is None:
            return float('inf')
        x, y = self.startState
        cost = 0
        from game import Actions

        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return float('inf')
            cost += self.costFn((x, y))
        return cost


def manhattanHeuristic(position, problem: Optional[PositionSearchProblem] = None, info: Dict = {}):
    """Heuristica Manhattan între poziție și scop (dacă există scop)."""
    if problem is None or getattr(problem, 'goal', None) is None:
        return 0
    goal = problem.goal
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


class StayEastSearchAgent(SearchAgent):
    """
    Agent A* cu o funcție de cost care încurajează pozițiile din est (x mare).
    Folosit pentru: python pacman.py -l mediumDottedMaze -p StayEastSearchAgent
    """

    def __init__(self):
        def costFn(pos):
            # Cost mai mic în est => încurajează deplasarea spre est
            x, y = pos
            return 0.5 ** x

        self.searchFunction = search.uniformCostSearch
        self.searchType = lambda state: PositionSearchProblem(state, costFn=costFn)
        self.actions = []

    def registerInitialState(self, state):
        problem = self.searchType(state)
        self.actions = self.searchFunction(problem)


class StayWestSearchAgent(SearchAgent):
    """
    Agent A* cu o funcție de cost care favorizează vestul (x mic).
    Folosit pentru: python pacman.py -l mediumScaryMaze -p StayWestSearchAgent
    """

    def __init__(self):
        def costFn(pos):
            x, y = pos
            return 2 ** x  # Cost crescut în est, scăzut în vest

        self.searchFunction = search.uniformCostSearch
        self.searchType = lambda state: PositionSearchProblem(state, costFn=costFn)
        self.actions = []

    def registerInitialState(self, state):
        problem = self.searchType(state)
        self.actions = self.searchFunction(problem)

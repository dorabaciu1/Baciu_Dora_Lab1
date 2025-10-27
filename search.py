# -*- coding: utf-8 -*-
"""
search.py

Algoritmi generali de căutare pentru proiectul Pacman (Berkeley).

NOTĂ privind autorii: înlocuiți textul de mai jos cu numele membrilor echipei
în comentariile funcțiilor, dacă este necesar de către regulile de predare.
Autor(i) funcții: <completați aici numele membrilor echipei>
"""

from __future__ import annotations

import sys
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple

import util


class SearchProblem(object):
    """
    Aceasta clasă conturează structura unei probleme de căutare, dar nu
    implementează niciuna dintre metode. Trebuie folosită ca interfață.
    """

    def getStartState(self) -> Any:
        """Returnează starea de start pentru problema de căutare."""
        raise NotImplementedError()

    def isGoalState(self, state: Any) -> bool:
        """Returnează True dacă și numai dacă starea este o stare scop."""
        raise NotImplementedError()

    def getSuccessors(self, state: Any) -> List[Tuple[Any, Any, float]]:
        """
        Pentru o stare, returnează o listă de triple (succesor, acțiune, cost)
        unde 'succesor' este o stare succesoare curentă, 'acțiune' este acțiunea
        necesară pentru a ajunge acolo și 'cost' este costul incremental.
        """
        raise NotImplementedError()

    def getCostOfActions(self, actions: Sequence[Any]) -> float:
        """
        Returnează costul total al unei secvențe de acțiuni. Secvența trebuie
        să fie compusă doar din acțiuni legale. Costul este suma costurilor
        incrementale returnate de `getSuccessors`.
        """
        raise NotImplementedError()


#####################################################
# Algoritmi de căutare                               #
#####################################################


def tinyMazeSearch(problem: SearchProblem) -> List[Any]:
    """Soluție hard-codată pentru tinyMaze (doar pentru test rapid)."""
    from game import Directions

    s = Directions.SOUTH
    w = Directions.WEST
    return [s, s, w, s, w, w, s, w]


def depthFirstSearch(problem: SearchProblem) -> List[Any]:
    """
    Căutare în adâncime (DFS) în spațiul stărilor.
    Autor: <completați numele autorului>
    """
    from util import Stack

    start_state = problem.getStartState()
    if problem.isGoalState(start_state):
        return []

    stack: Stack = Stack()
    stack.push((start_state, []))
    visited = set()

    while not stack.isEmpty():
        state, path = stack.pop()
        if state in visited:
            continue
        visited.add(state)

        if problem.isGoalState(state):
            return path

        for successor, action, _step_cost in problem.getSuccessors(state):
            if successor not in visited:
                stack.push((successor, path + [action]))

    return []


def breadthFirstSearch(problem: SearchProblem) -> List[Any]:
    """
    Căutare în lățime (BFS) care garantează drumul cu număr minim de pași.
    Autor: <completați numele autorului>
    """
    from util import Queue

    start_state = problem.getStartState()
    if problem.isGoalState(start_state):
        return []

    queue: Queue = Queue()
    queue.push((start_state, []))
    visited = {start_state}

    while not queue.isEmpty():
        state, path = queue.pop()
        if problem.isGoalState(state):
            return path

        for successor, action, _step_cost in problem.getSuccessors(state):
            if successor not in visited:
                visited.add(successor)
                queue.push((successor, path + [action]))

    return []


def uniformCostSearch(problem: SearchProblem) -> List[Any]:
    """
    Căutare cu cost uniform (UCS) folosind un PriorityQueue pe baza lui g(n).
    Autor: <completați numele autorului>
    """
    from util import PriorityQueue

    start_state = problem.getStartState()
    if problem.isGoalState(start_state):
        return []

    frontier: PriorityQueue = PriorityQueue()
    frontier.push((start_state, [] , 0.0), 0.0)
    best_g = {start_state: 0.0}

    while not frontier.isEmpty():
        state, path, g_cost = frontier.pop()

        # Dacă avem o cale mai bună deja cunoscută, sar peste această intrare.
        if best_g.get(state, float('inf')) < g_cost:
            continue

        if problem.isGoalState(state):
            return path

        for successor, action, step_cost in problem.getSuccessors(state):
            new_g = g_cost + step_cost
            if new_g < best_g.get(successor, float('inf')):
                best_g[successor] = new_g
                frontier.push((successor, path + [action], new_g), new_g)

    return []


def nullHeuristic(state: Any, problem: Optional[SearchProblem] = None) -> float:
    """Euristică nulă (admisibilă și consistentă)."""
    return 0.0


def aStarSearch(
    problem: SearchProblem, heuristic: Callable[[Any, Optional[SearchProblem]], float] = nullHeuristic
) -> List[Any]:
    """
    Căutare A* care folosește f(n) = g(n) + h(n).
    Autor: <completați numele autorului>
    """
    from util import PriorityQueue

    start_state = problem.getStartState()
    if problem.isGoalState(start_state):
        return []

    frontier: PriorityQueue = PriorityQueue()
    start_h = heuristic(start_state, problem)
    frontier.push((start_state, [], 0.0), start_h)

    best_g = {start_state: 0.0}

    while not frontier.isEmpty():
        state, path, g_cost = frontier.pop()

        if best_g.get(state, float('inf')) < g_cost:
            continue

        if problem.isGoalState(state):
            return path

        for successor, action, step_cost in problem.getSuccessors(state):
            new_g = g_cost + step_cost
            if new_g < best_g.get(successor, float('inf')):
                best_g[successor] = new_g
                f_cost = new_g + heuristic(successor, problem)
                frontier.push((successor, path + [action], new_g), f_cost)

    return []


# Alias-uri scurte pentru selecția funcțiilor prin argumentul `-a fn=...`
# Ex.: -a fn=dfs | fn=bfs | fn=ucs | fn=astar

dfs = depthFirstSearch
bfs = breadthFirstSearch
ucs = uniformCostSearch
astar = aStarSearch

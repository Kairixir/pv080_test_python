#!/usr/bin/env python3

# Povolene knihovny: typing, math, collections
# Z knihovny collections je povolena pouze datova struktura deque
# reprezentujici frontu. Pro jeji import pouzijte presne nasledujici radek:
# from collections import deque

from typing import List, Optional, Deque
from collections import deque
from math import inf


# IB002 Domaci uloha 11.
#
# Tento tyden bude vasim ukolem implementovat dva grafove algoritmy.
# Ukoly jsou zamereny na aplikace pruchodu grafem.
#
# Reprezentace grafu je stejna jako v ukolu cv11, tedy matici sousednosti.
# Matice je indexovana od [0][0], vrcholum odpovidaji cisla 0 .. graph.size-1.
# V matici je na indexu [u][v] hodnota True, pokud graf obsahuje hranu u -> v,
# jinak je tam hodnota False.
#
# Grafy (i neorientovane!) mohou obsahovat smycky (tj. situace, kdy v matici
# na indexu [u][u] je True) a mohou byt i nesouvisle.
#
# Pripomenuti prace s frontou typu deque:
# inicializace fronty: queue = deque() nebo queue = deque([seznam prvku])
# vlozeni prvku do fronty: queue.append(prvek)
# vybrani prvku z fronty: queue.popleft(prvek)
#
# Definici tridy Graph nijak nemodifikujte, ani nepridavejte zadne atributy.
# Zamerne se v teto uloze budete muset obejit bez pomocnych poli ve tride
# Graph; budete muset pouzit lokalni promenne a pripadne parametry v rekurzi.
#
# V teto uloze je zakazano pouzivat datove struktury set (mnoziny) a dict
# (slovniky). Uvedomte si, ze vrcholy grafu jsou vzdy cisla od 0 do size - 1.


class Graph:
    """Trida Graph drzi graf reprezentovany matici sousednosti.
    Atributy:
        size: velikost (pocet vrcholu) grafu
        matrix: matice sousednosti
                [u][v] reprezentuje hranu u -> v
    """
    __slots__ = ("size", "matrix")

    def __init__(self, size: int) -> None:
        self.size: int = size
        self.matrix: List[List[bool]] = [[False] * size for _ in range(size)]


# Ukol 1.
# Implementujte funkci colourable, ktera zjisti, zda je dany neorientovany graf
# obarvitelny dvema barvami tak, aby kazde dva sousedni vrcholy mely ruznou
# barvu.
#
# Neorientovany graf v nasi reprezentaci znamena, ze
#    graph.matrix[u][v] == graph.matrix[v][u] pro vsechny vrcholy u, v.

def colourable(graph: Graph) -> bool:
    """Zjisti, zda je zadany neorientovany graf obarvitelny dvema barvami.
    Vstup:
        graph - neorientovany graf typu Graph
    Vystup:
        True, pokud je graf obarvitelny dvema barvami
        False, jinak
    casova slozitost: O(n^2), kde n je pocet vrcholu grafu
    extrasekvencni prostorova slozitost: O(n), kde n je pocet vrcholu grafu
    """
    array = [[False, False, 0] for _ in range(graph.size)]
    queue = deque()
    for i in range(graph.size):
        if array[i][0] or array[i][1]:
            continue
        array[i][1] = True
        queue.append(i)
        if not checkBFSColourable(graph, queue, array):
            return False
    return True


def checkBFSColourable(graph: Graph, queue: deque, array) -> bool:
    key = queue.popleft()
    if graph.matrix[key][key]:
        return False
    array[key][0] = True
    length = 0
    for i in range(graph.size):
        if graph.matrix[key][i]:
            if array[i][1] and array[key][2] == array[i][2]:
                return False
            if array[i][1]:
                continue
            queue.append(i)
            array[i][2] = array[key][2] + 1
            length += 1
            array[i][1] = True
    if length == 0:
        return True
    else:
        ret_val = True
        for _ in range(length):
            ret_val = ret_val and checkBFSColourable(graph, queue, array)
            if not ret_val:
                return False
        return ret_val


# Ukol 2.
# Implementujte funkci compute_dependencies, ktera pro zadany orientovany graf
# spocita topologicke usporadani vrcholu, tj. ocislovani vrcholu takove, ze
# kazda hrana vede z vrcholu s nizsim cislem do vrcholu s vyssim cislem.
#
# Vystupem je pole zadavajici topologicke usporadani (ocislovani vrcholu),
# kde na prvni pozici (tedy s indexem 0) je vrchol nejmensi
# v tomto usporadani, tj. nevede do nej zadna hrana,
# a na posledni pozici vrchol nejvetsi, tj. nevede z nej zadna hrana.
# Pokud topologicke usporadani neexistuje, algoritmus vraci None.
#
# Priklad:
#    mejme graf s vrcholy 0, 1, 2 a hranami 0 -> 1, 2 -> 1, 2 -> 0;
#    vystupem bude pole (Pythonovsky seznam] [2, 0, 1]


def compute_dependencies(graph: Graph) -> Optional[List[int]]:
    """Spocita topologicke usporadani vrcholu v grafu.
    Vstup:
        graph - orientovany graf typu Graph
    Vystup:
        pole cisel reprezentujici topologicke usporadani vrcholu
        None, pokud zadne topologicke usporadani neexistuje
    casova slozitost: O(n^2), kde n je pocet vrcholu grafu
    extrasekvencni prostorova slozitost: O(n), kde n je pocet vrcholu grafu
    """
    topology = [[i, inf] for i in range(graph.size)]
    was_visited = [False for _ in range(graph.size)]
    result = []
    stack = []
    print(str_dot_graph(graph))
    for i in range(graph.size):
        if not was_visited[i]:
            find_roots(graph, i, stack, was_visited)
    queue = deque(stack)

    was_visited = [False for _ in range(graph.size)]
    if not stack:
        return None
    for key in stack:
        topology[key][1] = 0
        result.append(key)
        was_visited[key] = True

    if not do_search(graph, stack, topology, was_visited):
        return None
    if list(filter(lambda x: x[1] == inf, topology)):
        return None
    result = sorted(topology, key=lambda x: int(x[1]))
    result = list(map(lambda x: x[0], result))

    return result


def do_search(graph, stack, topology, was_visited):
    path = []
    while stack:
        node = stack.pop()
        if graph.matrix[node][node]:
            return False
        if node in path:
            return False
        path.append(node)
        for i in range(graph.size):
            if graph.matrix[node][i]:
                if not was_visited[i]:
                    was_visited[i] = True
                    stack.append(i)
                    topology[i][1] = topology[node][1] + 1
                    continue
                if topology[i][1] > topology[node][1] + 1:
                    topology[i][1] = topology[node][1] + 1
                    stack.append(i)
    return True


def find_roots(graph, node, roots: List[int], was_visited):
    is_root_node = True
    was_visited[node] = True
    for i in range(graph.size):
        if graph.matrix[i][node]:
            if not was_visited[i]:
                was_visited[i] = True
                find_roots(graph, i, roots, was_visited)
            is_root_node = False
    if is_root_node:
        roots.append(node)

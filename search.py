import heapq
from collections import deque
from node import Node

def BFS(initial_state):
    init_node = Node(initial_state)
    expanded = 0                             #compteur de noeuds explorés
    if initial_state.isGoal():
        return init_node, expanded         

    open_list = deque([init_node])   # file FIFO de noeuds
    open_states = {initial_state}    # états présents dans open_list
    closed = set()                   # états déjà explorés

    while open_list:
        current = open_list.popleft()
        expanded += 1                        
        open_states.discard(current.state)
        closed.add(current.state)

        for action, successor in current.state.successorFunction():
           
            if successor not in closed and successor not in open_states:
                child = Node(successor, current, action)
                if successor.isGoal():
                     return child, expanded 
                 
                open_list.append(child)
                open_states.add(successor)

    return None, expanded                    

def  AStar(initial_state, h):
    init_node = Node(initial_state)
    init_node.setF(h)                      # f = g + h(état initial)
    expanded = 0                           # compteur de noeuds explorés
    compteur = 0                           # départage les égalités de f dans le tas

    open_list = []                         # le tas : tuples (f, compteur, noeud)
    heapq.heappush(open_list, (init_node.f, compteur, init_node))
    open_nodes = {initial_state: init_node}   # état -> noeud actuellement dans Open
    closed = {}                               # état -> noeud déjà exploré

    while open_list:
        f, _, current = heapq.heappop(open_list)    # noeud de f minimal

        # ancien doublon (remplacé entre-temps par un meilleur) : on l'ignore
        if open_nodes.get(current.state) is not current:
            continue

        del open_nodes[current.state]
        expanded += 1

        if current.state.isGoal():         # test du but à l'extraction
            return current, expanded

        closed[current.state] = current

        for action, successor in current.state.successorFunction():
            child = Node(successor, current, action)   # g = g du parent + 1
            child.setF(h)                              # f = g + h

            inserer = False
            if successor not in open_nodes and successor not in closed:
                inserer = True                         # état nouveau
            elif successor in open_nodes and child.f < open_nodes[successor].f:
                inserer = True                         # meilleur que celui de Open
            elif successor in closed and child.f < closed[successor].f:
                del closed[successor]                  # on le retire de Closed
                inserer = True

            if inserer:
                compteur += 1
                heapq.heappush(open_list, (child.f, compteur, child))
                open_nodes[successor] = child

    return None, expanded
from collections import deque
from node import Node

def BFS(initial_state):
    init_node = Node(initial_state)
    if initial_state.isGoal():
        return init_node

    open_list = deque([init_node])   # file FIFO de noeuds
    open_states = {initial_state}    # états présents dans open_list
    closed = set()                   # états déjà explorés

    while open_list:
        current = open_list.popleft()
        open_states.discard(current.state)
        closed.add(current.state)

        for action, successor in current.state.successorFunction():
            if successor not in closed and successor not in open_states:
                child = Node(successor, current, action)
                if successor.isGoal():
                    return child
                open_list.append(child)
                open_states.add(successor)

    return None
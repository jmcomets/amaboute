def tarjan(vertices, neighbors):
    sccs = []

    stack = []
    on_stack = set()
    current_index = [0]
    indexes = {}
    lowlinks = {}

    def strongconnect(node):
        indexes[node] = current_index[0]
        lowlinks[node] = current_index[0]
        current_index[0] += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in neighbors(node):
            if neighbor not in indexes:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indexes[neighbor])

        if lowlinks[node] == indexes[node]:
            scc = []
            while True:
                new_node = stack.pop()
                on_stack.remove(new_node)
                scc.append(new_node)
                if new_node == node:
                    break
            sccs.append(scc)

    for node in vertices:
        if node not in indexes:
            strongconnect(node)

    return sccs

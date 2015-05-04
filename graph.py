import pqdict

class Graph(dict):
    def __init__(self, nodes=()):
        if type(nodes) == dict:
            super(Graph, self).__init__(nodes)
        else:
            for node in nodes:
                self.add_node(node)

    def add_node(self, node_a):
        assert node_a not in self
        self[node_a] = {}

    def remove_node(self, node_a):
        assert node_a in self
        for node_b in self[node_a]:
            del self[node_b][node_a]
        del self[node_a]

    def copy(self):
        return self.__class__(super(Graph, self)).copy()
    
    def is_connected(self, node_a, node_b):
        return node_a in self[node_b]

    def dijkstra(self, source, target):
        distance = {}
        previous = {}

        pque = pqdict.PQDict()
        for node in self:
            if node == source:
                pque[node] = 0
            else:
                pque[node] = float("inf")

        for (node, node_distance) in pque.iteritems():
            distance[node] = node_distance
            if node == target:
                break

            # XXX: hack
            if node != source and not node.circulatable:
                continue

            for neighbor_node in self[node]:
                if neighbor_node not in pque:
                    continue
                try:
                    alt_dist = distance[node] + self[node][neighbor_node]
                except TypeError:
                    alt_dist = distance[node] + 1
                if alt_dist < pque[neighbor_node]:
                    pque[neighbor_node] = alt_dist
                    previous[neighbor_node] = node
        return (distance, previous)

    def path(self, source, target):
        (distance, previous) = self.dijkstra(source, target)
        if not previous:
            return None
        total_distance = distance[target]
        node = target
        path = [node]
        while node != source:
            if node not in previous:
                return None
            node = previous[node]
            path.append(node)
        path.reverse()
        return (path, total_distance)

class DirectedGraph(Graph):
    def connect(self, node_a, node_b, weight=1):
        self[node_a][node_b] = weight

    def disconnect(self, node_a, node_b):
        assert node_b in self[node_a]
        del self[node_a][node_b]

class BidirectedGraph(Graph):
    def connect(self, node_a, node_b, weight=1):
        self[node_a][node_b] = weight
        self[node_b][node_a] = weight

    def disconnect(self, node_a, node_b):
        assert node_b in self[node_a]
        assert node_a in self[node_b]
        del self[node_a][node_b]
        del self[node_b][node_a]



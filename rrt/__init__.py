import numpy as np
from collections import namedtuple
from sklearn.neighbors import NearestNeighbors

RectShape = namedtuple('RectShape', ['x', 'y', 'width', 'height'])
CircleShape = namedtuple('CircleShape', ['x', 'y', 'radius'])


class Vertex:
    """
    Base vertex class
    contains:
    (x, y) as position
    is_available as check for final vertex
    """
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def is_available(self, v: "Vertex", eps: float) -> bool:
        return abs(self._x - v.x) <= eps and abs(self._y - v.y) <= eps


class Edge:
    """
    Edge connects two verts
    contains:
    v1, v2
    """
    def __init__(self, v1: "Vertex", v2: "Vertex"):
        self._v1 = v1
        self._v2 = v2

    @property
    def v1(self):
        return self._v1

    @property
    def v2(self):
        return self._v2

    def __len__(self):
        return (self._v1.x - self._v2.x)**2 + (self._v1.y - self._v2.y)**2


class PolygonShape:
    def __init__(self, vertex_list: list):
        self.lines = {'line_{}'.format(_id): (vertex_pair[0], vertex_pair[1]) for _id, vertex_pair in enumerate(vertex_list)}
        self.lines['line_{}'.format(len(self.lines))] = (self.lines['line_{}'.format(len(self.lines) - 1)][1], self.lines['line_0'][0])
    
    def get_lines(self) -> list:
        return list(self.lines.values())
    
    def get_line(self) -> tuple:
        for line_id in self.lines:
            yield self.lines[line_id]
            
    def __repr__(self):
        return str(self.lines)


class GlobalTree:
    """
    main tree structure for searching
    contains:
    vertex container
    edge container
    search - tries to get to final vert through generating v_rand
    expand - adds new v_rand to vertex container
    get_nearest - tries to find nearest vert to v_rand
    """
    def __init__(self):
        self._verts = list()
        self._edges = list()
        self._verts_xy = list()
        self._nn_searcher = NearestNeighbors(n_neighbors=1, algorithm='kd_tree')
        self._way_to_final = []

    @staticmethod
    def generate(base: "Vertex", radius: tuple, samples: int = 1):
        return np.random.normal(loc=(base.x, base.y), scale=radius, size=(samples, 2))

    def add_vertex(self, vertex: Vertex) -> None:
        self._verts.append(vertex)
        self._verts_xy.append([vertex.x, vertex.y])
        self._nn_searcher.fit(np.array(self._verts_xy))
        
    def add_edge(self, v1: Vertex, v2: Vertex) -> None:
        self._edges.append(Edge(v1, v2))
        
    @property
    def edges(self):
        return self._edges
        
    def find_nearest(self, vertex: Vertex) -> np.array:
        nn_distances, nn_indexes = self._nn_searcher.kneighbors([[vertex.x, vertex.y]], return_distance=True)
        return nn_distances, nn_indexes
    
    def get_vertex_by_index(self, index) -> Vertex:
        return self._verts[index]
        
    @property
    def verts(self):
        return self._verts
    
    def find_way_to_start(self, vertex: Vertex):
        for edge in self._edges:
            if vertex == self._verts[0]:
                print("FINAL")
                self._way_to_final.append(vertex)
                return self._way_to_final
            if vertex == edge.v2:
                # print('recursion')
                self._way_to_final.append(vertex)
                return self.find_way_to_start(edge.v1)
            
    def remove_last_step(self, steps):
        if len(self._edges) > steps:
            for _ in range(steps):
                self._verts.remove(self._verts[-1])
                self._edges.remove(self._edges[-1])
                self._verts_xy.remove(self._verts_xy[-1])
        self._nn_searcher.fit(np.array(self._verts_xy))


class ShapeFactory:
    """
    default shape figure
    contains rect, circle shapes
    """
    @staticmethod
    def create_rect(cords: tuple, sizes: tuple):
        assert len(cords) == 2
        assert len(sizes) == 2
        return RectShape(*cords, *sizes)

    # @staticmethod
    # def create_circle(cords: tuple, sizes: int):
    #     assert len(cords) == 2
    #     assert sizes > 0
    #     return CircleShape(cords[0], cords[1], sizes)


class Card:
    """
    configuration of search field
    contains:
    shapes: list() - off shape on field
    bool: intersection(vertex) - check for intersection with shapes
    """
    
    def __init__(self, borders: list):
        assert len(borders) == 2
        self.border_x = borders[0]
        self.border_y = borders[1]
        self._shapes = list()

    @staticmethod
    def rect_intersection(rect1: namedtuple, rect2: namedtuple) -> bool:
        return True

    def add_shape(self, shape):
        if True: #self.is_able_to_place(shape):
            self._shapes.append(shape)
        return None

    def is_intersect(self, vertex: Vertex):
        for shape in self._shapes:
            if shape.x < vertex.x < shape.x + shape.width and shape.y < vertex.y < shape.y + shape.height:
                return True
        return False
    
    @staticmethod
    def area(v1: Vertex, v2: Vertex, v3: Vertex) -> float:
        return (v2.x - v1.x) * (v3.y - v1.y) - (v2.y - v1.y) * (v3.x - v1.x)
    
    @staticmethod
    def intersect_1 (a, b, c, d):
        if a > b:
            a, b = b, a
        if c > d:
            c, d = d, c
        return np.max([a, c]) <= np.min([b, d])
    
    @staticmethod
    def is_intersect_lines(v1: Vertex, v2: Vertex, v3: Vertex, v4: Vertex) -> bool:
        return Card.intersect_1(v1.x, v2.x, v3.x, v4.x) and Card.intersect_1(v1.y, v2.y, v3.y, v4.y) and \
               np.multiply(Card.area(v1, v2, v3), Card.area(v1, v2, v4)) <= 0 and np.multiply(Card.area(v3, v4, v1), Card.area(v3, v4, v2)) <= 0
    
    @staticmethod
    def is_intersect_with_poly(v1: Vertex, v2: Vertex, shape: PolygonShape) -> bool:
        for line in shape.get_line():
            if Card.is_intersect_lines(v1, v2, Vertex(line[0].x, line[0].y), Vertex(line[1].x, line[1].y)):
                return True
        return False
    
    def is_able_to_place(self, base: Vertex, new: Vertex) -> bool:
        if self.border_x[0] < new.x < self.border_x[1] and self.border_y[0] < new.y < self.border_y[1]:
            for shape in self._shapes:
                if self.is_intersect_with_poly(base, new, shape):
                    return False
            return True
        return False
    
    def is_available(self, v1: Vertex, v2: Vertex) -> bool:
        if self.border_x[0] < v2.x < self.border_x[1] and self.border_y[0] < v2.y < self.border_y[1]:
            for shape in self._shapes:
                if self.is_intersect_with_poly(v1, v2, shape):
                    return False
            return True
        return False

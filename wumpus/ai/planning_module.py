from heapdict import heapdict
from ..config.settings import DIRECTIONS, DIRECTION_VECTORS

class PlanningModule:
    def __init__(self): 
        self.space = {(0,0)} 
        self.solution = []       

    def heuristic(self, pos, goal):
        return abs(goal[0] - pos[0]) + abs(goal[1] - pos[1])

    def get_cost(self, cur_pos, to_pos, cur_dir):
        dx, dy = to_pos[0] - cur_pos[0], to_pos[1] - cur_pos[1]
        desired_dir = None
        for d in DIRECTIONS:
            if DIRECTION_VECTORS[(dx, dy)] == d:
                desired_dir = d
                break

        return 1 if desired_dir == cur_dir else 2

    def add_safe_cell(self, cell):
        self.space.add(cell)

    def _get_next_pos(self, cur_pos):
        # Adjacent moves in 4 directions
        x, y = cur_pos
        adj = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [cell for cell in adj if cell in self.space]

    def _reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def find_route(self, start, goal, start_dir):
        open_set = heapdict()
        came_from = {}
        g_score = {}
        directions_map = {}

        g_score[start] = 0
        open_set[start] = self.heuristic(start, goal)
        directions_map[start] = start_dir

        visited = set()

        while open_set:
            current, _ = open_set.popitem()

            if current == goal:
                self.solution = self._reconstruct_path(came_from, current)
                return self.solution, g_score[goal]

            if current in visited:
                continue
            visited.add(current)

            cur_dir = directions_map[current]

            for neighbor in self._get_next_pos(current):
                if neighbor in visited:
                    continue

                tentative_g = g_score[current] + self.get_cost(current, neighbor, cur_dir)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal)
                    open_set[neighbor] = f_score
                    came_from[neighbor] = current

                    dx, dy = neighbor[0] - current[0], neighbor[1] - current[1]
                    for d in DIRECTIONS:
                        if DIRECTION_VECTORS[(dx, dy)] == d:
                            directions_map[neighbor] = d
                            break

        return None, None
    def get_nearest_goal_route(self, start, goals, start_dir):
        cur_route = []
        cur_goal = (-1, -1)
        min_g = float('inf')
        for goal in goals:
            temp_route, g = self.find_route(start, goal, start_dir)
            if g is None:
                continue
            if g < min_g:
                min_g = g
                cur_route = temp_route.copy()
                cur_goal = goal
        return cur_goal, cur_route
                


            

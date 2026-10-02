# agent.py
import random
import math
from collections import deque
import heapq


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:
    """Agent that supports BFS, DFS, UCS, and A* search."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance between two positions."""
        x1, y1 = pos
        x2, y2 = goal

        return abs(x1 - x2) + abs(y1 - y2)

    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance between two positions."""
        x1, y1 = pos
        x2, y2 = goal

        return math.sqrt(
            (x1 - x2) ** 2 +
            (y1 - y2) ** 2
        )

    def bfs_search(self, start, goal, percept):
        """Breadth-First Search using a FIFO queue."""

        frontier = deque([(start, [])])
        reached = {start}

        while frontier:
            current, path = frontier.popleft()

            if current == goal:
                return path

            for next_state, action in self.get_neighbors(current, percept):
                if next_state not in reached:
                    reached.add(next_state)

                    frontier.append(
                        (next_state, path + [action])
                    )

        return []

    def dfs_search(self, start, goal, percept):
        """Depth-First Search using a LIFO stack."""

        frontier = [(start, [])]
        reached = {start}

        while frontier:
            current, path = frontier.pop()

            if current == goal:
                return path

            for next_state, action in self.get_neighbors(current, percept):
                if next_state not in reached:
                    reached.add(next_state)

                    frontier.append(
                        (next_state, path + [action])
                    )

        return []

    def ucs_search(self, start, goal, percept):
        """Uniform-Cost Search using a priority queue."""

        frontier = [(0, start, [])]
        reached = {}

        while frontier:
            cost, current, path = heapq.heappop(frontier)

            if current in reached and reached[current] <= cost:
                continue

            reached[current] = cost

            if current == goal:
                return path

            for next_state, action in self.get_neighbors(current, percept):

                # Each movement currently has a cost of 1.
                new_cost = cost + 1

                if (
                    next_state not in reached
                    or new_cost < reached[next_state]
                ):
                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            next_state,
                            path + [action]
                        )
                    )

        return []

    # Lab 04: A* Search using g(n) + h(n).
    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):
        """A* Search using g(n) + h(n)."""

        # Lab 04: Create the priority queue and reached-state set.
        frontier = []
        reached_states = set()

        # Lab 04: Calculate the initial heuristic value.
        if heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(start_pos, goal_pos)
        else:
            h_cost = self.manhattan_distance(start_pos, goal_pos)

        # Lab 04: The initial node has g(n) = 0 and f(n) = g(n) + h(n).
        heapq.heappush(
            frontier,
            (h_cost, 0, start_pos, [])
        )

        while frontier:

            # Lab 04: Select the node with the lowest f(n) value.
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            # Lab 04: Return the path when the goal is reached.
            if current_pos == goal_pos:
                return path_taken

            # Lab 04: Skip states that have already been processed.
            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            x, y = current_pos

            # Lab 04: A* checks the four possible movement directions.
            moves = {
                'Up': (x, y + 1),
                'Down': (x, y - 1),
                'Left': (x - 1, y),
                'Right': (x + 1, y)
            }

            for action, next_pos in moves.items():

                nx, ny = next_pos

                # Lab 04: Ignore positions outside the grid.
                if not (
                    0 <= nx < grid_size[0]
                    and 0 <= ny < grid_size[1]
                ):
                    continue

                # Lab 04: Ignore positions containing walls.
                if next_pos in walls:
                    continue

                # Lab 04: Ignore states that have already been reached.
                if next_pos in reached_states:
                    continue

                # Lab 04: Every movement has a cost of 1.
                new_g_cost = g_cost + 1

                # Lab 04: Calculate h(n) using the selected heuristic.
                if heuristic_type == 'euclidean':
                    new_h_cost = self.euclidean_distance(
                        next_pos,
                        goal_pos
                    )
                else:
                    new_h_cost = self.manhattan_distance(
                        next_pos,
                        goal_pos
                    )

                # Lab 04: Calculate f(n) = g(n) + h(n).
                new_f_cost = new_g_cost + new_h_cost

                # Lab 04: Add the new node to the A* priority queue.
                heapq.heappush(
                    frontier,
                    (
                        new_f_cost,
                        new_g_cost,
                        next_pos,
                        path_taken + [action]
                    )
                )

        return []

    def get_neighbors(self, position, percept):
        """Generate valid neighboring states and their actions."""

        x, y = position

        moves = {
            'Up': (x, y + 1),
            'Down': (x, y - 1),
            'Left': (x - 1, y),
            'Right': (x + 1, y)
        }

        walls = set(percept['walls'])
        width, height = percept['grid_size']

        neighbors = []

        for action, next_state in moves.items():

            nx, ny = next_state

            # Check grid boundaries and walls
            if (
                0 <= nx < width
                and 0 <= ny < height
                and next_state not in walls
            ):
                neighbors.append(
                    (next_state, action)
                )

        return neighbors

    def sense_and_act(self, percept):

        # If there is no current plan, create a new one
        if not self.plan:

            current_position = tuple(percept['agent_pos'])
            all_food = percept['all_food']

            # If there is no food remaining, do nothing
            if not all_food:
                return 'Up'

            # Lab 04 integration:
            # If the agent is already standing on food, eat it.
            if current_position in all_food:
                return 'Eat'

            # Find the closest food pellet using Manhattan distance
            target = min(
                all_food,
                key=lambda food:
                    abs(food[0] - current_position[0]) +
                    abs(food[1] - current_position[1])
            )

            # Select the search algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(
                    current_position,
                    tuple(target),
                    percept
                )

            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(
                    current_position,
                    tuple(target),
                    percept
                )

            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(
                    current_position,
                    tuple(target),
                    percept
                )

            # Lab 04: Use A* search when AStar is selected.
            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(
                    current_position,
                    tuple(target),
                    percept['walls'],
                    percept['grid_size'],
                    heuristic_type='manhattan'
                )

        # Execute the first action in the plan
        if self.plan:
            return self.plan.pop(0)

        # Fallback if no path exists
        return 'Up'
# agent.py
import random
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
    """Agent that supports BFS, DFS, and UCS search."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

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

        # Execute the first action in the plan
        if self.plan:
            return self.plan.pop(0)

        # Fallback if no path exists
        return 'Up'
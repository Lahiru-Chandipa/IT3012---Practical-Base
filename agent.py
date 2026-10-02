# agent.py

import random
import math
from collections import deque
import heapq

from logic_engine import KnowledgeBase


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

        # Lab 05: Knowledge Base
        self.kb = KnowledgeBase()

        # Rule 1:
        # TargetVisible AND HasDust -> SafeToEngage
        self.kb.tell_rule(
            ['TargetVisible', 'HasDust'],
            'SafeToEngage'
        )

        # Rule 2:
        # SafeToEngage AND BloodseekerMissing -> Retreat
        self.kb.tell_rule(
            ['SafeToEngage', 'BloodseekerMissing'],
            'Retreat'
        )

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

            for next_state, action in self.get_neighbors(
                current,
                percept
            ):
                if next_state not in reached:

                    reached.add(next_state)

                    frontier.append(
                        (
                            next_state,
                            path + [action]
                        )
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

            for next_state, action in self.get_neighbors(
                current,
                percept
            ):
                if next_state not in reached:

                    reached.add(next_state)

                    frontier.append(
                        (
                            next_state,
                            path + [action]
                        )
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

            for next_state, action in self.get_neighbors(
                current,
                percept
            ):
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

    # Lab 05: Knowledge Base feasibility check
    def check_tile_feasibility(self, tile_facts):
        """
        Check whether a candidate tile is logically feasible
        using the Knowledge Base.
        """

        # Clear facts from the previous candidate tile
        self.kb.clear_facts()

        # Add the facts associated with this tile
        for fact in tile_facts:
            self.kb.tell_fact(fact)

        # Apply forward chaining
        self.kb.forward_chain()

        # If Retreat is derived, reject this tile
        return 'Retreat' not in self.kb.facts

    # Lab 04 + Lab 05: A* Search
    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan',
        tile_facts=None
    ):
        """
        A* Search using f(n) = g(n) + h(n).

        Lab 05 adds a Knowledge Base feasibility check
        before a candidate tile is added to the frontier.
        """

        frontier = []
        reached_states = set()

        # Calculate initial heuristic
        if heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(
                start_pos,
                goal_pos
            )
        else:
            h_cost = self.manhattan_distance(
                start_pos,
                goal_pos
            )

        # Initial node:
        # (f_cost, g_cost, position, path)
        heapq.heappush(
            frontier,
            (
                h_cost,
                0,
                start_pos,
                []
            )
        )

        while frontier:

            f_cost, g_cost, current_pos, path_taken = (
                heapq.heappop(frontier)
            )

            # Goal reached
            if current_pos == goal_pos:
                return path_taken

            # Skip already expanded states
            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            x, y = current_pos

            moves = {
                'Up': (x, y + 1),
                'Down': (x, y - 1),
                'Left': (x - 1, y),
                'Right': (x + 1, y)
            }

            for action, next_pos in moves.items():

                nx, ny = next_pos

                # Check grid boundaries
                if not (
                    0 <= nx < grid_size[0]
                    and 0 <= ny < grid_size[1]
                ):
                    continue

                # Check walls
                if next_pos in walls:
                    continue

                # Check already expanded states
                if next_pos in reached_states:
                    continue

                # Lab 05:
                # Check logical feasibility using Knowledge Base
                if tile_facts is not None:

                    facts_for_tile = tile_facts.get(
                        next_pos,
                        []
                    )

                    if not self.check_tile_feasibility(
                        facts_for_tile
                    ):
                        continue

                # Existing Lab 04 A* logic
                new_g_cost = g_cost + 1

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

                new_f_cost = new_g_cost + new_h_cost

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

            if (
                0 <= nx < width
                and 0 <= ny < height
                and next_state not in walls
            ):
                neighbors.append(
                    (
                        next_state,
                        action
                    )
                )

        return neighbors

    def sense_and_act(self, percept):

        if not self.plan:

            current_position = tuple(
                percept['agent_pos']
            )

            all_food = percept['all_food']

            if not all_food:
                return 'Up'

            # Find the closest food using Manhattan distance
            target = min(
                all_food,
                key=lambda food:
                    abs(
                        food[0] -
                        current_position[0]
                    )
                    +
                    abs(
                        food[1] -
                        current_position[1]
                    )
            )

            # Existing Lab 02 / Lab 03 / Lab 04 algorithms
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

            # Lab 04 + Lab 05
            elif self.active_algo == 'AStar':

                self.plan = self.astar_search(
                    current_position,
                    tuple(target),
                    percept['walls'],
                    percept['grid_size'],
                    heuristic_type='manhattan',
                    tile_facts=percept.get(
                        'tile_facts'
                    )
                )

        if self.plan:

            return self.plan.pop(0)

        return 'Up'
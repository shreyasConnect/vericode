"""
TASK-003: Dependency Graph Sorter & Cycle Detection Refactor (Refactoring & Architecture).
"""

from vericode.tasks.task_spec import TaskSpec

BASE_CODE = '''"""
Legacy Dependency Graph Topological Sorter.
FLAW: Recursive DFS causes RecursionError on deep graphs (>1000 nodes)
and fails to handle cycle identification cleanly.
"""

from typing import Dict, List, Set

class CycleDetectedError(Exception):
    def __init__(self, message: str, cycle: List[str] = None):
        super().__init__(message)
        self.cycle = cycle or []

class DependencyGraph:
    def __init__(self):
        self.adj: Dict[str, List[str]] = {}

    def add_dependency(self, parent: str, child: str) -> None:
        """Indicates that 'child' depends on 'parent' (parent must execute before child)."""
        if parent not in self.adj:
            self.adj[parent] = []
        if child not in self.adj:
            self.adj[child] = []
        self.adj[parent].append(child)

    def resolve_order(self) -> List[str]:
        # Legacy flawed recursive DFS
        visited: Set[str] = set()
        stack: Set[str] = set()
        order: List[str] = []

        def dfs(node: str):
            if node in stack:
                raise CycleDetectedError(f"Cycle detected at node {node}")
            if node in visited:
                return
            stack.add(node)
            visited.add(node)
            for neighbor in self.adj.get(node, []):
                dfs(neighbor)
            stack.remove(node)
            order.append(node)

        for node in list(self.adj.keys()):
            if node not in visited:
                dfs(node)

        return order[::-1]
'''

GOLDEN_SOLUTION = '''"""
Modern Dependency Graph Topological Sorter.
REFACTORED: Implemented using Kahn's iterative algorithm (in-degree BFS).
Guarantees O(V + E) complexity without recursion depth limits.
"""

from collections import deque
from typing import Dict, List, Set

class CycleDetectedError(Exception):
    def __init__(self, message: str, cycle: List[str] = None):
        super().__init__(message)
        self.cycle = cycle or []

class DependencyGraph:
    def __init__(self):
        self.adj: Dict[str, List[str]] = {}

    def add_dependency(self, parent: str, child: str) -> None:
        """Indicates that 'child' depends on 'parent' (parent must execute before child)."""
        if parent not in self.adj:
            self.adj[parent] = []
        if child not in self.adj:
            self.adj[child] = []
        self.adj[parent].append(child)

    def resolve_order(self) -> List[str]:
        in_degree: Dict[str, int] = {node: 0 for node in self.adj}
        for parent, children in self.adj.items():
            for child in children:
                in_degree[child] = in_degree.get(child, 0) + 1

        queue = deque([node for node, deg in in_degree.items() if deg == 0])
        order: List[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for child in self.adj.get(node, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(order) < len(in_degree):
            unresolved = [node for node, deg in in_degree.items() if deg > 0]
            raise CycleDetectedError("Graph contains circular dependencies", cycle=unresolved)

        return order
'''

PUBLIC_TESTS = '''
from dependency_graph import DependencyGraph, CycleDetectedError

def test_simple_dag():
    graph = DependencyGraph()
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    graph.add_dependency("A", "C")
    order = graph.resolve_order()
    assert order.index("A") < order.index("B")
    assert order.index("B") < order.index("C")

def test_cycle_detection():
    graph = DependencyGraph()
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    graph.add_dependency("C", "A")
    try:
        graph.resolve_order()
        assert False, "Should raise CycleDetectedError"
    except CycleDetectedError:
        pass

if __name__ == "__main__":
    test_simple_dag()
    test_cycle_detection()
    print("ALL_PUBLIC_TESTS_PASSED")
'''

HIDDEN_TESTS = '''
import sys
from dependency_graph import DependencyGraph, CycleDetectedError

def test_deep_recursion_resilience():
    # Construct a 2,500-node linear chain that crushes recursive implementations
    chain_length = 2500
    graph = DependencyGraph()
    for i in range(chain_length):
        graph.add_dependency(f"node_{i}", f"node_{i+1}")

    order = graph.resolve_order()
    assert len(order) == chain_length + 1
    assert order[0] == "node_0"
    assert order[-1] == f"node_{chain_length}"

def test_diamond_dag():
    graph = DependencyGraph()
    graph.add_dependency("root", "left")
    graph.add_dependency("root", "right")
    graph.add_dependency("left", "sink")
    graph.add_dependency("right", "sink")
    order = graph.resolve_order()
    assert order[0] == "root"
    assert order[-1] == "sink"

if __name__ == "__main__":
    test_deep_recursion_resilience()
    test_diamond_dag()
    print("ALL_HIDDEN_TESTS_PASSED")
'''

TASK_003 = TaskSpec(
    task_id="TASK-003",
    title="Dependency Graph Sorter & Cycle Detection Refactor",
    category="refactor",
    difficulty="hard",
    description=(
        "Refactor the legacy recursive DFS in `dependency_graph.py` to an iterative algorithm (e.g. Kahn's algorithm). "
        "The current implementation crashes with `RecursionError` on deep graphs (>1000 nodes). "
        "The refactored solution must handle arbitrary graph depths in $O(V + E)$ time and cleanly raise "
        "`CycleDetectedError` on cyclic dependency structures."
    ),
    target_filename="dependency_graph.py",
    base_code=BASE_CODE,
    public_tests=PUBLIC_TESTS,
    hidden_tests=HIDDEN_TESTS,
    golden_solution=GOLDEN_SOLUTION,
    tags=["graph-theory", "topological-sort", "refactoring", "kahn-algorithm"],
)

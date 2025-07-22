"""
Graph Algorithms for Knowledge Graph - Phase 3.3
Helper algorithms for graph operations like BFS, shortest path, and clustering.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class GraphAlgorithms:
    """Collection of graph algorithms for knowledge graph operations."""
    
    @staticmethod
    def breadth_first_search(adjacency: Dict[str, List[str]], start: str, max_depth: int = 2) -> Dict[str, int]:
        """
        Perform breadth-first search from a starting node.
        
        Args:
            adjacency: Adjacency list representation of the graph
            start: Starting node ID
            max_depth: Maximum depth to explore
            
        Returns:
            Dictionary mapping node IDs to their depths
        """
        if start not in adjacency:
            return {}
        
        visited = {}
        queue = deque([(start, 0)])
        visited[start] = 0
        
        while queue:
            current, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
            
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    visited[neighbor] = depth + 1
                    queue.append((neighbor, depth + 1))
        
        return visited
    
    @staticmethod
    def shortest_path_bfs(adjacency: Dict[str, List[str]], source: str, target: str) -> List[str]:
        """
        Find shortest path between two nodes using BFS.
        
        Args:
            adjacency: Adjacency list representation of the graph
            source: Source node ID
            target: Target node ID
            
        Returns:
            List of node IDs representing the shortest path, or empty list if no path exists
        """
        if source == target:
            return [source]
        
        if source not in adjacency or target not in adjacency:
            return []
        
        # BFS with path tracking
        queue = deque([(source, [source])])
        visited = {source}
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in adjacency.get(current, []):
                if neighbor == target:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    @staticmethod
    def find_connected_components(adjacency: Dict[str, List[str]]) -> List[List[str]]:
        """
        Find all connected components in the graph.
        
        Args:
            adjacency: Adjacency list representation of the graph
            
        Returns:
            List of lists, where each inner list contains node IDs of a connected component
        """
        visited = set()
        components = []
        
        def dfs(node: str, component: List[str]):
            if node in visited:
                return
            visited.add(node)
            component.append(node)
            
            for neighbor in adjacency.get(node, []):
                dfs(neighbor, component)
        
        for node in adjacency:
            if node not in visited:
                component = []
                dfs(node, component)
                if len(component) > 1:  # Only include components with multiple nodes
                    components.append(component)
        
        return components
    
    @staticmethod
    def find_clusters_by_type(adjacency: Dict[str, List[str]], 
                             node_types: Dict[str, str], 
                             target_type: Optional[str] = None) -> List[List[str]]:
        """
        Find clusters of nodes, optionally filtered by type.
        
        Args:
            adjacency: Adjacency list representation of the graph
            node_types: Dictionary mapping node IDs to their types
            target_type: Optional type to filter by
            
        Returns:
            List of lists, where each inner list contains node IDs of a cluster
        """
        # Filter nodes by type if specified
        if target_type:
            filtered_adjacency = {}
            for node, neighbors in adjacency.items():
                if node_types.get(node) == target_type:
                    filtered_adjacency[node] = [
                        neighbor for neighbor in neighbors 
                        if node_types.get(neighbor) == target_type
                    ]
        else:
            filtered_adjacency = adjacency
        
        return GraphAlgorithms.find_connected_components(filtered_adjacency)
    
    @staticmethod
    def calculate_degree_centrality(adjacency: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Calculate degree centrality for all nodes.
        
        Args:
            adjacency: Adjacency list representation of the graph
            
        Returns:
            Dictionary mapping node IDs to their degree centrality scores
        """
        centrality = {}
        total_nodes = len(adjacency)
        
        if total_nodes <= 1:
            return {node: 0.0 for node in adjacency}
        
        for node, neighbors in adjacency.items():
            centrality[node] = len(neighbors) / (total_nodes - 1)
        
        return centrality
    
    @staticmethod
    def calculate_betweenness_centrality(adjacency: Dict[str, List[str]], 
                                       sample_size: Optional[int] = None) -> Dict[str, float]:
        """
        Calculate betweenness centrality for all nodes.
        
        Args:
            adjacency: Adjacency list representation of the graph
            sample_size: Optional number of nodes to sample for performance
            
        Returns:
            Dictionary mapping node IDs to their betweenness centrality scores
        """
        nodes = list(adjacency.keys())
        if sample_size and sample_size < len(nodes):
            import random
            nodes = random.sample(nodes, sample_size)
        
        centrality = {node: 0.0 for node in adjacency}
        total_pairs = len(nodes) * (len(nodes) - 1)
        
        if total_pairs == 0:
            return centrality
        
        for i, source in enumerate(nodes):
            for target in nodes[i+1:]:
                if source != target:
                    # Find all shortest paths between source and target
                    paths = GraphAlgorithms._find_all_shortest_paths(adjacency, source, target)
                    
                    if paths:
                        # Count how many paths go through each node
                        for path in paths:
                            for node in path[1:-1]:  # Exclude source and target
                                if node in centrality:
                                    centrality[node] += 1.0 / len(paths)
        
        # Normalize
        for node in centrality:
            centrality[node] /= total_pairs
        
        return centrality
    
    @staticmethod
    def _find_all_shortest_paths(adjacency: Dict[str, List[str]], 
                                source: str, target: str) -> List[List[str]]:
        """
        Find all shortest paths between two nodes.
        
        Args:
            adjacency: Adjacency list representation of the graph
            source: Source node ID
            target: Target node ID
            
        Returns:
            List of all shortest paths
        """
        if source == target:
            return [[source]]
        
        # BFS to find shortest path length
        queue = deque([(source, 0)])
        visited = {source: 0}
        
        while queue:
            current, distance = queue.popleft()
            
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    visited[neighbor] = distance + 1
                    queue.append((neighbor, distance + 1))
        
        if target not in visited:
            return []
        
        shortest_length = visited[target]
        
        # DFS to find all paths of shortest length
        paths = []
        
        def dfs(current: str, path: List[str], remaining: int):
            if remaining == 0:
                if current == target:
                    paths.append(path[:])
                return
            
            for neighbor in adjacency.get(current, []):
                if neighbor not in path and visited.get(neighbor, float('inf')) <= remaining:
                    dfs(neighbor, path + [neighbor], remaining - 1)
        
        dfs(source, [source], shortest_length)
        return paths
    
    @staticmethod
    def find_communities_louvain(adjacency: Dict[str, List[str]], 
                                resolution: float = 1.0) -> Dict[str, int]:
        """
        Find communities using a simplified Louvain-like algorithm.
        
        Args:
            adjacency: Adjacency list representation of the graph
            resolution: Resolution parameter for community detection
            
        Returns:
            Dictionary mapping node IDs to their community IDs
        """
        if not adjacency:
            return {}
        
        # Initialize each node in its own community
        communities = {node: i for i, node in enumerate(adjacency.keys())}
        community_nodes = defaultdict(set)
        for node, comm in communities.items():
            community_nodes[comm].add(node)
        
        # Calculate modularity gain for moving nodes
        def calculate_modularity_gain(node: str, new_community: int) -> float:
            if communities[node] == new_community:
                return 0.0
            
            # Simplified modularity calculation
            old_community = communities[node]
            
            # Count edges within communities
            old_edges = sum(1 for neighbor in adjacency[node] 
                          if communities[neighbor] == old_community)
            new_edges = sum(1 for neighbor in adjacency[node] 
                          if communities[neighbor] == new_community)
            
            # Count total edges
            total_edges = len(adjacency[node])
            
            if total_edges == 0:
                return 0.0
            
            # Simplified gain calculation
            gain = (new_edges - old_edges) / total_edges
            return gain * resolution
        
        # Iterative optimization
        improved = True
        iterations = 0
        max_iterations = 10
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for node in adjacency:
                best_gain = 0.0
                best_community = communities[node]
                
                # Try moving to each neighboring community
                neighboring_communities = set()
                for neighbor in adjacency[node]:
                    neighboring_communities.add(communities[neighbor])
                
                for community in neighboring_communities:
                    gain = calculate_modularity_gain(node, community)
                    if gain > best_gain:
                        best_gain = gain
                        best_community = community
                
                # Move node if beneficial
                if best_gain > 0.0 and best_community != communities[node]:
                    old_community = communities[node]
                    communities[node] = best_community
                    
                    # Update community sets
                    community_nodes[old_community].discard(node)
                    community_nodes[best_community].add(node)
                    
                    improved = True
        
        return communities
    
    @staticmethod
    def calculate_graph_metrics(adjacency: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Calculate various graph metrics.
        
        Args:
            adjacency: Adjacency list representation of the graph
            
        Returns:
            Dictionary containing various graph metrics
        """
        if not adjacency:
            return {}
        
        # Basic metrics
        num_nodes = len(adjacency)
        num_edges = sum(len(neighbors) for neighbors in adjacency.values()) // 2
        
        # Average degree
        avg_degree = (2 * num_edges) / num_nodes if num_nodes > 0 else 0
        
        # Density
        max_edges = num_nodes * (num_nodes - 1) // 2
        density = num_edges / max_edges if max_edges > 0 else 0
        
        # Connected components
        components = GraphAlgorithms.find_connected_components(adjacency)
        num_components = len(components)
        
        # Largest component size
        largest_component_size = max(len(comp) for comp in components) if components else 0
        
        # Average path length (approximation)
        total_path_length = 0
        path_count = 0
        
        nodes = list(adjacency.keys())
        sample_size = min(100, len(nodes))  # Sample for performance
        
        import random
        sample_nodes = random.sample(nodes, sample_size) if len(nodes) > sample_size else nodes
        
        for i, source in enumerate(sample_nodes):
            for target in sample_nodes[i+1:]:
                path = GraphAlgorithms.shortest_path_bfs(adjacency, source, target)
                if path:
                    total_path_length += len(path) - 1
                    path_count += 1
        
        avg_path_length = total_path_length / path_count if path_count > 0 else 0
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'avg_degree': avg_degree,
            'density': density,
            'num_components': num_components,
            'largest_component_size': largest_component_size,
            'avg_path_length': avg_path_length
        } 
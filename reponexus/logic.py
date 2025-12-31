"""
Logic module: Analyzes code to find relationships between nodes based on
ports, URLs, and API calls.
"""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class RelationshipAnalyzer:
    """
    Analyzes code files to detect relationships between subsystems.
    """
    
    # Patterns to detect in code
    PORT_PATTERN = re.compile(r'(?:port|PORT)[\s:=]+(\d{4,5})')
    URL_PATTERN = re.compile(r'(?:https?://)?localhost:(\d{4,5})|127\.0\.0\.1:(\d{4,5})')
    API_URL_PATTERN = re.compile(r'["\']/(api|API)/([^"\']+)["\']')
    HTTP_METHOD_PATTERN = re.compile(r'\b(get|post|put|delete|patch|GET|POST|PUT|DELETE|PATCH)\s*\(["\']([^"\']+)["\']')
    IMPORT_PATTERN = re.compile(r'(?:from|import)\s+([a-zA-Z0-9_\.]+)')
    
    def __init__(self, nodes: Dict[str, Dict]):
        """
        Initialize the analyzer with node information.
        
        Args:
            nodes: Dictionary of nodes with their metadata
        """
        self.nodes = nodes
        self.port_to_node = {}  # Maps port numbers to nodes
        self.api_endpoints = {}  # Maps nodes to their API endpoints
        self.relationships = []  # List of (source, target, relationship_type) tuples
    
    def analyze(self) -> List[Tuple[str, str, str]]:
        """
        Analyze all nodes to detect relationships.
        
        Returns:
            List of tuples (source_node, target_node, relationship_type)
        """
        # First pass: identify ports and API endpoints exposed by each node
        for node_name, node_info in self.nodes.items():
            self._analyze_node_services(node_name, node_info)
        
        # Second pass: find connections between nodes
        for node_name, node_info in self.nodes.items():
            self._analyze_node_connections(node_name, node_info)
        
        return self.relationships
    
    def _analyze_node_services(self, node_name: str, node_info: Dict):
        """
        Analyze a node to identify services it exposes (ports, APIs).
        
        Args:
            node_name: Name of the node
            node_info: Node metadata including file paths
        """
        ports = set()
        api_endpoints = set()
        
        for file_path in node_info.get('file_paths', []):
            if not self._is_text_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Find ports
                    for match in self.PORT_PATTERN.finditer(content):
                        port = match.group(1)
                        ports.add(port)
                    
                    # Find API endpoint definitions
                    for match in self.API_URL_PATTERN.finditer(content):
                        endpoint = match.group(2)
                        api_endpoints.add(endpoint)
            except Exception:
                continue  # Skip files that can't be read
        
        # Map ports to this node
        for port in ports:
            self.port_to_node[port] = node_name
        
        # Store API endpoints
        if api_endpoints:
            self.api_endpoints[node_name] = api_endpoints
    
    def _analyze_node_connections(self, node_name: str, node_info: Dict):
        """
        Analyze a node to find connections to other nodes.
        
        Args:
            node_name: Name of the node
            node_info: Node metadata including file paths
        """
        connected_ports = set()
        api_calls = set()
        imports = set()
        
        for file_path in node_info.get('file_paths', []):
            if not self._is_text_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Find connections to localhost ports
                    for match in self.URL_PATTERN.finditer(content):
                        port = match.group(1) or match.group(2)
                        if port:
                            connected_ports.add(port)
                    
                    # Find API calls
                    for match in self.API_URL_PATTERN.finditer(content):
                        endpoint = match.group(2)
                        api_calls.add(endpoint)
                    
                    # Find HTTP method calls
                    for match in self.HTTP_METHOD_PATTERN.finditer(content):
                        url = match.group(2)
                        if url.startswith('/'):
                            api_calls.add(url.lstrip('/'))
                    
                    # Find imports (potential internal dependencies)
                    for match in self.IMPORT_PATTERN.finditer(content):
                        import_name = match.group(1)
                        imports.add(import_name)
            except Exception:
                continue
        
        # Create relationships based on port connections
        for port in connected_ports:
            if port in self.port_to_node:
                target_node = self.port_to_node[port]
                if target_node != node_name:
                    self.relationships.append((node_name, target_node, f'HTTP:{port}'))
        
        # Create relationships based on API calls
        for api_call in api_calls:
            for target_node, endpoints in self.api_endpoints.items():
                if target_node == node_name:
                    continue
                for endpoint in endpoints:
                    if api_call.startswith(endpoint) or endpoint.startswith(api_call):
                        self.relationships.append((node_name, target_node, 'API'))
                        break
        
        # Create relationships based on imports
        for import_name in imports:
            for target_node in self.nodes.keys():
                if target_node != node_name and target_node.lower() in import_name.lower():
                    self.relationships.append((node_name, target_node, 'Import'))
    
    def _is_text_file(self, file_path: Path) -> bool:
        """
        Check if a file is likely a text file based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is likely a text file
        """
        text_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rb', '.php',
            '.cs', '.cpp', '.c', '.h', '.hpp', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.vue', '.dart', '.yml', '.yaml', '.json', '.xml',
            '.md', '.txt', '.sh', '.bash', '.env', '.config'
        }
        return file_path.suffix.lower() in text_extensions
    
    def get_relationships(self) -> List[Tuple[str, str, str]]:
        """
        Get the detected relationships.
        
        Returns:
            List of tuples (source_node, target_node, relationship_type)
        """
        return self.relationships

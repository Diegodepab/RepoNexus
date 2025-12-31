"""
Renderer module: Generates Mermaid.js diagrams from analyzed data.
"""

from typing import Dict, List, Tuple


class MermaidRenderer:
    """
    Renders Mermaid.js diagrams from repository analysis data.
    """
    
    def __init__(self, nodes: Dict[str, Dict], relationships: List[Tuple[str, str, str]]):
        """
        Initialize the renderer with nodes and relationships.
        
        Args:
            nodes: Dictionary of nodes with their metadata
            relationships: List of (source, target, type) tuples
        """
        self.nodes = nodes
        self.relationships = relationships
    
    def render_graph(self) -> str:
        """
        Render a Mermaid.js graph diagram.
        
        Returns:
            Mermaid.js diagram as a string
        """
        lines = ['graph TD']
        
        # Add nodes with styling
        for node_name, node_info in self.nodes.items():
            languages = node_info.get('languages', [])
            lang_str = ', '.join(languages[:3])  # Limit to first 3 languages
            if len(languages) > 3:
                lang_str += '...'
            
            # Sanitize node name for Mermaid
            node_id = self._sanitize_node_id(node_name)
            
            # Create node label with languages
            if languages:
                label = f"{node_name}<br/>[{lang_str}]"
            else:
                label = node_name
            
            lines.append(f'    {node_id}["{label}"]')
        
        # Add relationships
        seen_relationships = set()
        for source, target, rel_type in self.relationships:
            source_id = self._sanitize_node_id(source)
            target_id = self._sanitize_node_id(target)
            
            # Avoid duplicate relationships
            rel_key = (source_id, target_id)
            if rel_key in seen_relationships:
                continue
            seen_relationships.add(rel_key)
            
            # Create relationship with label
            lines.append(f'    {source_id} -->|{rel_type}| {target_id}')
        
        # Add styling
        lines.append('')
        lines.append('    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px')
        
        return '\n'.join(lines)
    
    def render_c4_diagram(self) -> str:
        """
        Render a C4-style Mermaid diagram (more detailed).
        
        Returns:
            Mermaid.js C4 diagram as a string
        """
        lines = ['graph TD']
        
        # Categorize nodes by common patterns
        for node_name, node_info in self.nodes.items():
            node_id = self._sanitize_node_id(node_name)
            languages = node_info.get('languages', [])
            file_count = node_info.get('file_count', 0)
            
            # Determine node type based on name and languages
            node_type = self._guess_node_type(node_name, languages)
            
            # Create detailed label
            lang_str = ', '.join(languages[:2])
            if len(languages) > 2:
                lang_str += '...'
            
            label = f"{node_name}<br/>{node_type}"
            if languages:
                label += f"<br/>[{lang_str}]"
            label += f"<br/>{file_count} files"
            
            lines.append(f'    {node_id}["{label}"]')
            
            # Apply styling based on type
            if 'frontend' in node_type.lower():
                lines.append(f'    class {node_id} frontend')
            elif 'backend' in node_type.lower():
                lines.append(f'    class {node_id} backend')
            elif 'database' in node_type.lower():
                lines.append(f'    class {node_id} database')
        
        # Add relationships
        seen_relationships = set()
        for source, target, rel_type in self.relationships:
            source_id = self._sanitize_node_id(source)
            target_id = self._sanitize_node_id(target)
            
            rel_key = (source_id, target_id)
            if rel_key in seen_relationships:
                continue
            seen_relationships.add(rel_key)
            
            lines.append(f'    {source_id} -->|{rel_type}| {target_id}')
        
        # Add styling classes
        lines.append('')
        lines.append('    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px')
        lines.append('    classDef backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px')
        lines.append('    classDef database fill:#fff3e0,stroke:#e65100,stroke-width:2px')
        lines.append('    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px')
        
        return '\n'.join(lines)
    
    def _sanitize_node_id(self, node_name: str) -> str:
        """
        Sanitize node name to be a valid Mermaid ID.
        
        Args:
            node_name: Original node name
            
        Returns:
            Sanitized node ID
        """
        # Replace special characters with underscores
        sanitized = node_name.replace('-', '_').replace('.', '_').replace(' ', '_')
        # Remove any remaining non-alphanumeric characters
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
        return sanitized
    
    def _guess_node_type(self, node_name: str, languages: List[str]) -> str:
        """
        Guess the type of node based on name and languages.
        
        Args:
            node_name: Name of the node
            languages: List of programming languages detected
            
        Returns:
            String describing the node type
        """
        name_lower = node_name.lower()
        
        # Frontend indicators
        if any(keyword in name_lower for keyword in ['frontend', 'client', 'web', 'ui', 'app']):
            if any(lang in languages for lang in ['JavaScript', 'TypeScript', 'Vue', 'HTML']):
                return 'Frontend'
        
        # Backend indicators
        if any(keyword in name_lower for keyword in ['backend', 'api', 'server', 'service']):
            return 'Backend'
        
        # Database indicators
        if any(keyword in name_lower for keyword in ['db', 'database', 'data', 'storage']):
            return 'Database'
        
        # Scripts/Tools
        if any(keyword in name_lower for keyword in ['script', 'tool', 'util', 'helper']):
            return 'Scripts'
        
        # Guess based on primary language
        if languages:
            primary_lang = languages[0]
            if primary_lang in ['JavaScript', 'TypeScript', 'Vue', 'HTML']:
                return 'Frontend'
            elif primary_lang in ['Python', 'Java', 'Go', 'Ruby', 'PHP']:
                return 'Backend'
        
        return 'Component'

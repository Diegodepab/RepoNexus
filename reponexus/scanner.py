"""
Scanner module: Detects level-1 subdirectories and identifies programming languages.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Set


class RepositoryScanner:
    """
    Scans a repository to identify subsystems (level-1 folders) and detect languages.
    """
    
    # Language detection based on file extensions
    LANGUAGE_EXTENSIONS = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.java': 'Java',
        '.go': 'Go',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.cs': 'C#',
        '.cpp': 'C++',
        '.c': 'C',
        '.rs': 'Rust',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.html': 'HTML',
        '.css': 'CSS',
        '.vue': 'Vue',
        '.dart': 'Dart',
    }
    
    # Common directories to ignore
    IGNORE_DIRS = {
        '.git', '.github', '.vscode', '.idea', 'node_modules', '__pycache__',
        'venv', 'env', '.venv', '.env', 'build', 'dist', 'target',
        '.pytest_cache', '.mypy_cache', 'coverage', '.coverage'
    }
    
    def __init__(self, repo_path: str):
        """
        Initialize the scanner with a repository path.
        
        Args:
            repo_path: Path to the repository to scan
        """
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        if not self.repo_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {repo_path}")
    
    def get_level1_nodes(self) -> Dict[str, Dict[str, Any]]:
        """
        Get level-1 subdirectories (nodes) with their metadata.
        
        Returns:
            Dictionary mapping folder name to metadata (languages, file count, etc.)
        """
        nodes = {}
        
        try:
            for item in self.repo_path.iterdir():
                if item.is_dir() and item.name not in self.IGNORE_DIRS:
                    node_name = item.name
                    node_info = self._analyze_directory(item)
                    nodes[node_name] = node_info
        except PermissionError as e:
            print(f"Warning: Permission denied accessing {self.repo_path}: {e}")
        
        return nodes
    
    def _analyze_directory(self, directory: Path) -> Dict[str, Any]:
        """
        Analyze a directory to detect languages and count files.
        
        Args:
            directory: Path to the directory to analyze
            
        Returns:
            Dictionary with directory metadata
        """
        languages = set()
        file_count = 0
        file_paths = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
                
                for file in files:
                    file_count += 1
                    file_path = Path(root) / file
                    file_paths.append(file_path)
                    
                    # Detect language based on extension
                    ext = file_path.suffix.lower()
                    if ext in self.LANGUAGE_EXTENSIONS:
                        languages.add(self.LANGUAGE_EXTENSIONS[ext])
        
        except PermissionError:
            pass  # Skip directories we can't access
        
        return {
            'path': directory,
            'languages': sorted(list(languages)),
            'file_count': file_count,
            'file_paths': file_paths
        }
    
    def get_all_file_paths(self, node_name: str) -> List[Path]:
        """
        Get all file paths for a specific node.
        
        Args:
            node_name: Name of the level-1 directory
            
        Returns:
            List of file paths
        """
        node_path = self.repo_path / node_name
        if not node_path.exists():
            return []
        
        nodes = self.get_level1_nodes()
        if node_name in nodes:
            return nodes[node_name]['file_paths']
        return []

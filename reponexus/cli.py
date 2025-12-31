"""
CLI module: Command-line interface for RepoNexus.
"""

import argparse
import sys
from pathlib import Path

from .scanner import RepositoryScanner
from .logic import RelationshipAnalyzer
from .renderer import MermaidRenderer


def main():
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        description='RepoNexus - Generate Mermaid.js architecture diagrams from repository analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory
  reponexus .
  
  # Analyze specific repository
  reponexus /path/to/repo
  
  # Generate C4-style diagram
  reponexus . --style c4
  
  # Save output to file
  reponexus . --output diagram.mmd
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to the repository to analyze (default: current directory)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: print to stdout)'
    )
    
    parser.add_argument(
        '-s', '--style',
        choices=['simple', 'c4'],
        default='simple',
        help='Diagram style: simple (default) or c4 (detailed)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='RepoNexus 0.1.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Validate path
        repo_path = Path(args.path).resolve()
        if not repo_path.exists():
            print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"Analyzing repository: {repo_path}")
        
        # Step 1: Scan repository
        scanner = RepositoryScanner(str(repo_path))
        nodes = scanner.get_level1_nodes()
        
        if not nodes:
            print("Warning: No level-1 subdirectories found", file=sys.stderr)
            sys.exit(0)
        
        if args.verbose:
            print(f"Found {len(nodes)} subsystems:")
            for node_name, node_info in nodes.items():
                languages = ', '.join(node_info['languages']) or 'Unknown'
                print(f"  - {node_name}: {languages} ({node_info['file_count']} files)")
        
        # Step 2: Analyze relationships
        if args.verbose:
            print("\nAnalyzing relationships...")
        
        analyzer = RelationshipAnalyzer(nodes)
        relationships = analyzer.analyze()
        
        if args.verbose:
            print(f"Found {len(relationships)} relationships:")
            for source, target, rel_type in relationships:
                print(f"  - {source} --> {target} [{rel_type}]")
        
        # Step 3: Render diagram
        if args.verbose:
            print(f"\nGenerating {args.style} diagram...")
        
        renderer = MermaidRenderer(nodes, relationships)
        
        if args.style == 'c4':
            diagram = renderer.render_c4_diagram()
        else:
            diagram = renderer.render_graph()
        
        # Output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(diagram)
            print(f"Diagram saved to: {output_path}")
        else:
            print(diagram)
        
        if args.verbose:
            print("\nDone!")
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

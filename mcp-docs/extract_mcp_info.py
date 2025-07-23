#!/usr/bin/env python3
"""
MCP Server Information Extractor

This script processes an MCP server-info.json file and extracts useful information
for AI integration, including tools, resources, templates, and capabilities.
"""

import json
import argparse
from typing import Dict, List, Any
from pathlib import Path


class MCPInfoExtractor:
    """Extract and format MCP server information for AI integration."""
    
    def __init__(self, json_file_path: str):
        """Initialize with path to server-info.json file."""
        self.json_file_path = Path(json_file_path)
        self.data = self._load_json()
    
    def _load_json(self) -> Dict[str, Any]:
        """Load and parse the JSON file."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {self.json_file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    
    def extract_server_metadata(self) -> Dict[str, Any]:
        """Extract basic server metadata."""
        return {
            "name": self.data.get("name"),
            "instructions": self.data.get("instructions"),
            "fastmcp_version": self.data.get("fastmcp_version"),
            "mcp_version": self.data.get("mcp_version"),
            "server_version": self.data.get("server_version"),
        }
    
    def extract_tools_summary(self) -> Dict[str, Any]:
        """Extract tools information with categorization."""
        tools = self.data.get("tools", [])
        enabled_tools = [tool for tool in tools if tool.get("enabled", True)]
        
        # Group tools by tags/categories
        categories = {}
        for tool in enabled_tools:
            tags = tool.get("tags", [])
            if not tags:
                tags = ["uncategorized"]
            
            for tag in tags:
                if tag not in categories:
                    categories[tag] = []
                categories[tag].append({
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "key": tool.get("key")
                })
        
        return {
            "total_tools": len(tools),
            "enabled_tools": len(enabled_tools),
            "disabled_tools": len(tools) - len(enabled_tools),
            "categories": categories,
            "tools_by_name": {
                tool.get("name"): {
                    "description": tool.get("description"),
                    "required_params": tool.get("input_schema", {}).get("required", []),
                    "tags": tool.get("tags", []),
                    "enabled": tool.get("enabled", True)
                }
                for tool in tools
            }
        }
    
    def extract_detailed_tools(self) -> List[Dict[str, Any]]:
        """Extract detailed tool information including schemas."""
        tools = self.data.get("tools", [])
        detailed_tools = []
        
        for tool in tools:
            if not tool.get("enabled", True):
                continue
                
            schema = tool.get("input_schema", {})
            properties = schema.get("properties", {})
            
            # Extract parameter information
            parameters = {}
            for param_name, param_info in properties.items():
                param_type = param_info.get("type", "unknown")
                param_title = param_info.get("title", param_name)
                param_default = param_info.get("default")
                
                # Handle anyOf type definitions
                if "anyOf" in param_info:
                    types = [t.get("type") for t in param_info["anyOf"] if "type" in t]
                    param_type = " | ".join(filter(None, types))
                
                parameters[param_name] = {
                    "type": param_type,
                    "title": param_title,
                    "default": param_default,
                    "required": param_name in schema.get("required", [])
                }
            
            detailed_tools.append({
                "name": tool.get("name"),
                "description": tool.get("description"),
                "key": tool.get("key"),
                "tags": tool.get("tags", []),
                "parameters": parameters,
                "required_parameters": schema.get("required", []),
                "annotations": tool.get("annotations", {}),
                "enabled": tool.get("enabled", True)
            })
        
        return detailed_tools
    
    def extract_resources(self) -> Dict[str, Any]:
        """Extract resources information."""
        resources = self.data.get("resources", [])
        enabled_resources = [res for res in resources if res.get("enabled", True)]
        
        return {
            "total_resources": len(resources),
            "enabled_resources": len(enabled_resources),
            "resources": [
                {
                    "name": res.get("name"),
                    "description": res.get("description"),
                    "uri": res.get("uri"),
                    "mime_type": res.get("mime_type"),
                    "tags": res.get("tags"),
                    "enabled": res.get("enabled", True)
                }
                for res in resources
            ]
        }
    
    def extract_templates(self) -> Dict[str, Any]:
        """Extract template information."""
        templates = self.data.get("templates", [])
        enabled_templates = [tmpl for tmpl in templates if tmpl.get("enabled", True)]
        
        return {
            "total_templates": len(templates),
            "enabled_templates": len(enabled_templates),
            "templates": [
                {
                    "name": tmpl.get("name"),
                    "description": tmpl.get("description"),
                    "uri_template": tmpl.get("uri_template"),
                    "key": tmpl.get("key"),
                    "mime_type": tmpl.get("mime_type"),
                    "enabled": tmpl.get("enabled", True)
                }
                for tmpl in templates
            ]
        }
    
    def extract_capabilities(self) -> Dict[str, Any]:
        """Extract server capabilities."""
        return self.data.get("capabilities", {})
    
    def generate_ai_integration_guide(self) -> str:
        """Generate a comprehensive integration guide for AIs."""
        metadata = self.extract_server_metadata()
        tools_summary = self.extract_tools_summary()
        resources = self.extract_resources()
        templates = self.extract_templates()
        capabilities = self.extract_capabilities()
        
        guide = f"""# MCP Server Integration Guide: {metadata['name']}

## Server Information
- **Name**: {metadata['name']}
- **MCP Version**: {metadata['mcp_version']}
- **Server Version**: {metadata['server_version']}
- **FastMCP Version**: {metadata['fastmcp_version']}

## Available Tools ({tools_summary['enabled_tools']} enabled)

### Tool Categories:
"""
        
        for category, tools in tools_summary['categories'].items():
            guide += f"\n#### {category.title()}\n"
            for tool in tools:
                guide += f"- **{tool['name']}**: {tool['description']}\n"
        
        guide += f"""
### Most Common Tool Operations:
- **Todo Management**: Create areas, projects, and tasks with priority/scheduling
- **Knowledge Graph**: Manage entities and relationships 
- **Automation**: Workflow control and suggestions
- **Search**: Intelligent semantic search across data types
- **Analytics**: Get insights and project intelligence

## Resources ({resources['enabled_resources']} available)
"""
        
        for resource in resources['resources'][:10]:  # Show first 10
            if resource['enabled']:
                guide += f"- **{resource['name']}**: {resource['description']}\n"
        
        if len(resources['resources']) > 10:
            guide += f"... and {len(resources['resources']) - 10} more resources\n"
        
        guide += f"""
## Templates ({templates['enabled_templates']} available)
"""
        
        for template in templates['templates']:
            if template['enabled']:
                guide += f"- **{template['name']}**: {template['description']}\n"
                guide += f"  URI: `{template['uri_template']}`\n"
        
        guide += f"""
## Server Capabilities
- **Tools**: {"✓" if capabilities.get('tools', {}).get('listChanged') else "✗"} List changes supported
- **Resources**: {"✓" if capabilities.get('resources', {}).get('subscribe') else "✗"} Subscription, {"✓" if capabilities.get('resources', {}).get('listChanged') else "✗"} List changes
- **Prompts**: {"✓" if capabilities.get('prompts', {}).get('listChanged') else "✗"} List changes supported
- **Logging**: {"✓" if capabilities.get('logging') else "✗"} Available

## Integration Tips for AIs
1. **Start with todo_get** to understand current task state
2. **Use intelligent_search** for finding relevant information across all data types
3. **Create tasks with todo_create_task_nl** using natural language
4. **Get project insights** with get_project_intelligence
5. **Use graph operations** for understanding entity relationships
6. **Leverage automation** for workflow suggestions and control

## Key Namespaces
- `todo_*`: Task and project management
- `graph_*`: Knowledge graph operations  
- `automation_*`: Workflow automation
- `handoff_*`: Context management
- `intelligent_search`: Cross-domain search
- `get_*`: Data retrieval and insights
"""
        
        return guide
    
    def save_extracted_info(self, output_dir: str = None) -> Dict[str, str]:
        """Save extracted information to files."""
        if output_dir is None:
            output_dir = self.json_file_path.parent
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        files_created = {}
        
        # Save comprehensive AI integration guide
        guide_content = self.generate_ai_integration_guide()
        guide_file = output_path / "mcp_ai_integration_guide.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        files_created['integration_guide'] = str(guide_file)
        
        # Save detailed tools JSON
        detailed_tools = self.extract_detailed_tools()
        tools_file = output_path / "mcp_tools_detailed.json"
        with open(tools_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_tools, f, indent=2, ensure_ascii=False)
        files_created['detailed_tools'] = str(tools_file)
        
        # Save summary JSON
        summary = {
            "metadata": self.extract_server_metadata(),
            "tools_summary": self.extract_tools_summary(),
            "resources": self.extract_resources(),
            "templates": self.extract_templates(),
            "capabilities": self.extract_capabilities()
        }
        summary_file = output_path / "mcp_server_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        files_created['summary'] = str(summary_file)
        
        return files_created


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Extract MCP server information for AI integration")
    parser.add_argument("json_file", help="Path to server-info.json file")
    parser.add_argument("-o", "--output", help="Output directory (default: same as input file)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output messages")
    
    args = parser.parse_args()
    
    try:
        extractor = MCPInfoExtractor(args.json_file)
        files_created = extractor.save_extracted_info(args.output)
        
        if not args.quiet:
            print(f"✅ Successfully processed MCP server info from: {args.json_file}")
            print("\n📁 Files created:")
            for file_type, file_path in files_created.items():
                print(f"  - {file_type}: {file_path}")
            print(f"\n🤖 AI Integration Guide: {files_created['integration_guide']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

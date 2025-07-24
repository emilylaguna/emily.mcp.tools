#!/usr/bin/env python3
"""
MCP Individual Tool Extractor

This script processes an MCP server-info.json file and creates individual
documentation files for each tool, making it easier for AIs to load
specific tool information on-demand.
"""

import json
import argparse
from typing import Dict, List, Any
from pathlib import Path
import re


class MCPToolFileGenerator:
    """Generate individual tool files from MCP server information."""
    
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
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize tool name for filename."""
        # Replace any non-alphanumeric characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        return sanitized.strip('_')
    
    def _format_parameter_type(self, param_info: Dict[str, Any]) -> str:
        """Format parameter type information."""
        if "anyOf" in param_info:
            types = []
            for type_option in param_info["anyOf"]:
                if "type" in type_option:
                    types.append(type_option["type"])
            return " | ".join(types) if types else "unknown"
        
        if "$ref" in param_info:
            # Handle reference types (like enums)
            return param_info.get("title", "enum")
        
        param_type = param_info.get("type", "unknown")
        return param_type if param_type is not None else "unknown"
    
    def _extract_enum_values(self, schema: Dict[str, Any], ref_path: str) -> List[str]:
        """Extract enum values from schema definitions."""
        if not ref_path or not ref_path.startswith("#/$defs/"):
            return []
        
        def_name = ref_path.replace("#/$defs/", "")
        defs = schema.get("$defs", {})
        
        if def_name in defs:
            enum_values = defs[def_name].get("enum", [])
            return enum_values if enum_values is not None else []
        
        return []
    
    def generate_tool_file_content(self, tool: Dict[str, Any]) -> str:
        """Generate markdown content for a single tool."""
        name = tool.get("name", "unknown")
        description = tool.get("description", "No description available")
        tags = tool.get("tags", [])
        enabled = tool.get("enabled", True)
        annotations = tool.get("annotations", {})
        
        schema = tool.get("input_schema", {})
        properties = schema.get("properties", {})
        required_params = schema.get("required", [])
        
        # Ensure we have valid values
        if tags is None:
            tags = []
        if annotations is None:
            annotations = {}
        if properties is None:
            properties = {}
        if required_params is None:
            required_params = []
        
        content = f"""# {name}

## Description
{description}

## Status
- **Enabled**: {'✅ Yes' if enabled else '❌ No'}
- **Tags**: {', '.join(tags) if tags else 'None'}

## Parameters

"""
        
        if not properties:
            content += "This tool takes no parameters.\n\n"
        else:
            # Group parameters by required/optional
            required_props = {k: v for k, v in properties.items() if k in required_params}
            optional_props = {k: v for k, v in properties.items() if k not in required_params}
            
            if required_props:
                content += "### Required Parameters\n\n"
                for param_name, param_info in required_props.items():
                    param_type = self._format_parameter_type(param_info)
                    param_title = param_info.get("title", param_name)
                    param_desc = param_info.get("description", "No description")
                    
                    content += f"#### `{param_name}` ({param_type})\n"
                    content += f"- **Title**: {param_title}\n"
                    content += f"- **Description**: {param_desc}\n"
                    
                    # Handle enum values
                    if "$ref" in param_info:
                        enum_values = self._extract_enum_values(schema, param_info["$ref"])
                        if enum_values:
                            content += f"- **Allowed values**: {', '.join(f'`{v}`' for v in enum_values)}\n"
                    
                    content += "\n"
            
            if optional_props:
                content += "### Optional Parameters\n\n"
                for param_name, param_info in optional_props.items():
                    param_type = self._format_parameter_type(param_info)
                    param_title = param_info.get("title", param_name)
                    param_desc = param_info.get("description", "No description")
                    param_default = param_info.get("default")
                    
                    content += f"#### `{param_name}` ({param_type})\n"
                    content += f"- **Title**: {param_title}\n"
                    content += f"- **Description**: {param_desc}\n"
                    if param_default is not None:
                        content += f"- **Default**: `{param_default}`\n"
                    
                    # Handle enum values
                    if "$ref" in param_info:
                        enum_values = self._extract_enum_values(schema, param_info["$ref"])
                        if enum_values:
                            content += f"- **Allowed values**: {', '.join(f'`{v}`' for v in enum_values)}\n"
                    
                    content += "\n"
        
        # Add annotations if present
        if annotations and any(v is not None for v in annotations.values()):
            content += "## Tool Annotations\n\n"
            if annotations.get("destructiveHint"):
                content += "- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone\n"
            if annotations.get("idempotentHint"):
                content += "- 🔄 **Idempotent**: Multiple calls with same parameters produce same result\n"
            if annotations.get("readOnlyHint"):
                content += "- 👁️ **Read-only**: This tool only retrieves information\n"
            content += "\n"
        
        # Add usage example section
        content += "## Usage Example\n\n"
        content += f"```json\n{{\n  \"tool\": \"{name}\""
        
        # Initialize required_props here for the usage example
        required_props = {k: v for k, v in properties.items() if k in required_params} if properties else {}
        
        if required_props:
            content += ",\n  \"parameters\": {\n"
            example_params = []
            for param_name, param_info in required_props.items():
                param_type = self._format_parameter_type(param_info)
                if "string" in param_type:
                    example_params.append(f'    "{param_name}": "example_value"')
                elif "integer" in param_type or "number" in param_type:
                    example_params.append(f'    "{param_name}": 1')
                elif "boolean" in param_type:
                    example_params.append(f'    "{param_name}": true')
                else:
                    example_params.append(f'    "{param_name}": "value"')
            
            content += ",\n".join(example_params)
            content += "\n  }"
        
        content += "\n}\n```\n\n"
        
        # Add related tools section based on tags
        related_tools = self._find_related_tools(tool)
        if related_tools:
            content += "## Related Tools\n\n"
            for related_tool in related_tools[:5]:  # Limit to 5 related tools
                content += f"- `{related_tool['name']}`: {related_tool['description'][:100]}{'...' if len(related_tool['description']) > 100 else ''}\n"
            content += "\n"
        
        return content
    
    def _find_related_tools(self, current_tool: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find tools with similar tags or name patterns."""
        current_tags = set(current_tool.get("tags") or [])
        current_name = current_tool.get("name") or ""
        current_prefix = current_name.split("_")[0] if "_" in current_name else ""
        
        related = []
        tools = self.data.get("tools") or []
        
        for tool in tools:
            if tool.get("name") == current_name:
                continue  # Skip self
            
            tool_tags = set(tool.get("tags") or [])
            tool_name = tool.get("name") or ""
            tool_prefix = tool_name.split("_")[0] if "_" in tool_name else ""
            
            # Score based on tag overlap and name prefix
            tag_overlap = len(current_tags.intersection(tool_tags))
            prefix_match = 1 if current_prefix and current_prefix == tool_prefix else 0
            
            score = tag_overlap + prefix_match
            if score > 0:
                related.append({
                    "name": tool_name,
                    "description": tool.get("description") or "",
                    "score": score
                })
        
        # Sort by score and return
        return sorted(related, key=lambda x: x["score"], reverse=True)
    
    def generate_tool_index(self, tools: List[Dict[str, Any]]) -> str:
        """Generate an index file listing all tools."""
        # Group tools by category (first tag)
        categories = {}
        for tool in tools:
            if not tool.get("enabled", True):
                continue
                
            tags = tool.get("tags") or ["uncategorized"]
            category = tags[0] if tags else "uncategorized"
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                "name": tool.get("name") or "unknown",
                "description": tool.get("description") or "",
                "filename": f"{self._sanitize_filename(tool.get('name') or 'unknown')}.md"
            })
        
        enabled_count = len([t for t in tools if t.get('enabled', True)])
        
        content = f"""# MCP Tools Index

This directory contains individual documentation files for each MCP tool.

**Total Tools**: {enabled_count}

## Categories

"""
        
        for category, category_tools in sorted(categories.items()):
            content += f"### {category.title()}\n\n"
            for tool in sorted(category_tools, key=lambda x: x["name"]):
                desc = tool['description'][:100] + ('...' if len(tool['description']) > 100 else '')
                content += f"- [`{tool['name']}`](./{tool['filename']}) - {desc}\n"
            content += "\n"
        
        content += """## Quick Reference

### Common Patterns

- **todo_*** - Task and project management
- **graph_*** - Knowledge graph operations
- **automation_*** - Workflow automation
- **get_*** - Data retrieval and insights
- **intelligent_search** - Cross-domain semantic search
- **natural_query** - Natural language processing

### Usage Tips

1. Start with the index to find relevant tools
2. Check required vs optional parameters
3. Note tool annotations (destructive, read-only, etc.)
4. Use related tools section for workflow discovery
"""
        
        return content
    
    def generate_all_tool_files(self, output_dir: str = None) -> Dict[str, Any]:
        """Generate individual files for each tool."""
        if output_dir is None:
            output_dir = self.json_file_path.parent
        
        # Create tools subdirectory
        tools_dir = Path(output_dir) / "mcp-docs/mcp_tools"
        tools_dir.mkdir(exist_ok=True)
        
        tools = self.data.get("tools", [])
        enabled_tools = [tool for tool in tools if tool.get("enabled", True)]
        
        files_created = []
        
        # Generate individual tool files
        for tool in enabled_tools:
            tool_name = tool.get("name", "unknown")
            filename = f"{self._sanitize_filename(tool_name)}.md"
            file_path = tools_dir / filename
            
            content = self.generate_tool_file_content(tool)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            files_created.append({
                "tool_name": tool_name,
                "filename": filename,
                "file_path": str(file_path)
            })
        
        # Generate index file
        index_content = self.generate_tool_index(enabled_tools)
        index_path = tools_dir / "README.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        return {
            "tools_directory": str(tools_dir),
            "index_file": str(index_path),
            "total_tools": len(enabled_tools),
            "files_created": files_created
        }


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Generate individual MCP tool documentation files")
    parser.add_argument("json_file", help="Path to server-info.json file")
    parser.add_argument("-o", "--output", help="Output directory (default: same as input file)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output messages")
    
    args = parser.parse_args()
    
    try:
        generator = MCPToolFileGenerator(args.json_file)
        result = generator.generate_all_tool_files(args.output)
        
        if not args.quiet:
            print(f"✅ Successfully generated individual tool files from: {args.json_file}")
            print(f"\n📁 Tools directory: {result['tools_directory']}")
            print(f"📋 Index file: {result['index_file']}")
            print(f"🔧 Total tools documented: {result['total_tools']}")
            print(f"\n💡 Each tool now has its own .md file for easy loading!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

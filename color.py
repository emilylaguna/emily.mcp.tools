import coloredlogs, logging
import asyncio
from mcp.server.fastmcp import Context, FastMCP
import main
import json

logger = logging.getLogger(__name__)
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR) 
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('huggingface_hub').setLevel(logging.ERROR)
logging.getLogger('filelock').setLevel(logging.ERROR)

logger.debug("Starting up MCP server...")


json_data = {
  "id": "meow-detector",
  "name": "Meow Detection Workflow",
  "description": "Creates a fun todo when Emily says 'meow' in conversation",
  "trigger": {
    "type": "handoff",
    "content": "meow"
  },
  "schedule": None,
  "actions": [
    {
      "type": "create_task",
      "params": {
        "title": "🐱 Meow Alert!",
        "description": "Emily said meow! Time for some cat-related fun. Maybe watch cat videos or share cat memes?",
        "priority": "low",
        "tags": [
          "meow",
          "cats",
          "fun",
          "emily"
        ]
      },
      "condition": None
    }
  ]
}

mcp = main.create_mcp_server()

async def color():
    # handoff = await mcp.call_tool("automation_register_workflow", {
    #     "workflow_definition": json_data
    # })
    # Print a JSON pretty print
    handoff = await mcp.call_tool("handoff_save", {"context": "Hello, world! and Meow"})
    logger.info(f"Handoff: {handoff}")
    
    today = await mcp.call_tool("todo_get_today", {})
    logger.info(f"Today: {today}")

asyncio.run(color())
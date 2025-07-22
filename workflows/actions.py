"""
Workflow Actions Implementation

Provides implementations for all built-in workflow action types.
Each action type has its own handler with proper error handling and logging.
"""

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional
from datetime import datetime

import aiohttp
from pydantic import BaseModel

try:
    from ..core import UnifiedMemoryStore
    from ..core.models import MemoryEntity, MemoryRelation
except ImportError:
    from core import UnifiedMemoryStore
    from core.models import MemoryEntity, MemoryRelation

logger = logging.getLogger(__name__)


class ActionResult(BaseModel):
    """Result of an action execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WorkflowActionExecutor:
    """Executes workflow actions with proper error handling."""
    
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory = memory_store
        self.notification_channels = {}  # Configured notification channels
    
    async def execute_action(self, action_type: str, params: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        """Execute a workflow action."""
        try:
            if action_type == 'create_task':
                return await self._create_task(params, context)
            elif action_type == 'update_entity':
                return await self._update_entity(params, context)
            elif action_type == 'save_relation':
                return await self._save_relation(params, context)
            elif action_type == 'notify':
                return await self._notify(params, context)
            elif action_type == 'run_shell':
                return await self._run_shell(params, context)
            elif action_type == 'http_request':
                return await self._http_request(params, context)
            else:
                return ActionResult(
                    success=False,
                    message=f"Unknown action type: {action_type}",
                    error=f"Unsupported action type: {action_type}"
                )
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return ActionResult(
                success=False,
                message="Action execution failed",
                error=str(e)
            )
    
    async def _create_task(self, params: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        """Create a new task entity."""
        try:
            # Extract task parameters
            title = params.get('title', 'Untitled Task')
            content = params.get('content', '')
            priority = params.get('priority', 'medium')
            due_date = params.get('due_date')
            project_id = params.get('project_id')
            
            # Create task entity
            task = MemoryEntity(
                type="task",
                name=title,
                content=content,
                metadata={
                    'priority': priority,
                    'status': 'pending',
                    'created_by_workflow': True,
                    'workflow_context': context.get('workflow_id')
                }
            )
            
            # Add due date if specified
            if due_date:
                task.metadata['due_date'] = due_date
            
            # Add project reference if specified
            if project_id:
                task.metadata['project_id'] = project_id
            
            # Save task
            saved_task = self.memory.save_entity(task)
            
            # Create relation to project if specified
            if project_id:
                try:
                    relation = MemoryRelation(
                        source_id=project_id,
                        target_id=saved_task.id,
                        relation_type="contains"
                    )
                    self.memory.save_relation(relation)
                except Exception as e:
                    logger.warning(f"Failed to create project relation: {e}")
            
            return ActionResult(
                success=True,
                message=f"Created task: {title}",
                data={'task_id': saved_task.id, 'task_name': title}
            )
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return ActionResult(
                success=False,
                message="Failed to create task",
                error=str(e)
            )
    
    async def _update_entity(self, params: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        """Update an existing entity."""
        try:
            entity_id = params.get('entity_id')
            if not entity_id:
                return ActionResult(
                    success=False,
                    message="Missing entity_id parameter",
                    error="entity_id is required for update_entity action"
                )
            
            # Get existing entity
            entity = self.memory.get_entity(entity_id)
            if not entity:
                return ActionResult(
                    success=False,
                    message=f"Entity not found: {entity_id}",
                    error=f"Entity {entity_id} does not exist"
                )
            
            # Update fields
            updates = params.get('updates', {})
            metadata_updates = params.get('metadata', {})
            
            # Update basic fields
            if 'name' in updates:
                entity.name = updates['name']
            if 'content' in updates:
                entity.content = updates['content']
            if 'type' in updates:
                entity.type = updates['type']
            
            # Update metadata
            if metadata_updates:
                entity.metadata.update(metadata_updates)
            
            # Save updated entity
            updated_entity = self.memory.update_entity(entity)
            
            return ActionResult(
                success=True,
                message=f"Updated entity: {entity_id}",
                data={'entity_id': entity_id, 'updated_fields': list(updates.keys())}
            )
            
        except Exception as e:
            logger.error(f"Failed to update entity: {e}")
            return ActionResult(
                success=False,
                message="Failed to update entity",
                error=str(e)
            )
    
    async def _save_relation(self, params: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        """Create a new relation between entities."""
        try:
            source_id = params.get('source_id')
            target_id = params.get('target_id')
            relation_type = params.get('relation_type')
            
            if not all([source_id, target_id, relation_type]):
                return ActionResult(
                    success=False,
                    message="Missing required parameters",
                    error="source_id, target_id, and relation_type are required"
                )
            
            # Create relation
            relation = MemoryRelation(
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                metadata=params.get('metadata', {})
            )
            
            saved_relation = self.memory.save_relation(relation)
            
            return ActionResult(
                success=True,
                message=f"Created relation: {source_id} -> {target_id} ({relation_type})",
                data={'relation_id': saved_relation.id}
            )
            
        except Exception as e:
            logger.error(f"Failed to save relation: {e}")
            return ActionResult(
                success=False,
                message="Failed to save relation",
                error=str(e)
            )
    
    async def _notify(self, params: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        """Send a notification via configured channels."""
        try:
            message = params.get('message', '')
            channel = params.get('channel', 'console')
            
            if not message:
                return ActionResult(
                    success=False,
                    message="Missing message parameter",
                    error="message is required for notify action"
                )
            
            # Send notification based on channel
            if channel == 'console':
                logger.info(f"NOTIFICATION: {message}")
                return ActionResult(
                    success=True,
                    message="Notification logged to console",
                    data={'channel': 'console', 'message': message}
                )
            
            elif channel == 'slack':
                return await self._send_slack_notification(message, params)
            
            elif channel == 'email':
                return await self._send_email_notification(message, params)
            
            else:
                return ActionResult(
                    success=False,
                    message=f"Unsupported notification channel: {channel}",
                    error=f"Channel {channel} is not configured"
                )
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return ActionResult(
                success=False,
                message="Failed to send notification",
                error=str(e)
            )
    
    async def _send_slack_notification(self, message: str, params: Dict[str, Any]) -> ActionResult:
        """Send notification to Slack."""
        webhook_url = self.notification_channels.get('slack_webhook')
        if not webhook_url:
            return ActionResult(
                success=False,
                message="Slack webhook not configured",
                error="slack_webhook not found in notification channels"
            )
        
        try:
            payload = {
                'text': message,
                'username': 'Workflow Bot',
                'icon_emoji': ':robot_face:'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        return ActionResult(
                            success=True,
                            message="Slack notification sent",
                            data={'channel': 'slack', 'message': message}
                        )
                    else:
                        return ActionResult(
                            success=False,
                            message=f"Slack API error: {response.status}",
                            error=f"HTTP {response.status}"
                        )
        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to send Slack notification",
                error=str(e)
            )
    
    async def _send_email_notification(self, message: str, params: Dict[str, Any]) -> ActionResult:
        """Send notification via email."""
        # This would integrate with an email service
        # For now, just log the email
        recipient = params.get('to', 'admin@example.com')
        subject = params.get('subject', 'Workflow Notification')
        
        logger.info(f"EMAIL NOTIFICATION - To: {recipient}, Subject: {subject}, Message: {message}")
        
        return ActionResult(
            success=True,
            message="Email notification logged",
            data={'channel': 'email', 'to': recipient, 'subject': subject, 'message': message}
        )
    
    async def _run_shell(self, params: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        """Execute a shell command."""
        try:
            command = params.get('command')
            if not command:
                return ActionResult(
                    success=False,
                    message="Missing command parameter",
                    error="command is required for run_shell action"
                )
            
            # Execute command in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._execute_shell_command, 
                command
            )
            
            return ActionResult(
                success=result['success'],
                message=result['message'],
                data={'command': command, 'output': result.get('output', '')},
                error=result.get('error')
            )
            
        except Exception as e:
            logger.error(f"Failed to run shell command: {e}")
            return ActionResult(
                success=False,
                message="Failed to run shell command",
                error=str(e)
            )
    
    def _execute_shell_command(self, command: str) -> Dict[str, Any]:
        """Execute shell command synchronously."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Command executed successfully',
                    'output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'message': f'Command failed with return code {result.returncode}',
                    'error': result.stderr,
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'Command timed out',
                'error': 'Command execution exceeded 30 second timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'message': 'Command execution failed',
                'error': str(e)
            }
    
    async def _http_request(self, params: Dict[str, Any], context: Dict[str, Any]) -> ActionResult:
        """Make an HTTP request."""
        try:
            url = params.get('url')
            method = params.get('method', 'GET')
            headers = params.get('headers', {})
            data = params.get('data')
            
            if not url:
                return ActionResult(
                    success=False,
                    message="Missing url parameter",
                    error="url is required for http_request action"
                )
            
            async with aiohttp.ClientSession() as session:
                if method.upper() == 'GET':
                    async with session.get(url, headers=headers) as response:
                        response_text = await response.text()
                        return ActionResult(
                            success=response.status < 400,
                            message=f"HTTP {method} completed with status {response.status}",
                            data={
                                'url': url,
                                'method': method,
                                'status': response.status,
                                'response': response_text
                            },
                            error=None if response.status < 400 else f"HTTP {response.status}"
                        )
                elif method.upper() == 'POST':
                    async with session.post(url, headers=headers, json=data) as response:
                        response_text = await response.text()
                        return ActionResult(
                            success=response.status < 400,
                            message=f"HTTP {method} completed with status {response.status}",
                            data={
                                'url': url,
                                'method': method,
                                'status': response.status,
                                'response': response_text
                            },
                            error=None if response.status < 400 else f"HTTP {response.status}"
                        )
                else:
                    return ActionResult(
                        success=False,
                        message=f"Unsupported HTTP method: {method}",
                        error=f"Method {method} is not supported"
                    )
                    
        except Exception as e:
            logger.error(f"Failed to make HTTP request: {e}")
            return ActionResult(
                success=False,
                message="Failed to make HTTP request",
                error=str(e)
            )
    
    def configure_notification_channel(self, channel: str, config: Dict[str, Any]) -> None:
        """Configure a notification channel."""
        self.notification_channels[channel] = config
        logger.info(f"Configured notification channel: {channel}")
    
    def get_supported_actions(self) -> List[str]:
        """Get list of supported action types."""
        return [
            'create_task',
            'update_entity', 
            'save_relation',
            'notify',
            'run_shell',
            'http_request'
        ] 
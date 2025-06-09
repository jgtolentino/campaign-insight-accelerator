from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket
from ..memory_sync.memory_service import MemoryService
from ..mcp.mcp_service import MCPService

class AgentBridge:
    def __init__(self):
        self.app = FastAPI()
        self.memory_service = MemoryService()
        self.mcp_service = MCPService()
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, agent_id: str):
        """Connect an agent to the bridge."""
        await websocket.accept()
        self.active_connections[agent_id] = websocket

    async def disconnect(self, agent_id: str):
        """Disconnect an agent from the bridge."""
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]

    async def broadcast(self, message: Dict):
        """Broadcast a message to all connected agents."""
        for connection in self.active_connections.values():
            await connection.send_json(message)

    async def send_to_agent(self, agent_id: str, message: Dict):
        """Send a message to a specific agent."""
        if agent_id in self.active_connections:
            await self.active_connections[agent_id].send_json(message)
            # Store in memory for persistence
            self.memory_service.send_message(
                sender_id=message.get('sender_id', 'system'),
                receiver_id=agent_id,
                message_type=message.get('type', 'message'),
                content=message
            )

    async def handle_message(self, agent_id: str, message: Dict):
        """Handle incoming messages from agents."""
        # Store in memory
        self.memory_service.store_memory(
            agent_id=agent_id,
            memory_type='message',
            content=message
        )

        # Process based on message type
        if message.get('type') == 'sync_request':
            # Handle sync request
            memories = self.memory_service.get_memories(agent_id)
            await self.send_to_agent(agent_id, {
                'type': 'sync_response',
                'memories': memories
            })
        elif message.get('type') == 'cloud_sync':
            # Handle cloud sync request
            self.mcp_service.sync_across_clouds(
                source=message.get('source'),
                destination=message.get('destination'),
                data=message.get('data', {})
            )

    def setup_routes(self):
        """Set up FastAPI routes for the bridge."""
        @self.app.websocket("/ws/{agent_id}")
        async def websocket_endpoint(websocket: WebSocket, agent_id: str):
            await self.connect(websocket, agent_id)
            try:
                while True:
                    message = await websocket.receive_json()
                    await self.handle_message(agent_id, message)
            except Exception as e:
                print(f"Error handling message: {e}")
            finally:
                await self.disconnect(agent_id)

        @self.app.get("/agents/{agent_id}/memories")
        async def get_agent_memories(agent_id: str):
            return self.memory_service.get_memories(agent_id)

        @self.app.post("/agents/{agent_id}/message")
        async def send_agent_message(agent_id: str, message: Dict):
            await self.send_to_agent(agent_id, message)
            return {"status": "sent"} 
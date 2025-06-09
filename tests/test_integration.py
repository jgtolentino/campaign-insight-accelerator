import pytest
import asyncio
from fastapi.testclient import TestClient
from shared.memory_sync.memory_service import MemoryService
from shared.mcp.mcp_service import MCPService
from shared.agent_bridge.bridge_service import AgentBridge
import os

@pytest.fixture
def memory_service():
    return MemoryService()

@pytest.fixture
def mcp_service():
    return MCPService()

@pytest.fixture
def agent_bridge():
    bridge = AgentBridge()
    bridge.setup_routes()
    return bridge

@pytest.fixture
def client(agent_bridge):
    return TestClient(agent_bridge.app)

def test_memory_service(memory_service):
    # Test storing memory
    memory_id = memory_service.store_memory(
        agent_id="test_agent",
        memory_type="test",
        content={"key": "value"}
    )
    assert memory_id is not None

    # Test retrieving memory
    memories = memory_service.get_memories("test_agent")
    assert len(memories) > 0
    assert memories[0]["content"]["key"] == "value"

def test_mcp_service(mcp_service):
    # Test Google Drive integration
    files = mcp_service.list_drive_files(os.getenv("DRIVE_CAMPAIGN_ROOT_ID"))
    assert isinstance(files, list)

    # Test Pinecone integration
    test_vector = [0.1] * 1536  # OpenAI embedding size
    mcp_service.store_vector("test-index", [(1, test_vector)])
    results = mcp_service.query_vector("test-index", test_vector)
    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_agent_bridge(agent_bridge, client):
    # Test WebSocket connection
    with client.websocket_connect("/ws/test_agent") as websocket:
        # Send a message
        websocket.send_json({
            "type": "test_message",
            "content": "Hello, World!"
        })
        
        # Receive response
        response = websocket.receive_json()
        assert response["type"] == "test_message"
        assert response["content"] == "Hello, World!"

    # Test memory retrieval
    response = client.get("/agents/test_agent/memories")
    assert response.status_code == 200
    memories = response.json()
    assert isinstance(memories, list)

def test_full_integration(memory_service, mcp_service, agent_bridge, client):
    # 1. Store memory
    memory_id = memory_service.store_memory(
        agent_id="test_agent",
        memory_type="test",
        content={"key": "value"}
    )

    # 2. Sync to cloud
    mcp_service.sync_across_clouds(
        source="memory",
        destination="pinecone",
        data={"memory_id": memory_id}
    )

    # 3. Send message through bridge
    response = client.post(
        "/agents/test_agent/message",
        json={
            "type": "test_message",
            "content": "Integration test"
        }
    )
    assert response.status_code == 200

    # 4. Verify memory was stored
    memories = memory_service.get_memories("test_agent")
    assert any(m["content"].get("content") == "Integration test" for m in memories) 
from typing import Dict, List, Optional
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

class MemoryService:
    def __init__(self):
        self.engine = create_engine(os.getenv('DATABASE_URL'))
        self.Session = sessionmaker(bind=self.engine)

    def store_memory(self, agent_id: str, memory_type: str, content: Dict) -> int:
        """Store a memory for an agent."""
        with self.Session() as session:
            result = session.execute(
                text("""
                INSERT INTO agent_memory (agent_id, memory_type, content)
                VALUES (:agent_id, :memory_type, :content)
                RETURNING id
                """),
                {
                    "agent_id": agent_id,
                    "memory_type": memory_type,
                    "content": json.dumps(content)
                }
            )
            memory_id = result.scalar()
            session.commit()
            return memory_id

    def get_memories(self, agent_id: str, memory_type: Optional[str] = None) -> List[Dict]:
        """Retrieve memories for an agent."""
        with self.Session() as session:
            query = """
            SELECT id, memory_type, content, created_at, updated_at
            FROM agent_memory
            WHERE agent_id = :agent_id
            """
            params = {"agent_id": agent_id}
            
            if memory_type:
                query += " AND memory_type = :memory_type"
                params["memory_type"] = memory_type
            
            result = session.execute(text(query), params)
            return [dict(row) for row in result]

    def send_message(self, sender_id: str, receiver_id: str, message_type: str, content: Dict) -> int:
        """Send a message between agents."""
        with self.Session() as session:
            result = session.execute(
                text("""
                INSERT INTO agent_communication (sender_id, receiver_id, message_type, content)
                VALUES (:sender_id, :receiver_id, :message_type, :content)
                RETURNING id
                """),
                {
                    "sender_id": sender_id,
                    "receiver_id": receiver_id,
                    "message_type": message_type,
                    "content": json.dumps(content)
                }
            )
            message_id = result.scalar()
            session.commit()
            return message_id

    def get_messages(self, agent_id: str, as_sender: bool = True) -> List[Dict]:
        """Retrieve messages for an agent."""
        with self.Session() as session:
            column = "sender_id" if as_sender else "receiver_id"
            result = session.execute(
                text(f"""
                SELECT id, sender_id, receiver_id, message_type, content, created_at
                FROM agent_communication
                WHERE {column} = :agent_id
                ORDER BY created_at DESC
                """),
                {"agent_id": agent_id}
            )
            return [dict(row) for row in result] 
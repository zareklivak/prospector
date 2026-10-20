"""
WebSocket handler for real-time pipeline updates
"""
import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        # Dictionary of job_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """Accept new WebSocket connection for a job"""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
        print(f"[WebSocket] Client connected to job {job_id}")

    def disconnect(self, websocket: WebSocket, job_id: str):
        """Remove WebSocket connection"""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        print(f"[WebSocket] Client disconnected from job {job_id}")

    async def send_log(self, job_id: str, message: str, level: str = "info"):
        """
        Send log message to all connected clients for a job

        Args:
            job_id: Job identifier
            message: Log message
            level: Log level (info, success, warning, error)
        """
        if job_id not in self.active_connections:
            return

        data = {
            "type": "log",
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }

        await self._broadcast(job_id, data)

    async def send_metrics(self, job_id: str, metrics: Dict):
        """
        Send metrics update to all connected clients

        Args:
            job_id: Job identifier
            metrics: Metrics dictionary
        """
        if job_id not in self.active_connections:
            return

        data = {
            "type": "metrics",
            "data": metrics
        }

        await self._broadcast(job_id, data)

    async def send_complete(self, job_id: str, csv_path: str):
        """
        Send completion message to all connected clients

        Args:
            job_id: Job identifier
            csv_path: Path to generated CSV file
        """
        if job_id not in self.active_connections:
            return

        data = {
            "type": "complete",
            "csv_path": csv_path,
            "timestamp": datetime.now().isoformat()
        }

        await self._broadcast(job_id, data)

    async def send_error(self, job_id: str, error_message: str):
        """
        Send error message to all connected clients

        Args:
            job_id: Job identifier
            error_message: Error description
        """
        if job_id not in self.active_connections:
            return

        data = {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }

        await self._broadcast(job_id, data)

    async def _broadcast(self, job_id: str, data: Dict):
        """
        Broadcast message to all connections for a job

        Args:
            job_id: Job identifier
            data: Data to send
        """
        if job_id not in self.active_connections:
            return

        # Create a copy of connections to avoid modification during iteration
        connections = list(self.active_connections[job_id])

        for connection in connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                print(f"[WebSocket] Error sending to client: {e}")
                self.disconnect(connection, job_id)

    def has_connections(self, job_id: str) -> bool:
        """Check if job has any active connections"""
        return job_id in self.active_connections and len(self.active_connections[job_id]) > 0


# Global connection manager instance
manager = ConnectionManager()

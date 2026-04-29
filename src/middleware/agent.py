"""
Agent-ready middleware for Compilore API.
Tracks whether request comes from human UI or agent/API caller.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class AgentMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        agent_id = request.headers.get("X-Agent-ID")
        request.state.agent_id = agent_id
        request.state.is_agent_call = agent_id is not None
        response = await call_next(request)
        if agent_id:
            response.headers["X-Agent-ID"] = agent_id
        return response

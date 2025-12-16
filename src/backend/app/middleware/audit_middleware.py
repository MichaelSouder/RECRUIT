from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to capture request context for audit logs"""
    
    async def dispatch(self, request: Request, call_next):
        # Store request context for use in audit logging
        # Get IP address from client or forwarded headers
        ip_address = request.client.host if request.client else None
        if not ip_address:
            # Check for forwarded IP (from proxy/load balancer)
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                ip_address = forwarded_for.split(",")[0].strip()
        
        request.state.ip_address = ip_address
        request.state.user_agent = request.headers.get("user-agent")
        request.state.session_id = request.headers.get("X-Session-ID")  # Custom header or cookie
        
        response = await call_next(request)
        return response






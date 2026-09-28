import pytest
from fastapi import FastAPI, APIRouter
from httpx import ASGITransport, AsyncClient
from app.core.errors import (
    SentinelException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    RateLimitException,
    sentinel_exception_handler,
    global_exception_handler,
)


def create_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.add_exception_handler(SentinelException, sentinel_exception_handler)
    test_app.add_exception_handler(Exception, global_exception_handler)

    @test_app.middleware("http")
    async def error_handling_middleware(request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            return await global_exception_handler(request, exc)

    router = APIRouter()

    @router.get("/trigger-unauthorized")
    async def trigger_unauthorized():
        raise UnauthorizedException("Invalid token signature")

    @router.get("/trigger-forbidden")
    async def trigger_forbidden():
        raise ForbiddenException("Developer role cannot modify policies")

    @router.get("/trigger-not-found")
    async def trigger_not_found():
        raise NotFoundException("Incident", "INC-999")

    @router.get("/trigger-rate-limit")
    async def trigger_rate_limit():
        raise RateLimitException("Too many events submitted")

    @router.get("/trigger-unhandled")
    async def trigger_unhandled():
        # Deliberate internal crash simulation
        raise ValueError("Sensitive database syntax error: SELECT * FROM secret_table")

    test_app.include_router(router)
    return test_app


@pytest.mark.asyncio
async def test_unauthorized_error_format():
    test_app = create_test_app()
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/trigger-unauthorized")
        assert res.status_code == 401
        data = res.json()
        assert data["error"]["code"] == "UNAUTHORIZED"
        assert "Invalid token signature" in data["error"]["message"]


@pytest.mark.asyncio
async def test_forbidden_error_format():
    test_app = create_test_app()
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/trigger-forbidden")
        assert res.status_code == 403
        data = res.json()
        assert data["error"]["code"] == "FORBIDDEN"
        assert "Developer role" in data["error"]["message"]


@pytest.mark.asyncio
async def test_not_found_error_format():
    test_app = create_test_app()
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/trigger-not-found")
        assert res.status_code == 404
        data = res.json()
        assert data["error"]["code"] == "NOT_FOUND"
        assert "INC-999" in data["error"]["message"]


@pytest.mark.asyncio
async def test_unhandled_exception_does_not_leak_internals():
    test_app = create_test_app()
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/trigger-unhandled")
        assert res.status_code == 500
        data = res.json()
        # Ensure raw exception message and SQL query are NEVER leaked in response
        assert "SELECT * FROM secret_table" not in str(data)
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "request_id" in data["error"]


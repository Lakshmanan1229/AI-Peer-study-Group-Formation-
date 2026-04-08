from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.middleware.rate_limit import limiter

# Disable rate limiting during tests
limiter.enabled = False

# ---------------------------------------------------------------------------
# pytest-asyncio configuration
# ---------------------------------------------------------------------------

pytest_plugins = ("pytest_asyncio",)


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")


# Use asyncio_mode="auto" so every async test/fixture runs automatically
import pytest_asyncio  # noqa: E402  (re-import to satisfy linters)

# ---------------------------------------------------------------------------
# In-memory SQLite engine (no PostgreSQL required for tests)
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

TestingSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncSession:
    """Create all tables in the in-memory SQLite database and yield a session."""
    # Import models to register them with Base.metadata
    import app.models  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_client(test_db: AsyncSession):
    """Return an AsyncClient whose get_db dependency is overridden with test_db."""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_student_data() -> dict:
    return {
        "email": "teststudent@example.com",
        "password": "SecurePass123",
        "full_name": "Test Student",
        "department": "CSE",
        "year": 2,
        "cgpa": 8.5,
        "learning_pace": "moderate",
    }


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_client: AsyncClient, sample_student_data: dict) -> dict:
    """Register a student and return Authorization headers."""
    resp = await test_client.post("/v1/auth/register", json=sample_student_data)
    assert resp.status_code in (200, 201), resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def admin_headers(test_client: AsyncClient, test_db: AsyncSession) -> dict:
    """Create an admin user directly in the DB and return Authorization headers."""
    from app.middleware.security import create_access_token, hash_password
    from app.models.student import RoleEnum, Student

    admin = Student(
        email="admin@example.com",
        hashed_password=hash_password("AdminPass123"),
        full_name="Admin User",
        department="CSE",
        year=1,
        cgpa=9.0,
        learning_pace="fast",
        role=RoleEnum.admin,
    )
    test_db.add(admin)
    await test_db.commit()
    await test_db.refresh(admin)

    token = create_access_token(str(admin.id))
    return {"Authorization": f"Bearer {token}"}

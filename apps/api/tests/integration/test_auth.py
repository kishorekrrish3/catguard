import pytest

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_login_no_credentials(client):
    response = await client.post("/api/auth/login", json={"email": "nobody@test.com", "password": "bad"})
    assert response.status_code == 401
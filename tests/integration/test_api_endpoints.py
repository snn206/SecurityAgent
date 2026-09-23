"""Integration tests for all SecurityAgent REST API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from security_agent.api.app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_health_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ("ok", "healthy")


@pytest.mark.asyncio
async def test_providers_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/providers")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 8


@pytest.mark.asyncio
async def test_tools_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/tools")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        tool_ids = [t.get("id", t["name"]).lower() for t in data]
        assert "nmap" in tool_ids
        assert "gobuster" in tool_ids


@pytest.mark.asyncio
async def test_memory_crud_api(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a Golden Rule
        post_res = await client.post(
            "/api/v1/memory",
            json={
                "collection": "golden_rules",
                "title": "API Integration Rule",
                "content": "Always verify SSL certs before sending exploits",
                "target": "all",
                "category": "safety",
                "recommended_flags": "--verify-ssl",
            },
        )
        assert post_res.status_code == 201
        post_data = post_res.json()
        doc_id = post_data["_id"]
        assert doc_id is not None

        # 2. List memories
        list_res = await client.get("/api/v1/memory?collection=golden_rules")
        assert list_res.status_code == 200
        list_data = list_res.json()
        assert any(item["_id"] == doc_id for item in list_data["items"])

        # 3. Update memory
        put_res = await client.put(
            f"/api/v1/memory/golden_rules/{doc_id}",
            json={"title": "Updated API Rule", "content": "Updated rule content"},
        )
        assert put_res.status_code == 200

        # 4. Get specific memory
        get_res = await client.get(f"/api/v1/memory/golden_rules/{doc_id}")
        assert get_res.status_code == 200
        assert get_res.json()["title"] == "Updated API Rule"

        # 5. Delete memory
        del_res = await client.delete(f"/api/v1/memory/golden_rules/{doc_id}")
        assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_hierarchy_and_queue_api(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get topology
        topo_res = await client.get("/api/v1/hierarchy")
        assert topo_res.status_code == 200
        topo = topo_res.json()
        assert topo["max_limit"] == 10
        assert topo["coordinator"]["role"] == "coordinator"
        assert len(topo["parents"]) == 3

        # 2. Get queue status
        q_res = await client.get("/api/v1/hierarchy/queue")
        assert q_res.status_code == 200
        q_data = q_res.json()
        assert q_data["max_parent_slots"] == 3

        # 3. Enqueue task
        enq_res = await client.post(
            "/api/v1/hierarchy/queue",
            json={
                "title": "Integration Test Task",
                "goal": "Scan ports on target",
                "target": "10.0.0.1",
                "domain": "recon",
                "priority": 1,
            },
        )
        assert enq_res.status_code == 201


@pytest.mark.asyncio
async def test_react_ui_serving(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        # Verify served HTML has root div and title
        assert '<div id="root">' in res.text
        assert "SECURITY_AGENT" in res.text

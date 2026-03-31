import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app, activities


@pytest.mark.anyio
async def test_get_activities():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


@pytest.mark.anyio
async def test_signup_duplicate_and_delete_cycle():
    activity_name = "Chess Club"
    email = "temp-testuser@mergington.edu"

    # cleanup before test run
    participants = activities[activity_name]["participants"]
    if email in participants:
        participants.remove(email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        signup_response = await client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )
        assert signup_response.status_code == 200
        assert "Signed up" in signup_response.json().get("message", "")

        # confirm participant added
        assert email in activities[activity_name]["participants"]

        # duplicate registration fails
        duplicate_response = await client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )
        assert duplicate_response.status_code == 400

        # remove participant
        remove_response = await client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert remove_response.status_code == 200
        assert email not in activities[activity_name]["participants"]

        # remove again returns 404
        remove_again_response = await client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert remove_again_response.status_code == 404

def test_consent_given(client):
    """Test that consent can be given by a participant."""

    response = client.post("/api/participants/consent", json={"participant_id": "testuser1", "consent": True})
    assert response.status_code == 200
    data = response.json()
    assert data["participant_id"] == "testuser1"
    assert data["consent"] is True


def test_consent_declined(client):
    """Test that consent can be declined by a participant."""

    response = client.post("/api/participants/consent", json={"participant_id": "testuser2", "consent": False})
    assert response.status_code == 200
    data = response.json()
    assert data["participant_id"] == "testuser2"
    assert data["consent"] is False

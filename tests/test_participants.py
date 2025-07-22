import pytest


@pytest.mark.usefixtures("client")
class TestParticipants:
    """Test suite for participant-related API endpoints."""

    def test_consent_given(self, client):
        """Test that consent can be given by a participant."""

        response = client.post(
            "/api/participants/consent",
            json={"participant_id": "testuser1", "consent": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["participant_id"] == "testuser1"
        assert data["consent"] is True

    def test_consent_declined(self, client):
        """Test that consent can be declined by a participant."""

        response = client.post(
            "/api/participants/consent",
            json={"participant_id": "testuser2", "consent": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["participant_id"] == "testuser2"
        assert data["consent"] is False

    def test_participant_exists(self, client):
        """Test participant existence checks."""

        # Register a participant
        client.post(
            "/api/participants/consent",
            json={"participant_id": "exists1", "consent": True},
        )
        # Check existence
        response = client.post(
            "/api/participants/participant-exists", json={"participant_id": "exists1"}
        )
        assert response.status_code == 200
        assert response.json()["exists"] is True

        # Check non-existent participant
        response = client.post(
            "/api/participants/participant-exists", json={"participant_id": "notfound"}
        )
        assert response.status_code == 200
        assert response.json()["exists"] is False

    def test_revoke_consent(self, client):
        """Test revoking consent from a participant."""

        # Register and then revoke
        client.post(
            "/api/participants/consent",
            json={"participant_id": "revoke1", "consent": True},
        )
        response = client.post(
            "/api/participants/revoke-consent", json={"participant_id": "revoke1"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["participant_id"] == "revoke1"
        assert data["consent"] is False

    def test_submit_experience(self, client):
        """Test submitting experience information for a participant."""

        # Register and submit experience
        client.post(
            "/api/participants/consent",
            json={"participant_id": "exp1", "consent": True},
        )
        response = client.post(
            "/api/participants/experience",
            json={"participant_id": "exp1", "python_yoe": 3},
        )
        assert response.status_code == 200
        assert response.json()["participant_id"] == "exp1"

    def test_revoke_consent_not_found(self, client):
        """Test revoking consent for a non-existent participant."""

        response = client.post(
            "/api/participants/revoke-consent", json={"participant_id": "notfound"}
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Participant not found"}

    def test_revoke_consent_already_declined(self, client):
        """Test revoking consent for a participant who has already declined."""

        # Register and decline consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "declined1", "consent": False},
        )

        response = client.post(
            "/api/participants/revoke-consent", json={"participant_id": "declined1"}
        )
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Consent has already been revoked or declined."
        }

    def test_submit_experience_not_found(self, client):
        """Test submitting experience for a non-existent participant."""

        response = client.post(
            "/api/participants/experience",
            json={"participant_id": "notfound", "python_yoe": 2},
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "Participant not found"}

    def test_submit_experience_consent_declined(self, client):
        """Test submitting experience for a participant who has declined consent."""

        # Register and decline consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "declined_exp", "consent": False},
        )

        response = client.post(
            "/api/participants/experience",
            json={"participant_id": "declined_exp", "python_yoe": 1},
        )
        assert response.status_code == 403
        assert response.json() == {"detail": "Consent is required to continue."}

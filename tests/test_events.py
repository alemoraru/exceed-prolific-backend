import pytest


@pytest.mark.usefixtures("client")
class TestEvents:
    """Test suite for logging events (API) in the application."""

    def test_log_event_success(self, client):
        """Test logging an event successfully after participant registration and consent."""

        # Register participant and give consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "eventuser1", "consent": True},
        )
        # Log event
        response = client.post(
            "/api/events/event",
            json={"participant_id": "eventuser1", "event_type": "tab_switch"},
        )
        assert response.status_code == 200

    def test_log_event_no_consent(self, client):
        """Test that logging an event fails if consent has not been given."""

        # Register participant without giving consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "eventuser2", "consent": False},
        )

        # Try to log event
        response = client.post(
            "/api/events/event",
            json={"participant_id": "eventuser2", "event_type": "copy_paste"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to record events."

    def test_log_event_participant_not_found(self, client):
        """Test that logging an event fails if the participant does not exist."""

        # Try to log event for a non-existent participant
        response = client.post(
            "/api/events/event",
            json={"participant_id": "notfound", "event_type": "window_blur"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_log_event_missing_fields(self, client):
        """Test that logging an event fails if required fields are missing."""

        # Register participant and give consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "eventuser3", "consent": True},
        )

        # Log event with missing fields
        response = client.post(
            "/api/events/event",
            json={
                "participant_id": "eventuser3",
                # "event_type" missing
                "timestamp": "1721650000003",
            },
        )
        assert response.status_code == 422

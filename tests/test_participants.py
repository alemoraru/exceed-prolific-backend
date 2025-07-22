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

    def test_get_questions_requires_consent(self, client):
        """Register participant without consent and try to get questions."""

        client.post(
            "/api/participants/consent",
            json={"participant_id": "no_consent", "consent": False},
        )
        response = client.get(
            "/api/participants/questions", params={"participant_id": "no_consent"}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to continue."

    def test_get_questions_participant_not_found(self, client):
        """Test getting questions for a non-existent participant."""

        response = client.get(
            "/api/participants/questions", params={"participant_id": "notfound"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_submit_question_participant_not_found(self, client):
        """Test answering a question for a non-existent participant."""

        response = client.post(
            "/api/participants/question",
            json={
                "participant_id": "non_existing_participant",
                "question_id": "0",
                "answer": "0",
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_submit_question_invalid_answer_type(self, client):
        """Test submitting a question with an invalid answer type."""

        client.post(
            "/api/participants/consent",
            json={"participant_id": "invalid_answer", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "invalid_answer", "python_yoe": 1},
        )
        questions = client.get(
            "/api/participants/questions", params={"participant_id": "invalid_answer"}
        ).json()

        # Get question ID
        qid = (
            questions[0]["id"] if "id" in questions[0] else list(questions[0].keys())[0]
        )

        # Submit invalid answer (integer instead of string of an int)
        response = client.post(
            "/api/participants/question",
            json={
                "participant_id": "invalid_answer",
                "question_id": qid,
                "answer": 0,  # should be a string like "0"
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 422

    def test_submit_question_correct(self, client):
        """Test submitting a question with a valid answer (Good weather case)."""

        client.post(
            "/api/participants/consent",
            json={"participant_id": "id_test", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "id_test", "python_yoe": 1},
        )
        questions = client.get(
            "/api/participants/questions", params={"participant_id": "id_test"}
        ).json()
        qid = (
            questions[0]["id"] if "id" in questions[0] else list(questions[0].keys())[0]
        )
        # Submit answer
        response = client.post(
            "/api/participants/question",
            json={
                "participant_id": "id_test",
                "question_id": qid,
                "answer": "0",
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 200
        assert response.json()["participant_id"] == "id_test"
        assert response.json()["question_id"] == qid

    def test_submit_question_non_existing_question_id(self, client):
        """Test submitting a question with a question ID that doesn't exist."""

        client.post(
            "/api/participants/consent",
            json={"participant_id": "invalid_qid", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "invalid_qid", "python_yoe": 1},
        )
        # Try to submit to a question ID that doesn't exist
        response = client.post(
            "/api/participants/question",
            json={
                "participant_id": "invalid_qid",
                "question_id": "not_a_real_qid",  # Valid ID according to the schema, but non-existing
                "answer": "0",
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "MCQ answer map not found or question not served to participant"
        )

    def test_submit_question_already_answered(self, client):
        """Test submitting a question that has already been answered."""

        # Register and set up participant
        client.post(
            "/api/participants/consent",
            json={"participant_id": "already_answered", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "already_answered", "python_yoe": 1},
        )
        questions = client.get(
            "/api/participants/questions", params={"participant_id": "already_answered"}
        ).json()
        qid = (
            questions[0]["id"] if "id" in questions[0] else list(questions[0].keys())[0]
        )

        # Submit answer
        client.post(
            "/api/participants/question",
            json={
                "participant_id": "already_answered",
                "question_id": qid,
                "answer": "0",
                "time_taken_ms": 1000,
            },
        )

        # Try to submit the same question again
        response = client.post(
            "/api/participants/question",
            json={
                "participant_id": "already_answered",
                "question_id": qid,
                "answer": "1",  # Different answer
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Question already answered"

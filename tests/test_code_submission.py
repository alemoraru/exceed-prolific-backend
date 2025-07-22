import pytest


@pytest.mark.usefixtures("client")
class TestCodeSubmission:
    """
    Test suite for code submission functionality in the application.
    This includes submitting code snippets & retrieving code snippets.
    """

    def test_submit_code_success(self, client, monkeypatch):
        """Test successful code submission with valid participant and intervention type."""

        # Register participant with consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "submituser1", "consent": True},
        )
        # Assign experience
        client.post(
            "/api/participants/experience",
            json={"participant_id": "submituser1", "python_yoe": 2},
        )

        # Get MCQ questions to trigger intervention assignment
        questions = client.get(
            "/api/participants/questions", params={"participant_id": "submituser1"}
        ).json()

        # Answer all MCQs to trigger intervention assignment
        for q in questions:
            qid = q["id"] if "id" in q else list(q.keys())[0]
            client.post(
                "/api/participants/question",
                json={
                    "participant_id": "submituser1",
                    "question_id": qid,
                    "answer": "0",
                    "time_taken_ms": 1000,
                },
            )
        # Patch evaluate_code to return dummy values
        monkeypatch.setattr(
            "app.api.code_submission.evaluate_code",
            lambda code, snippet_id, intervention_type: ("success", "", 1, 1),
        )

        # Submit code
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "submituser1",
                "snippet_id": "0",
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["participant_id"] == "submituser1"
        assert data["snippet_id"] == "0"
        assert data["status"] == "success"

    def test_submit_code_no_participant(self, client):
        """Test that code submission fails if participant does not exist."""

        # Try to submit code for a non-existent participant
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "notfound",
                "snippet_id": "snippetA",
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_submit_code_no_consent(self, client):
        """Test that code submission fails if consent has not been given."""

        # Register participant without giving consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "submituser2", "consent": False},
        )

        # Try to submit code
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "submituser2",
                "snippet_id": "snippetA",
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to continue."

    def test_submit_code_no_intervention_type(self, client):
        """
        Test that code submission fails if intervention type is not assigned.
        Intervention type is not set if a participant did not complete the first part of
        the study, namely the experience + MCQs.
        """

        # Register participant and give consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "submituser3", "consent": True},
        )

        # Assign experience but do not set intervention_type
        client.post(
            "/api/participants/experience",
            json={"participant_id": "submituser3", "python_yoe": 2},
        )

        # Do not assign intervention_type
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "submituser3",
                "snippet_id": "snippetA",
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Intervention type not assigned for participant."
        )

    def test_get_code_snippet_no_participant(self, client):
        """Test that getting a code snippet fails if participant does not exist."""

        # Try to get code snippet for a non-existent participant
        response = client.get(
            "/api/code/snippet/snippetA",
            params={"participant_id": "notfound"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_get_code_snippet_no_consent(self, client):
        """Test that getting a code snippet fails if consent has not been given."""

        # Register participant without giving consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "snippetuser2", "consent": False},
        )

        # Try to get code snippet
        response = client.get(
            "/api/code/snippet/snippetA",
            params={"participant_id": "snippetuser2"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to continue."

    def test_get_code_snippet_not_found(self, client):
        """Test that getting a code snippet fails if the snippet does not exist."""

        # Register participant and give consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "snippetuser3", "consent": True},
        )

        # Try to get a non-existent code snippet
        response = client.get(
            "/api/code/snippet/notarealsnippet",
            params={"participant_id": "snippetuser3"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Snippet not found"

    def test_get_code_snippet_success(self, client):
        """Test successful retrieval of a code snippet."""

        # Register participant and give consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "snippetuser1", "consent": True},
        )

        # Get code snippet
        response = client.get(
            "/api/code/snippet/0",
            params={"participant_id": "snippetuser1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "0"
        # We omit the actual code content check here

import pytest


@pytest.mark.usefixtures("client")
class TestCodeSubmission:
    """
    Test suite for code submission functionality in the application.
    This includes submitting code snippets & retrieving code snippets.
    """

    def test_submit_code_success(self, client, monkeypatch):
        """Test successful code submission with valid participant and intervention type and assigned snippet."""

        client.post(
            "/api/participants/consent",
            json={"participant_id": "codesubmit", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "codesubmit", "python_yoe": 2},
        )
        questions = client.get(
            "/api/participants/questions", params={"participant_id": "codesubmit"}
        ).json()
        for q in questions:
            qid = q["id"] if "id" in q else list(q.keys())[0]
            client.post(
                "/api/participants/question",
                json={
                    "participant_id": "codesubmit",
                    "question_id": qid,
                    "answer": "0",
                    "time_taken_ms": 1000,
                },
            )

        # Patch get_rephrased_error_message to return a dummy string value
        monkeypatch.setattr(
            "app.api.code.get_rephrased_error_message",
            lambda code_snippet, error_msg, intervention_type: "Rephrased error message",
        )

        response = client.get(
            "/api/code/snippet",
            params={"participant_id": "codesubmit"},
        )

        assert response.status_code == 200
        snippet_id = response.json()["id"]

        # Patch evaluate_code to return dummy values
        monkeypatch.setattr(
            "app.api.code.evaluate_code",
            lambda code, code_snippet_id: ("success", "", 1, 1),
        )

        # Submit code
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "codesubmit",
                "snippet_id": snippet_id,
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["participant_id"] == "codesubmit"
        assert data["snippet_id"] == snippet_id
        assert data["status"] == "success"

    def test_submit_code_too_many_attempts(self, client, monkeypatch):
        """Test that code submission fails if the participant has already submitted too many attempts."""

        # Set up participant and initial conditions
        client.post(
            "/api/participants/consent",
            json={"participant_id": "codesubmit", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "codesubmit", "python_yoe": 2},
        )
        questions = client.get(
            "/api/participants/questions", params={"participant_id": "codesubmit"}
        ).json()
        for q in questions:
            qid = q["id"] if "id" in q else list(q.keys())[0]
            client.post(
                "/api/participants/question",
                json={
                    "participant_id": "codesubmit",
                    "question_id": qid,
                    "answer": "0",
                    "time_taken_ms": 1000,
                },
            )

        # Patch get_rephrased_error_message to return a dummy string value
        monkeypatch.setattr(
            "app.api.code.get_rephrased_error_message",
            lambda code_snippet, error_msg, intervention_type: "Rephrased error message",
        )

        response = client.get(
            "/api/code/snippet",
            params={"participant_id": "codesubmit"},
        )

        assert response.status_code == 200
        snippet_id = response.json()["id"]

        # Patch evaluate_code to return dummy values
        monkeypatch.setattr(
            "app.api.code.evaluate_code",
            lambda code, code_snippet_id: ("success", "", 1, 1),
        )

        # Submit code (1st attempt)
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "codesubmit",
                "snippet_id": snippet_id,
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 200

        # Submit code (2nd attempt)
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "codesubmit",
                "snippet_id": snippet_id,
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 200

        # Submit code (3rd attempt)
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "codesubmit",
                "snippet_id": snippet_id,
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 200

        # Submit code (4th attempt) - should fail
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "codesubmit",
                "snippet_id": snippet_id,
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "Maximum number of attempts (3) reached for this snippet."
        )

    def test_submit_code_snippet_id_mismatch(self, client, monkeypatch):
        """Test that code submission fails if submitted snippet_id does not match assigned snippet_id."""
        client.post(
            "/api/participants/consent",
            json={"participant_id": "submituserX", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "submituserX", "python_yoe": 2},
        )
        questions = client.get(
            "/api/participants/questions", params={"participant_id": "submituserX"}
        ).json()
        for q in questions:
            qid = q["id"] if "id" in q else list(q.keys())[0]
            client.post(
                "/api/participants/question",
                json={
                    "participant_id": "submituserX",
                    "question_id": qid,
                    "answer": "0",
                    "time_taken_ms": 1000,
                },
            )
        wrong_snippet_id = "wrong_snippet"
        response = client.post(
            "/api/code/submit",
            json={
                "participant_id": "submituserX",
                "snippet_id": wrong_snippet_id,
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You can only submit code for your assigned snippet."
        )

    def test_get_code_snippet_success(self, client, monkeypatch):
        """Test successful retrieval of a code snippet using participant ID only."""
        client.post(
            "/api/participants/consent",
            json={"participant_id": "snippetuser1", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "snippetuser1", "python_yoe": 2},
        )
        questions = client.get(
            "/api/participants/questions", params={"participant_id": "snippetuser1"}
        ).json()
        for q in questions:
            qid = q["id"] if "id" in q else list(q.keys())[0]
            client.post(
                "/api/participants/question",
                json={
                    "participant_id": "snippetuser1",
                    "question_id": qid,
                    "answer": "0",
                    "time_taken_ms": 1000,
                },
            )

        # Patch get_rephrased_error_message to return a dummy string value
        monkeypatch.setattr(
            "app.api.code.get_rephrased_error_message",
            lambda code_snippet, error_msg, intervention_type: "Rephrased error message",
        )

        response = client.get(
            "/api/code/snippet",
            params={"participant_id": "snippetuser1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "code" in data
        assert "error" in data
        assert "markdown" in data

    def test_get_code_snippet_no_participant(self, client):
        """Test that getting a code snippet fails if participant does not exist."""
        response = client.get(
            "/api/code/snippet",
            params={"participant_id": "notfound"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_get_code_snippet_no_consent(self, client):
        """Test that getting a code snippet fails if consent has not been given."""
        client.post(
            "/api/participants/consent",
            json={"participant_id": "snippetuser2", "consent": False},
        )
        response = client.get(
            "/api/code/snippet",
            params={"participant_id": "snippetuser2"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to continue."

    def test_submit_code_no_participant(self, client):
        """Test that code submission fails if participant does not exist."""
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
        client.post(
            "/api/participants/consent",
            json={"participant_id": "submituser2", "consent": False},
        )
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
        This test also covers the case where no snippet is assigned, since both
        intervention type and snippet are assigned together.
        """
        client.post(
            "/api/participants/consent",
            json={"participant_id": "submituser3", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "submituser3", "python_yoe": 2},
        )
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

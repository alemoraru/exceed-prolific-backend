import pytest


@pytest.mark.usefixtures("client")
class TestFeedbackSubmission:
    """
    Test suite for error feedback submission API endpoint.
    """

    @staticmethod
    def setup_participant_and_submission(
        client, participant_id="fbuser1", snippet_id="0", attempt_number=1
    ):
        """
        Helper method to set up a participant with consent, experience, and a code submission.
        :param client: the test client to use for API requests.
        :param participant_id: the ID of the participant to set up.
        :param snippet_id: the ID of the code snippet to use for submission.
        :param attempt_number: the attempt number for the code submission (default is 1).
        :return: None
        """

        # Register participant with consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": participant_id, "consent": True},
        )
        # Assign experience
        client.post(
            "/api/participants/experience",
            json={"participant_id": participant_id, "python_yoe": 2},
        )
        # Complete MCQs to assign intervention_type
        questions = client.get(
            "/api/participants/questions", params={"participant_id": participant_id}
        ).json()
        for q in questions:
            qid = q["id"] if "id" in q else list(q.keys())[0]
            client.post(
                "/api/participants/question",
                json={
                    "participant_id": participant_id,
                    "question_id": qid,
                    "answer": "0",
                    "time_taken_ms": 1000,
                },
            )
        # Submit code to create a CodeSubmission
        client.post(
            "/api/code/submit",
            json={
                "participant_id": participant_id,
                "snippet_id": snippet_id,
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )

    def test_submit_feedback_success(self, client):
        """Test successful feedback submission after participant registration and code submission."""

        self.setup_participant_and_submission(client)
        response = client.post(
            "/api/errors/feedback",
            json={
                "participant_id": "fbuser1",
                "snippet_id": "0",
                "attempt_number": 1,
                "authoritativeness": 5,
                "cognitive_load": 4,
                "readability": 3,
                "timestamp": "1234567890",
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_submit_feedback_no_participant(self, client):
        """Test that feedback submission fails if participant does not exist."""

        response = client.post(
            "/api/errors/feedback",
            json={
                "participant_id": "notfound",
                "snippet_id": "0",
                "attempt_number": 1,
                "authoritativeness": 5,
                "cognitive_load": 4,
                "readability": 3,
                "timestamp": "1234567890",
            },
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_submit_feedback_no_consent(self, client):
        """Test that feedback submission fails if consent has not been given."""

        client.post(
            "/api/participants/consent",
            json={"participant_id": "fbuser2", "consent": False},
        )
        response = client.post(
            "/api/errors/feedback",
            json={
                "participant_id": "fbuser2",
                "snippet_id": "0",
                "attempt_number": 1,
                "authoritativeness": 5,
                "cognitive_load": 4,
                "readability": 3,
                "timestamp": "1234567890",
            },
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to continue."

    def test_submit_feedback_invalid_attempt_number(self, client):
        """Test that feedback submission fails if attempt number is not 1 or 2."""

        self.setup_participant_and_submission(client)
        response = client.post(
            "/api/errors/feedback",
            json={
                "participant_id": "fbuser1",
                "snippet_id": "0",
                "attempt_number": 3,
                "authoritativeness": 5,
                "cognitive_load": 4,
                "readability": 3,
                "timestamp": "1234567890",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Attempt number must be either 1 or 2"

    @pytest.mark.parametrize(
        "authoritativeness,cognitive_load,readability",
        [
            (0, 4, 3),
            (5, 0, 3),
            (5, 4, 6),
        ],
    )
    def test_submit_feedback_invalid_likert(
        self, client, authoritativeness, cognitive_load, readability
    ):
        """Test that feedback submission fails if Likert ratings are out of range."""

        self.setup_participant_and_submission(client)
        response = client.post(
            "/api/errors/feedback",
            json={
                "participant_id": "fbuser1",
                "snippet_id": "0",
                "attempt_number": 1,
                "authoritativeness": authoritativeness,
                "cognitive_load": cognitive_load,
                "readability": readability,
                "timestamp": "1234567890",
            },
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Feedback ratings must be integers between 1 and 5"
        )

    def test_submit_feedback_no_submission(self, client):
        """Test that error feedback submission fails if no associated code submission exists."""

        # Register participant and give consent, but do not submit code
        client.post(
            "/api/participants/consent",
            json={"participant_id": "fbuser3", "consent": True},
        )

        client.post(
            "/api/participants/experience",
            json={"participant_id": "fbuser3", "python_yoe": 2},
        )

        questions = client.get(
            "/api/participants/questions", params={"participant_id": "fbuser3"}
        ).json()

        for q in questions:
            qid = q["id"] if "id" in q else list(q.keys())[0]
            client.post(
                "/api/participants/question",
                json={
                    "participant_id": "fbuser3",
                    "question_id": qid,
                    "answer": "0",
                    "time_taken_ms": 1000,
                },
            )

        # Try to submit feedback without a code submission
        response = client.post(
            "/api/errors/feedback",
            json={
                "participant_id": "fbuser3",
                "snippet_id": "0",
                "attempt_number": 1,
                "authoritativeness": 5,
                "cognitive_load": 4,
                "readability": 3,
                "timestamp": "1234567890",
            },
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Submission not found for feedback"

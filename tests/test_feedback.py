from http.client import responses

import pytest


@pytest.mark.usefixtures("client")
class TestFeedbackSubmission:
    """
    Test suite for error feedback submission API endpoint.
    """

    @staticmethod
    def setup_participant_and_submission(client, participant_id) -> str:
        """
        Helper method to set up a participant with consent, experience, and a code submission.
        :param client: the test client to use for API requests.
        :param participant_id: the ID of the participant to set up.
        :return: The snippet ID of the code submission created for the participant.
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

        # Complete MCQs to assign skill level, intervention type, and snippet ID
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

        # Get code snippet for the participant (creates feedback entry)
        response = client.get(
            "/api/code/snippet",
            params={"participant_id": participant_id},
        )

        # Get the snippet ID from the response
        snippet_id = response.json()["id"]

        # Submit code fix for the same participant
        client.post(
            "/api/code/submit",
            json={
                "participant_id": participant_id,
                "snippet_id": snippet_id,
                "code": "print('hello')",
                "time_taken_ms": 1234,
            },
        )
        return snippet_id

    @staticmethod
    def setup_monkeypatch_for_evaluation(monkeypatch):
        """Helper method to set up monkeypatches for evaluation functions."""

        # Patch get_rephrased_error_message to return a dummy string value
        monkeypatch.setattr(
            "app.api.code.get_rephrased_error_message",
            lambda code_snippet, error_msg, intervention_type: "Rephrased error message",
        )

        # Patch evaluate_code to return dummy values
        monkeypatch.setattr(
            "app.api.code.evaluate_code",
            lambda code, code_snippet_id: ("success", "", 1, 1),
        )

    def test_submit_readability_feedback_success(self, client, monkeypatch):
        """Test successful feedback submission after participant registration and code submission."""

        # Set up participant and code submission, get correct snippet_id
        self.setup_monkeypatch_for_evaluation(monkeypatch)
        snippet_id = self.setup_participant_and_submission(client, "fbuser1")

        # Submit readability feedback
        response = client.post(
            "/api/errors/readability-feedback",
            json={
                "participant_id": "fbuser1",
                "snippet_id": snippet_id,
                "length": 4,
                "jargon": 3,
                "sentence_structure": 5,
                "vocabulary": 2,
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_readability_feedback_invalid_likert(self, client, monkeypatch):
        """Test readability feedback fails if Likert ratings are out of range."""

        # Set up participant and code submission, get correct snippet_id
        self.setup_monkeypatch_for_evaluation(monkeypatch)
        snippet_id = self.setup_participant_and_submission(client, "fbuser2")

        response = client.post(
            "/api/errors/readability-feedback",
            json={
                "participant_id": "fbuser2",
                "snippet_id": snippet_id,
                "length": 0,  # Invalid
                "jargon": 3,
                "sentence_structure": 5,
                "vocabulary": 2,
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 400
        assert (
            "readability ratings must be integers between 1 and 5"
            in response.json()["detail"].lower()
        )

    def test_readability_feedback_duplicate(self, client, monkeypatch):
        """Test readability feedback fails if already submitted for entry."""

        # Set up participant and code submission, get correct snippet_id
        self.setup_monkeypatch_for_evaluation(monkeypatch)
        snippet_id = self.setup_participant_and_submission(client, "fbuser3")

        response = client.post(
            "/api/errors/readability-feedback",
            json={
                "participant_id": "fbuser3",
                "snippet_id": snippet_id,
                "length": 4,
                "jargon": 3,
                "sentence_structure": 5,
                "vocabulary": 2,
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Submit again for the same snippet_id
        response = client.post(
            "/api/errors/readability-feedback",
            json={
                "participant_id": "fbuser3",
                "snippet_id": snippet_id,
                "length": 5,
                "jargon": 5,
                "sentence_structure": 5,
                "vocabulary": 5,
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is False

    def test_cognitive_load_feedback_success(self, client, monkeypatch):
        """Test successful cognitive load feedback submission."""

        # Set up participant and code submission, get correct snippet_id
        self.setup_monkeypatch_for_evaluation(monkeypatch)
        snippet_id = self.setup_participant_and_submission(client, "fbuser4")
        response = client.post(
            "/api/errors/cognitive-load-feedback",
            json={
                "participant_id": "fbuser4",
                "snippet_id": snippet_id,
                "intrinsic_load": 4,
                "extraneous_load": 3,
                "germane_load": 5,
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_cognitive_load_feedback_invalid_likert(self, client, monkeypatch):
        """Test cognitive load feedback fails if Likert ratings are out of range."""

        # Set up participant and code submission, get correct snippet_id
        self.setup_monkeypatch_for_evaluation(monkeypatch)
        snippet_id = self.setup_participant_and_submission(client, "fbuser5")
        response = client.post(
            "/api/errors/cognitive-load-feedback",
            json={
                "participant_id": "fbuser5",
                "snippet_id": snippet_id,
                "intrinsic_load": 0,
                "extraneous_load": 3,
                "germane_load": 5,
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 400
        assert (
            "cognitive load ratings must be integers between 1 and 5"
            in response.json()["detail"].lower()
        )

    def test_cognitive_load_feedback_duplicate(self, client, monkeypatch):
        """Test cognitive load feedback fails if already submitted for entry."""

        # Set up participant and code submission, get correct snippet_id
        self.setup_monkeypatch_for_evaluation(monkeypatch)
        snippet_id = self.setup_participant_and_submission(client, "fbuser6")

        response = client.post(
            "/api/errors/cognitive-load-feedback",
            json={
                "participant_id": "fbuser6",
                "snippet_id": snippet_id,
                "intrinsic_load": 4,
                "extraneous_load": 3,
                "germane_load": 5,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Submit again for the same snippet_id
        response = client.post(
            "/api/errors/cognitive-load-feedback",
            json={
                "participant_id": "fbuser6",
                "snippet_id": snippet_id,
                "intrinsic_load": 5,
                "extraneous_load": 5,
                "germane_load": 5,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 200
        assert response.json()["success"] is False

    def test_authoritativeness_feedback_success(self, client, monkeypatch):
        """Test successful authoritativeness feedback submission and ended_at update."""

        # Set up participant and code submission, get correct snippet_id
        self.setup_monkeypatch_for_evaluation(monkeypatch)
        snippet_id = self.setup_participant_and_submission(client, "fbuser7")

        response = client.post(
            "/api/errors/authoritativeness-feedback",
            json={
                "participant_id": "fbuser7",
                "snippet_id": snippet_id,
                "authoritativeness": 5,
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_authoritativeness_feedback_invalid_likert(self, client, monkeypatch):
        """Test authoritativeness feedback fails if Likert rating is out of range."""

        # Set up participant and code submission, get correct snippet_id
        self.setup_monkeypatch_for_evaluation(monkeypatch)
        snippet_id = self.setup_participant_and_submission(client, "fbuser8")
        response = client.post(
            "/api/errors/authoritativeness-feedback",
            json={
                "participant_id": "fbuser8",
                "snippet_id": snippet_id,
                "authoritativeness": 0,
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 400
        assert (
            "authoritativeness rating must be an integer between 1 and 5"
            in response.json()["detail"].lower()
        )

    def test_authoritativeness_feedback_duplicate(self, client, monkeypatch):
        """Test authoritativeness feedback fails if already submitted for entry."""

        # Set up participant and code submission, get correct snippet_id
        self.setup_monkeypatch_for_evaluation(monkeypatch)
        snippet_id = self.setup_participant_and_submission(client, "fbuser9")

        response = client.post(
            "/api/errors/authoritativeness-feedback",
            json={
                "participant_id": "fbuser9",
                "snippet_id": snippet_id,
                "authoritativeness": 5,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Submit again for the same snippet_id
        response = client.post(
            "/api/errors/authoritativeness-feedback",
            json={
                "participant_id": "fbuser9",
                "snippet_id": snippet_id,
                "authoritativeness": 4,
                "time_taken_ms": 1000,
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is False

    def test_readability_feedback_no_participant(self, client):
        """Test readability feedback submission fails if participant does not exist."""

        response = client.post(
            "/api/errors/readability-feedback",
            json={
                "participant_id": "fbuser10",
                "snippet_id": "A",
                "length": 1,
                "jargon": 3,
                "sentence_structure": 5,
                "vocabulary": 2,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_readability_feedback_no_consent(self, client):
        """Test readability feedback submission fails if participant has not given consent."""

        # Register participant without consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "fbuser11", "consent": False},
        )

        response = client.post(
            "/api/errors/readability-feedback",
            json={
                "participant_id": "fbuser11",
                "snippet_id": "A",
                "length": 1,
                "jargon": 3,
                "sentence_structure": 5,
                "vocabulary": 2,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to continue."

    def test_cognitive_load_feedback_no_participant(self, client):
        """Test cognitive load feedback submission fails if participant does not exist."""

        response = client.post(
            "/api/errors/cognitive-load-feedback",
            json={
                "participant_id": "fbuser12",
                "snippet_id": "A",
                "intrinsic_load": 1,
                "extraneous_load": 2,
                "germane_load": 3,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_cognitive_load_feedback_no_consent(self, client):
        """Test cognitive load feedback submission fails if participant has not given consent."""

        # Register participant without consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "fbuser13", "consent": False},
        )

        response = client.post(
            "/api/errors/cognitive-load-feedback",
            json={
                "participant_id": "fbuser13",
                "snippet_id": "A",
                "intrinsic_load": 1,
                "extraneous_load": 2,
                "germane_load": 3,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to continue."

    def test_authoritativeness_feedback_no_participant(self, client):
        """Test authoritativeness feedback submission fails if participant does not exist."""

        response = client.post(
            "/api/errors/authoritativeness-feedback",
            json={
                "participant_id": "fbuser14",
                "snippet_id": "A",
                "authoritativeness": 5,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_authoritativeness_feedback_no_consent(self, client):
        """Test authoritativeness feedback submission fails if participant has not given consent."""

        # Register participant without consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "fbuser15", "consent": False},
        )

        # Attempt to submit authoritativeness feedback
        response = client.post(
            "/api/errors/authoritativeness-feedback",
            json={
                "participant_id": "fbuser15",
                "snippet_id": "A",
                "authoritativeness": 5,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to continue."

    def test_readability_feedback_no_entry(self, client):
        """Test readability feedback submission fails if no feedback entry exists for participant."""

        # Register participant with consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "fbuser16", "consent": True},
        )

        # Attempt to submit readability feedback without a prior code submission
        response = client.post(
            "/api/errors/readability-feedback",
            json={
                "participant_id": "fbuser16",
                "snippet_id": "A",
                "length": 1,
                "jargon": 3,
                "sentence_structure": 5,
                "vocabulary": 2,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Feedback entry not found for update"

    def test_cognitive_load_feedback_no_entry(self, client):
        """Test cognitive load feedback submission fails if no feedback entry exists for participant."""

        # Register participant with consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "fbuser17", "consent": True},
        )

        # Attempt to submit cognitive load feedback without a prior code submission
        response = client.post(
            "/api/errors/cognitive-load-feedback",
            json={
                "participant_id": "fbuser17",
                "snippet_id": "A",
                "intrinsic_load": 1,
                "extraneous_load": 2,
                "germane_load": 3,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Feedback entry not found for update"

    def test_authoritativeness_feedback_no_entry(self, client):
        """Test authoritativeness feedback submission fails if no feedback entry exists for participant."""

        # Register participant with consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "fbuser18", "consent": True},
        )

        # Attempt to submit authoritativeness feedback without a prior code submission
        response = client.post(
            "/api/errors/authoritativeness-feedback",
            json={
                "participant_id": "fbuser18",
                "snippet_id": "A",
                "authoritativeness": 5,
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Feedback entry not found for update"

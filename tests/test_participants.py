import pytest

from app.api.participants import assess_skill_level, get_balanced_assignment


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

    def test_submit_question_answer_without_consent(self, client):
        """Test submitting a question without giving consent first."""

        # Register and set up participant
        client.post(
            "/api/participants/consent",
            json={"participant_id": "revoke_consent_after", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "revoke_consent_after", "python_yoe": 1},
        )
        questions = client.get(
            "/api/participants/questions",
            params={"participant_id": "revoke_consent_after"},
        ).json()
        qid = (
            questions[0]["id"] if "id" in questions[0] else list(questions[0].keys())[0]
        )

        # Revoke consent before submitting an answer to a question
        client.post(
            "/api/participants/revoke-consent",
            json={"participant_id": "revoke_consent_after"},
        )

        # Submit answer
        response = client.post(
            "/api/participants/question",
            json={
                "participant_id": "revoke_consent_after",
                "question_id": qid,
                "answer": "0",
                "time_taken_ms": 1000,
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Consent is required to continue."

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

    def test_answer_all_questions(self, client):
        """Test answering all questions for a participant."""

        # Register and set up participant
        client.post(
            "/api/participants/consent",
            json={"participant_id": "all_questions", "consent": True},
        )
        client.post(
            "/api/participants/experience",
            json={"participant_id": "all_questions", "python_yoe": 1},
        )
        questions = client.get(
            "/api/participants/questions", params={"participant_id": "all_questions"}
        ).json()

        # Answer all questions
        for question in questions:
            qid = question["id"] if "id" in question else list(question.keys())[0]
            response = client.post(
                "/api/participants/question",
                json={
                    "participant_id": "all_questions",
                    "question_id": qid,
                    "answer": "0",  # Random value, we don't care about correctness here
                    "time_taken_ms": 1000,
                },
            )
            assert response.status_code == 200
            assert response.json()["participant_id"] == "all_questions"
            assert response.json()["question_id"] == qid

    def test_completion_redirect_non_existing_participant(self, client):
        """Test completion redirect for a non-existing participant."""

        response = client.get(
            "/api/participants/completion-redirect",
            params={"participant_id": "non_existing"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"


    def test_completion_redirect_not_completed(self, client):
        """Test completion redirect fails if participant has not finished the study."""
        # Register and consent
        client.post(
            "/api/participants/consent",
            json={"participant_id": "redirect_not_completed", "consent": True},
        )
        # Do not set ended_at
        response = client.get(
            "/api/participants/completion-redirect",
            params={"participant_id": "redirect_not_completed"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Participant has not completed the study yet."


class TestSkillAssessment:
    """Test suite for skill assessment function."""

    def test_assess_skill_level_expert_by_mcq(self):
        """Test assessing skill level as expert based on MCQ performance."""
        assert assess_skill_level(6, 1) == "expert"
        assert assess_skill_level(8, 0) == "expert"

    def test_assess_skill_level_novice_by_mcq(self):
        """Test assessing skill level as novice based on MCQ performance."""
        assert assess_skill_level(3, 10) == "novice"
        assert assess_skill_level(0, 0) == "novice"

    def test_assess_skill_level_expert_by_experience(self):
        """Test assessing skill level as expert based on experience (used in conjunction with MCQ)."""
        assert assess_skill_level(4, 5) == "expert"
        assert assess_skill_level(5, 7) == "expert"

    def test_assess_skill_level_novice_by_experience(self):
        """Test assessing skill level as novice based on experience (used in conjunction with MCQ)."""
        assert assess_skill_level(4, 3) == "novice"
        assert assess_skill_level(5, 4) == "novice"


class TestBalancedAssignment:
    """Test suite for the balanced assignment function."""

    def test_get_balanced_assignment_least_assigned(self):
        """Test that the function returns the least assigned option."""
        options = ["A", "B", "C"]
        assigned = ["A", "A", "B"]

        # C is least assigned
        assert get_balanced_assignment(options, assigned) == "C"

    def test_get_balanced_assignment_tie(self):
        """Test that the function returns one of the least assigned options in case of a tie."""
        options = ["A", "B", "C"]
        assigned = ["A", "B", "C", "A", "B", "C"]

        # All have 2, so any is valid
        results = set(get_balanced_assignment(options, assigned) for _ in range(20))
        assert results.issubset(set(options))
        assert len(results) > 1  # Should be random among ties

    def test_get_balanced_assignment_empty(self):
        """Test that the function returns randomly from options when no assignments exist."""
        options = ["A", "B", "C"]
        assigned = []

        # All are least assigned
        results = set(get_balanced_assignment(options, assigned) for _ in range(10))
        assert results.issubset(set(options))
        assert len(results) > 1  # Should be random among all

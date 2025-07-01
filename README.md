# exceed-prolific-backend


Proposed Directory Structure for Backend

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── participants.py       # Consent + part 1
│   │   │   ├── code_submission.py    # Submit & evaluate code
│   │   │   └── intervention.py       # Trigger LLM-based feedback
│   ├── core/
│   │   ├── config.py                 # Env variables
│   │   └── security.py               # Malicious detection
│   ├── db/
│   │   ├── base.py                   # SQLAlchemy base
│   │   ├── models.py                 # Participant, submission, metadata
│   │   └── session.py
│   ├── services/
│   │   ├── evaluator.py              # Code compiler + test suite
│   │   ├── llm_intervention.py       # Calls LLM with context
│   │   └── state_manager.py          # Participant group balancing
│   ├── utils/
│   │   └── anti_cheat.py             # Keystroke speed, random typing checks
│   └── main.py                       # FastAPI app entry
├── tests/
│   └── ...
├── requirements.txt
└── Dockerfile
```
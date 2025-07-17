# EXCEED Prolific Backend

This repository contains the backend code for the EXCEED Prolific application, a study aimed at investigating code
understanding and error correction using Python code snippets and (automatically rephrased) error messages. The backend
is built with FastAPI and SQLAlchemy, and provides RESTful APIs for participant management, code submission, and error
intervention.

---

## 🧩 Stack Overview

- **Python 3.12**
- **FastAPI** for API endpoints
- **SQLAlchemy** for ORM and database management
- **Docker** for containerization
- **unittest** for testing (i.e., testing participant submitted code snippets)
- **Ollama/ChatGPT** clients for LLM rephrasing of error messages

---

## 🏗️ API Architecture

- Modular FastAPI routers for participants, code submissions, and interventions
- SQLAlchemy models for participants and submissions
- Evaluator service for syntax and semantic code checks
- LLM-based error rephrasing for educational feedback
- Data folder for code snippets, test suites, and error messages

---

## ⚡ QuickStart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/amoraru/exceed-prolific-backend.git
   cd exceed-prolific-backend
   ```
2. **Create a virtual environment in the root directory (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. **Access the API docs (Swagger Documentation):**
   Visit [http://localhost:8000/docs](http://localhost:8000/docs)

> Note: Without any explicit environment variables set, the application will default to using the ones defined in the
`.env` file. If you want to use a different database or LLM model, make sure to set the appropriate environment
> variables before running the application. Check the next section for the list of environment variables.

---

## ⚙️ Environment Variables

| Variable       | Description                                                              | Example Value                                                                                           |
|----------------|--------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| DATABASE_URL   | PostgreSQL connection string                                             | postgresql://admin:admin@localhost:5432/prolific                                                        |
| OLLAMA_URL     | URL for the Ollama LLM service                                           | http://localhost:11434                                                                                  |
| FRONTEND_URL   | Allowed frontend origin for CORS                                         | http://localhost:3000                                                                                   |
| OPENAI_API_KEY | API key for OpenAI (used for LLM error rephrasing if ChatGPT is enabled) | your_openai_api_key_here -> note that we do not use the ChatGPT Client unless modifying the actual code |                  

---

## 📚 Example Usage

- **Submit participant consent:**
  ```http
  POST /consent
  {
    "participant_id": "abc123",
    "consent": true
  }
  ```
  Response:
  ```http
  {
    "participant_id": "abc123",
    "consent": true
  }
  ```

- **Submit participant experience:**
  ```http
  POST /experience
  {
    "participant_id": "abc123",
    "python_yoe": 3
  }
  ```
  Response:
  ```http
  {
    "participant_id": "abc123"
  }
  ```

- **Get MCQ questions:**
  ```http
  GET /questions?participant_id=abc123
  ```
  Response:
  ```http
  [
    {
      "id": "q1",
      "question": "What does the following code output?",
      "options": ["1", "2", "3", "4"]
    },
    ...
  ]
  ```

- **Submit MCQ answer:**
  ```http
  POST /question
  {
    "participant_id": "abc123",
    "question_id": "q1",
    "answer": "2",
    "time_taken_ms": 5000
  }
  ```
  Response:
  ```http
  {
    "participant_id": "abc123",
    "question_id": "q1"
  }
  ```

- **Submit code for evaluation:**
  ```http
  POST /submit
  {
    "participant_id": "abc123",
    "snippet_id": "0",
    "code": "print('hello')",
    "time_taken_ms": 12000
  }
  ```
  Response:
  ```http
  {
    "participant_id": "abc123",
    "snippet_id": "0",
    "status": "success",
    "error_msg": ""
  }
  ```

- **Get a code snippet:**
  ```http
  GET /snippet/0?participant_id=abc123
  ```
  Response:
  ```http
  {
    "id": "0",
    "code": "def foo(): ...",
    "error": "TypeError: ..."
  }
  ```

---

## 📝 Notes

- Error messages for first attempts are static, while second attempts use LLM-rephrased feedback.
- The backend is naturally designed for integration with a frontend survey application (the implementation for
  that is located in a separate GitHub
  repository: [EXCEED Prolific Frontend](https://github.com/alemoraru/exceed-prolific-frontend)).

---

## 🛠️ Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started) (for containerized deployment only, optional)
- [PostgreSQL](https://www.postgresql.org/download/) (needed for database management - we recommend using Docker for
  this)
    - If using Docker, you can make use of the provided `docker-compose.yml` file to set up a PostgreSQL database:
      ```bash
      docker-compose up -d
      ```
- [Ollama](https://ollama.com/) (for LLM rephrasing of error messages - optional, but required for the second
  attempt at fixing code snippets).
    - Make sure that you have downloaded the model you want to use within the code.

---

## 🤝 Contributing

This project was developed as part of the EXCEED MSc Thesis project at Technische Universiteit Delft. As such,
contributions of any sort will not be accepted. This repository is provided for replication and educational purposes
ONLY. Since it was used to orchestrate the deployment of our study on Prolific, it is NOT intended for further
development or contributions.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

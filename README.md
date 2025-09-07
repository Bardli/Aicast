
# Personalized AI-Powered Audio News Platform

## Introduction
This project outlines and implements a novel platform designed to empower users to become active curators of their own news experience. It provides a platform for creating user-curated, AI-generated audio news digests, offering a unique synthesis of user agency via a drag-and-drop "block" interface, a declarative and extensible content sourcing mechanism, and advanced AI-driven narrative synthesis to transform disparate information into a coherent audio broadcast.

## High-Level Architecture
The platform is built on a modern, scalable, and resilient microservices architecture, allowing for independent development, deployment, and scaling of each functional component. The core services include:

*   **Frontend Web Application:** A single-page application (SPA) for user interaction.
*   **API Gateway:** The unified entry point for all frontend requests.
*   **User & Block Service:** Manages user profiles and content "Block" definitions.
*   **Content Ingestion Service:** Fetches and normalizes news content from various sources.
*   **LLM Orchestration Service:** Manages the workflow for summarizing and synthesizing news into a script using Large Language Models.
*   **Audio Generation Service:** Converts the final text script into high-quality audio using Text-to-Speech services.
*   **Notification Service:** Handles asynchronous notifications to users.

## Key Features
*   **User-Curated Content:** Users define their news digests using a drag-and-drop "Block" interface.
*   **Declarative Blocks:** "Blocks" are self-contained, machine-readable instructions for content retrieval, defined by a strict JSON Schema.
*   **AI-Driven Narrative Synthesis:** Utilizes a "Synthesizer-Weaver" prompting pattern to transform raw articles into coherent, human-like audio scripts.
*   **High-Quality Audio Output:** Integrates with leading Text-to-Speech (TTS) providers to deliver natural-sounding audio.
*   **Scalable and Resilient:** Designed with asynchronous, queue-driven workflows and containerized microservices for robustness.

## Technology Stack
*   **Frontend:** React, dnd-kit
*   **Backend:** Python (FastAPI), PostgreSQL (with JSONB support), SQLAlchemy
*   **Containerization:** Docker
*   **Orchestration:** Kubernetes (future)
*   **Message Queues:** (e.g., RabbitMQ, AWS SQS - to be implemented)
*   **External APIs:** LLM Providers (e.g., OpenAI, Anthropic), TTS Providers (e.g., ElevenLabs, AWS Polly), Authentication Providers (e.g., Auth0)

## Getting Started

Follow these steps to set up and run the backend services of the Personalized AI-Powered Audio News Platform.

### Prerequisites

*   Python 3.9+
*   `pip` (Python package installer)
*   `git` (for cloning the repository)

### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone <repository_url> # Replace with the actual repository URL
cd Code # Navigate to the project root directory
```

### 2. Set Up Virtual Environment

It's highly recommended to use a Python virtual environment to manage dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages for both the main backend and the Content Ingestion Service:

```bash
pip install -r backend/requirements.txt
pip install -r backend/ingestion_service/requirements.txt
```

### 4. Run the Backend Services

You need to run two separate FastAPI applications: the Main Backend API and the Content Ingestion Service.

#### Run Main Backend API

This service will run on `http://127.0.0.1:8000`.

```bash
# Ensure your virtual environment is activated
source .venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000
```

#### Run Content Ingestion Service

Open a **new terminal window**, activate the virtual environment, and run this service. This service will run on `http://127.0.0.1:8001`.

```bash
# Ensure your virtual environment is activated in this new terminal
source .venv/bin/activate
uvicorn backend.ingestion_service.main:app --reload --port 8001
```

### 5. Verify Installation

Once both services are running, you can verify their basic functionality:

*   **Main Backend API:** Open your browser and navigate to `http://127.0.0.1:8000/docs` to see the interactive API documentation.
*   **Content Ingestion Service:** Open your browser and navigate to `http://127.0.0.1:8001/docs` to see its interactive API documentation.

You can also use `curl` to test the root endpoints:

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8001/
```

Expected output for both should be a JSON message indicating the service is running.

## Future Roadmap
The project is designed with a clear roadmap for future development, including a Block Marketplace, implicit personalization engines, social features, multimedia ingestion, and custom voice integration.
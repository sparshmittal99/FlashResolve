# FlashResolveAI

**Enterprise-Grade Asynchronous Fraud Detection Engine**

FlashResolveAI is an enterprise-grade, asynchronous, event-driven fraud detection engine. It intercepts incoming e-commerce transactions in real time, routes them through a secure processing pipeline, and utilizes generative AI to dynamically calculate risk scores and instantly block high-risk fraudulent activity before financial damage occurs.

---

## 🛠️ The Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Angular v19 | Renders a live security dashboard using reactive Signals and RxJS polling for real-time UI updates. |
| **Backend Gateway** | Java Spring Boot | Serves as the high-throughput ingestion REST API and orchestrates database updates. |
| **Message Queue** | Redis | Acts as an asynchronous, event-driven broker to decouple ingestion from heavy processing. |
| **AI Brain** | Python (LangGraph) | Orchestrates complex multi-factor fraud analysis state machines. |
| **LLM Engine** | Google Gemini 2.5 Flash | Computes multi-layered quantitative risk scores and generates context-aware logic explanations. |
| **Database** | PostgreSQL | Serves as the persistent ACID-compliant ledger for all transaction states. |
| **Containerization** | Docker & Docker Compose | Standardizes, isolates, and networks the microservices across environments. |

---

## ⚙️ Core Architecture & Data Flow

The system processes transactions through a multi-stage pipeline designed to ensure low-latency storefront checkout and reliable background evaluation:

1. **Ingestion & Buffer:** The storefront or payment gateway triggers an HTTP POST request to the Spring Boot REST API. Java immediately flags the transaction state as PROCESSING, writes the baseline row to PostgreSQL, and pushes the event payload into a Redis queue.
2. **Asynchronous Processing:** A dockerized Python worker continuously monitors the Redis queue. Upon popping a transaction, it feeds the raw geospatial, merchant, and value parameters into a LangGraph state machine powered by Gemini 2.5 Flash.
3. **AI Evaluation Matrix:** The AI evaluates a weighted risk matrix (e.g., location anomalies, value spikes, merchant risk) to assign a definitive quantitative score (0-100) and status (APPROVED, FLAGGED, or BLOCKED).
4. **Resolution Webhook:** The Python worker fires an HTTP PUT request back to a secure Spring Boot endpoint, updating the transaction's terminal state and injecting the AI's explanation into PostgreSQL.
5. **Reactive UI Update:** The Angular v19 dashboard fetches updates via an active heartbeat subscription, automatically transitioning the visual status badge from a pulsing PROCESSING state to its final resolved color without requiring a manual page refresh.

---

## 🚀 Key Engineering Features

* **Asynchronous Decoupling:** Separating ingestion (Java) from heavy evaluation (Python/LLM) ensures storefront checkouts never freeze or crash during traffic spikes.
* **UX Pending State Design:** Eliminates user confusion by explicitly visualizing a temporary buffer state while background workers execute downstream calculations.
* **Containerized Networking:** Utilizes an isolated virtual bridge (`host.docker.internal`) allowing sandboxed containers to cleanly communicate with host-running microservices.
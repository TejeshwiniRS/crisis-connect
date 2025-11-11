# 🚨 CrisisConnect — AI-Powered Disaster Response Coordination

CrisisConnect is a **serverless AI system** built to connect **disaster incidents** with the **right NGOs and resources** in real time.  
It combines **AI Studio-generated agents**, **Cloud Run services**, and **Firestore** to orchestrate emergency response efficiently.

---

## 🌍 Inspiration

During crises, responders often face information overload and fragmented communication between victims, NGOs, and authorities.  
We wanted to build a **scalable, data-driven coordination layer** that automatically matches urgent needs to the most capable responders — all powered by Google Cloud’s serverless stack.

---

## 💡 What It Does

CrisisConnect ingests live reports (voice, text, or data feeds) and uses two cooperative AI agents:

| Agent | Role |
|-------|------|
| 🎙️ **SpeechTranscriberAgent** | Converts multilingual audio calls from field responders into structured incident reports. |
| 🧭 **ResourcePlannerAgent** | Scans new incidents in Firestore and automatically matches each need (e.g., “medical aid”, “food supply”) to the best-fit NGOs or relief teams. |

A **web dashboard** (built with AI Studio) visualizes ongoing incidents, matched NGOs, and resource flow — enabling responders to make faster, data-backed decisions.

---

## 🏗️ How We Built It

1. **AI Studio (Google AI Studio):**
   - Used to generate initial agent scaffolds (`SpeechTranscriberAgent`, `ResourcePlannerAgent`).
   - Leveraged the *Deploy to Run* feature for direct deployment to Cloud Run.

2. **Agent Development Kit (ADK):**
   - Implemented both agents using `adk.Agent` subclassing.
   - `SpeechTranscriberAgent` uses Gemini API for transcription and summarization.
   - `ResourcePlannerAgent` queries Firestore to match NGOs with needs.

3. **Cloud Run Services:**
   - Each agent is containerized and deployed independently:
     - `speech-transcriber-gpu` (GPU-accelerated transcription)
     - `resourceplanner` (matching + report writer)
     - `dashboard` (frontend for visualization)

4. **Cloud Firestore:**
   - Stores incidents (`incidents`), NGO records (`ngos`), and match results (`matches`).

5. **Cloud Storage + Pub/Sub:**
   - Audio files are uploaded to Cloud Storage and trigger Pub/Sub events for automatic processing.

6. **Cloud Build & Artifact Registry:**
   - CI/CD pipeline for building and pushing Docker images.



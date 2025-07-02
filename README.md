# Calendar Bot

A conversational assistant to check Google Calendar availability and schedule events using natural language.

## Features

- Check free/busy slots in your Google Calendar.
- Book events using natural language (e.g., "Book a meeting tomorrow at 10am for 30 minutes").
- Context-aware chat interface (remembers conversation).
- Microservice architecture: Streamlit frontend, FastAPI backend, and OpenAI-powered agent, each as a separate service.
- All inter-service communication is via HTTP APIs (cloud-ready, scalable).
- Async-only backend and agent for better concurrency and responsiveness.

## Setup

1. **Clone the repo**  
   `git clone https://github.com/ordinarianx/calendar-bot && cd calendar-bot`

2. **Install dependencies**  
   Each service has its own requirements and virtual environment.
   - Backend:  
     ```
     cd backend
     python -m venv venv
     venv\Scripts\activate
     pip install -r requirements.txt
     ```
   - Agent:  
     ```
     cd agent
     python -m venv venv
     venv\Scripts\activate
     pip install -r requirements.txt
     ```
   - Frontend:  
     ```
     cd frontend
     python -m venv venv
     venv\Scripts\activate
     pip install -r requirements.txt
     ```

3. **Google Calendar API**  
   - Create a service account and download the credentials JSON.
   - Place it in `backend/credentials/calendar-bot-sa.json`.
   - Go to Google Calendar (as the owner).
   - Settings → Share with specific people.
   - Share your Google Calendar with the service account email, with "Make changes to events" permission.

4. **Environment variables**  
   - Each service (`backend`, `agent`, `frontend`) has its own `.env` file in its folder.
   - Example for `backend/.env`:
     ```
     GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
     OPENAI_API_KEY=sk-...
     AGENT_URL=...
     ```
   - Example for `agent/.env`:
     ```
     OPENAI_API_KEY=sk-...
     FASTAPI_URL=....
     ```
   - Example for `frontend/.env`:
     ```
     FASTAPI_URL=....
     ```

## Usage

- Open the Streamlit app in your browser.
- Chat with the assistant to check availability or book events.

## Deployment Notes

- Each service can be deployed independently (e.g., on Render) with its own `.env` and requirements.
- For cloud deployment, pass the Google credentials file as a base64-encoded environment variable and decode it on startup (see backend code comments).
- All times are handled in UTC for backend and Google Calendar.
- All inter-service communication is via HTTP, so services can be scaled or replaced independently.

## Troubleshooting

- For issues, check logs in `backend/calendar-bot.log` and `agent/agent.log`.
- Ensure all environment variables are set correctly in each service's `.env` file.
- Make sure the Google service account has access to your calendar.

---
<br>
This application was built to fulfill an assignment requirement and has been successfully completed and deployed.


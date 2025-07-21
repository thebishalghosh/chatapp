# Flask Chat Application

This is a simple chat application built with Flask and PostgreSQL, ready to deploy on Render.

## Features
- User registration and login
- Send and retrieve chat messages
- REST API endpoints

## Setup

1. Clone the repository and navigate to the `chat` directory.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL and create a database (e.g., `chatdb`).
4. Set the `DATABASE_URL` environment variable (Render does this automatically):
   ```
   export DATABASE_URL=postgresql://user:password@localhost:5432/chatdb
   ```
5. Initialize the database:
   ```
   python
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```
6. Run the app locally:
   ```
   flask run
   ```

## Deployment on Render
- Add a PostgreSQL database in Render dashboard and connect it to your web service.
- Make sure `DATABASE_URL` is set in the environment variables.
- Render will use the `Procfile` to start the app.

## API Endpoints
- `POST /auth/register` — Register a new user
- `POST /auth/login` — Login
- `GET /chat/messages` — Get all messages
- `POST /chat/messages` — Send a message 
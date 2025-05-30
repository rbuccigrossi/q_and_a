# Audience Q&A Application

This project is a minimal Flask application that lets an audience submit
questions and vote on them in real time. It persists questions to a JSON
file on disk. The frontend periodically updates to show new questions and
votes and includes a simple "presentation" view for displaying a selected
question.

## Project Structure

```
.
├── app.py             # Flask API and server configuration
├── static/
│   ├── script.js      # Frontend logic (fetching, add, upvote)
│   └── style.css      # Page styling
└── templates/
    └── index.html     # HTML template served by Flask
```

- **`app.py`** exposes three API routes under `/api/` for listing,
  creating and upvoting questions. It uses `flask` and `flask_cors`.
- **`static/`** holds JavaScript and CSS served as static assets.
- **`templates/`** contains the single HTML template loaded by Flask.
- Questions are stored in `questions.json` next to `app.py`.

## Configuration and Deployment

1. **Install dependencies**

   Create a virtual environment and install the packages listed in
   `requirements.txt`:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the development server**

   Start Flask directly from `app.py`:

   ```bash
   python app.py
   ```

  The app will listen on `http://localhost:5000` with debug mode enabled.
  Open `/` for the audience view, `/present/` for the presenter view, or
  `/admin/` for the admin interface.

3. **Deploying**

   For production use, run the app with a WSGI server such as
   [Gunicorn](https://gunicorn.org/). Example:

   ```bash
   gunicorn -w 4 app:app
   ```

   You may also wish to use a reverse proxy (e.g. Nginx) to serve static
   files and handle TLS termination.

   Because data is stored in `questions.json`, ensure the process has
   write access to the project directory, or configure persistent
   storage accordingly. For multi-user deployments consider switching to
   a database such as SQLite or PostgreSQL.

## OAuth2 Configuration

This application supports Google OAuth2 for authentication. To enable it:

1. Create an OAuth2 Client ID in the Google Cloud Console and configure the
   authorized redirect URI to `http://localhost:5000/authorize` (replace the
   host if deploying elsewhere).
2. Copy `.env.example` to `.env` and fill in the following values (or set them
   as environment variables) before running the app:

   - `GOOGLE_CLIENT_ID` – OAuth2 client ID.
   - `GOOGLE_CLIENT_SECRET` – OAuth2 client secret.
   - `ALLOWED_DOMAIN` – Google Workspace domain allowed to sign in.
   - `SECRET_KEY` – secret key used by Flask to secure sessions.

The application loads these variables automatically using
[`python-dotenv`](https://github.com/theskumar/python-dotenv).

Once configured, visiting `/login` will start the sign‑in flow and `/logout`
will clear the session. Access to `/admin/` requires an authenticated user
from the allowed domain.

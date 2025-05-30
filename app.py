from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    send_from_directory,
    redirect,
    url_for,
    session,
)
from flask_cors import CORS  # Import CORS
from authlib.integrations.flask_client import OAuth
from functools import wraps
import config
import os
import json
import uuid
import threading

# --- Configuration ---
DATA_FILE = 'questions.json'
# Use the directory where app.py is located
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILE_PATH = os.path.join(BASE_DIR, DATA_FILE)

# --- Flask App Setup ---
app = Flask(__name__)
# Enable CORS for all routes under /api/
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = config.Config.SECRET_KEY

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=config.Config.GOOGLE_CLIENT_ID,
    client_secret=config.Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url=config.Config.GOOGLE_DISCOVERY_URL,
    client_kwargs={"scope": "openid email profile"},
)

def login_required(func):
    """Decorator to ensure the user is logged in."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper

# --- Data Handling ---
# Thread lock for safe file writes
file_lock = threading.Lock()

def read_questions():
    """Reads questions from the JSON file."""
    with file_lock:
        if not os.path.exists(FILE_PATH):
            return []
        try:
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                # Handle empty file case
                content = f.read()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading {FILE_PATH}: {e}")
            return []

def write_questions(data):
    """Writes questions to the JSON file."""
    with file_lock:
        try:
            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error writing to {FILE_PATH}: {e}")

# --- API Routes ---

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """API endpoint to get all questions, sorted by votes."""
    questions = read_questions()
    # Sort by votes (descending), then by text (ascending) as a tie-breaker
    sorted_questions = sorted(questions, key=lambda x: (-x.get('votes', 0), x.get('text', '')))
    return jsonify(sorted_questions)

@app.route('/api/questions', methods=['POST'])
def add_question():
    """API endpoint to add a new question."""
    if not request.json or 'text' not in request.json or not request.json['text'].strip():
        return jsonify({"error": "Question text cannot be empty"}), 400

    new_question_text = request.json['text'].strip()
    questions = read_questions()

    new_question = {
        'id': str(uuid.uuid4()),
        'text': new_question_text,
        'votes': 0
        # We might add 'upvoters': [] later if we implement user tracking
    }

    questions.append(new_question)
    write_questions(questions)
    return jsonify(new_question), 201

@app.route('/api/questions/<string:question_id>/upvote', methods=['POST'])
def upvote_question(question_id):
    """API endpoint to upvote a question."""
    questions = read_questions()
    question_found = False
    updated_question = None

    for q in questions:
        if q.get('id') == question_id:
            q['votes'] = q.get('votes', 0) + 1
            question_found = True
            updated_question = q
            break

    if not question_found:
        return jsonify({"error": "Question not found"}), 404

    write_questions(questions)
    return jsonify(updated_question)

# --- Serve a Simple Test Page (Optional - for basic testing) ---
@app.route('/')
@login_required
def index():
    """Serves the audience view."""
    return render_template('index.html', presenter=False)

@app.route('/present/')
@login_required
def presenter_view():
    """Serves the presenter view with additional controls."""
    return render_template('index.html', presenter=True)

@app.route('/login')
def login():
    """Starts the Google OAuth flow with a unique nonce."""
    redirect_uri = url_for('authorize', _external=True)
    nonce = uuid.uuid4().hex
    session['nonce'] = nonce  # Store nonce for later validation
    return google.authorize_redirect(
        redirect_uri,
        hd=config.Config.ALLOWED_DOMAIN,
        nonce=nonce,
    )


@app.route('/authorize')
def authorize():
    """Handles the OAuth callback and stores the user session."""
    token = google.authorize_access_token()
    user = google.parse_id_token(token, nonce=session.get('nonce'))
    session.pop('nonce', None)  # Remove nonce after use
    if not user or not user.get('email', '').endswith('@' + config.Config.ALLOWED_DOMAIN):
        return "Unauthorized", 403
    session['user'] = user
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Logs out the current user."""
    session.clear()
    return redirect(url_for('index'))

# --- Admin Routes ---

@app.route('/admin/')
@login_required
def admin_page():
    """Serves a simple admin interface."""
    return render_template('admin.html')


@app.route('/admin/download')
@login_required
def download_questions():
    """Allows downloading the current questions.json file."""
    if not os.path.exists(FILE_PATH):
        write_questions([])
    return send_from_directory(BASE_DIR, DATA_FILE, as_attachment=True)


@app.route('/admin/upload', methods=['POST'])
@login_required
def upload_questions():
    """Replaces questions.json with the uploaded file."""
    uploaded = request.files.get('file')
    if not uploaded or uploaded.filename == '':
        return redirect(url_for('admin_page'))

    try:
        data = json.load(uploaded)
    except json.JSONDecodeError:
        return redirect(url_for('admin_page'))

    # Validate that the uploaded data is a list
    if not isinstance(data, list):
        return redirect(url_for('admin_page'))

    write_questions(data)
    return redirect(url_for('admin_page'))


@app.route('/admin/clear', methods=['POST'])
@login_required
def clear_questions():
    """Empties the questions file."""
    write_questions([])
    return redirect(url_for('admin_page'))

# --- Run the App ---
if __name__ == '__main__':
    # Ensure the data file exists (or is created) on startup
    if not os.path.exists(FILE_PATH):
        write_questions([])
    print(f"Data file will be stored at: {FILE_PATH}")
    # Run in debug mode for development (auto-reloads, provides debugger)
    # Use host='0.0.0.0' to make it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)

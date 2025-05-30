document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = `${window.location.origin}/api`; // Use relative URL to the current server
    const questionList = document.getElementById('question-list');
    const addQuestionForm = document.getElementById('add-question-form');
    const questionText = document.getElementById('question-text');
    const anonymousCheckbox = document.getElementById('anonymous-checkbox');
    const updateButton = document.getElementById('update-button');
    const errorMessage = document.getElementById('error-message');

    const UPDATE_INTERVAL = 15000; // 15 seconds
    let presentationWindow = null;

    // --- Data Fetching ---

    async function fetchQuestions() {
        try {
            const response = await fetch(`${API_BASE_URL}/questions`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const questions = await response.json();
            displayQuestions(questions);
            errorMessage.textContent = ''; // Clear error on successful fetch
        } catch (error) {
            console.error("Failed to fetch questions:", error);
            errorMessage.textContent = "Failed to load questions. Please try updating.";
        }
    }

    // --- Display Logic ---

    function displayQuestions(questions) {
        questionList.innerHTML = ''; // Clear current list

        if (questions.length === 0) {
            questionList.innerHTML = '<p>No questions yet. Be the first!</p>';
            return;
        }

        const upvotedIds = getUpvotedIds();

        questions.forEach(q => {
            const item = document.createElement('div');
            item.className = 'question-item';
            item.dataset.id = q.id;

            const content = document.createElement('div');
            content.className = 'question-content';

            const textEl = document.createElement('div');
            // Show question and author on one line
            textEl.textContent = `${q.text} -- ${q.author}`;

            content.appendChild(textEl);

            const votes = document.createElement('span');
            votes.className = 'question-votes';
            votes.textContent = q.votes;

            const actions = document.createElement('div');
            actions.className = 'question-actions';

            const upvoteBtn = document.createElement('button');
            upvoteBtn.textContent = 'Upvote';
            upvoteBtn.className = 'upvote-btn';
            upvoteBtn.onclick = () => upvoteQuestion(q.id, upvoteBtn);
            // Disable if already upvoted in this session
            if (upvotedIds.includes(q.id)) {
                upvoteBtn.disabled = true;
            }

            actions.appendChild(votes);
            actions.appendChild(upvoteBtn);

            if (window.isPresenter) {
                const presentBtn = document.createElement('button');
                presentBtn.textContent = 'Present';
                presentBtn.className = 'present-btn';

                // Style button based on whether this question was presented before
                if (getPresentedIds().includes(q.id)) {
                    presentBtn.classList.add('presented');
                }

                presentBtn.onclick = () => presentQuestion(q.text, q.author, q.id, presentBtn);
                actions.appendChild(presentBtn);
            }

            item.appendChild(content);
            item.appendChild(actions);

            questionList.appendChild(item);
        });
    }

    // --- Actions ---

    async function handleAddQuestion(event) {
        event.preventDefault(); // Prevent page reload
        const text = questionText.value.trim();
        const anonymous = anonymousCheckbox.checked;

        if (!text) {
            errorMessage.textContent = "Question cannot be empty.";
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/questions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, anonymous: anonymous })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || `HTTP error! status: ${response.status}`);
            }

            questionText.value = ''; // Clear input
            anonymousCheckbox.checked = false;
            errorMessage.textContent = ''; // Clear error
            await fetchQuestions(); // Refresh list immediately

        } catch (error) {
            console.error("Failed to add question:", error);
            errorMessage.textContent = `Failed to add question: ${error.message}`;
        }
    }

    async function upvoteQuestion(id, button) {
        try {
            const response = await fetch(`${API_BASE_URL}/questions/${id}/upvote`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            addUpvotedId(id); // Mark as upvoted for this session
            button.disabled = true; // Disable button immediately
            await fetchQuestions(); // Refresh to show new vote count

        } catch (error) {
            console.error("Failed to upvote question:", error);
            errorMessage.textContent = "Failed to upvote. Please try updating.";
        }
    }

    function presentQuestion(text, author, id, button) {
        const windowName = "QAPresentationWindow";

        // Try to focus existing window, or open a new one
        if (presentationWindow && !presentationWindow.closed) {
            presentationWindow.focus();
        } else {
            presentationWindow = window.open('', windowName, 'width=800,height=600');
        }

        if (presentationWindow) {
            presentationWindow.document.title = 'Presenting Question';
            presentationWindow.document.body.innerHTML = `
                <style>
                    body {
                        background-color: #111; color: #fff;
                        display: flex; justify-content: center; align-items: center;
                        height: 100vh; margin: 0; font-family: sans-serif;
                        overflow: hidden;
                    }
                    .presentation-question {
                        font-size: 6vw; text-align: center; padding: 5%;
                    }
                    .presentation-author {
                        font-size: 2vw; margin-top: 1vh; text-align: right;
                    }
                </style>
                <div class="presentation-question">${escapeHTML(text)}<div class="presentation-author">${escapeHTML(author)}</div></div>
            `;
            addPresentedId(id);
            if (button) {
                button.classList.add('presented');
            }
        } else {
            alert("Please allow pop-ups for this site to use the Present feature.");
        }
    }

    // --- Upvote Tracking (Session-based) ---

    function getUpvotedIds() {
        return JSON.parse(sessionStorage.getItem('upvotedQuestions') || '[]');
    }

    function addUpvotedId(id) {
        const ids = getUpvotedIds();
        if (!ids.includes(id)) {
            ids.push(id);
            sessionStorage.setItem('upvotedQuestions', JSON.stringify(ids));
        }
    }

    // --- Presentation Tracking (Session-based) ---

    function getPresentedIds() {
        return JSON.parse(sessionStorage.getItem('presentedQuestions') || '[]');
    }

    function addPresentedId(id) {
        const ids = getPresentedIds();
        if (!ids.includes(id)) {
            ids.push(id);
            sessionStorage.setItem('presentedQuestions', JSON.stringify(ids));
        }
    }

    // --- Utility ---

    function escapeHTML(str) {
       const div = document.createElement('div');
       div.appendChild(document.createTextNode(str));
       return div.innerHTML;
    }

    // --- Event Listeners & Initialization ---

    addQuestionForm.addEventListener('submit', handleAddQuestion);
    updateButton.addEventListener('click', fetchQuestions);

    // Initial load
    fetchQuestions();

    // Set up automatic updates
    setInterval(fetchQuestions, UPDATE_INTERVAL);
});

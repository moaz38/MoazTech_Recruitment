import io
from datetime import datetime
from bson.objectid import ObjectId
import os # <-- Zaroori hai
import sys # <-- Zaroori hai

# === VIP FIX FOR RENDER (REMOVED: Ab iski zaroorat nahi) ===
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file

# ================================
# VIP FIX: (ModuleNotFoundError Fix)
# Hum 'utils' se import nahi kar rahe, 
# kyunki files ab bahar 'app.py' ke saath hain.
# ================================
from database import users_col, quizzes_col, results_col
from auth import hash_password, verify_password
# ================================
# import config (REMOVED - Ab iski zaroorat nahi)

app = Flask(__name__)

# === VIP DEPLOYMENT FIX ===
# Render.com ke liye Environment Variables istemal karein
# Hum ab 'config.py' ki jagah direct 'os.environ.get()' use kar rahe hain
# (Defaults aapki .env file se li hain, taake local bhi chale)
app.secret_key = os.environ.get('SECRET_KEY', 'moaztech_supersecret_123!@#')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@moaztech.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin123!')
PASSING_PERCENT = int(os.environ.get('PASSING_PERCENT', 70))
MAX_ATTEMPTS = int(os.environ.get('MAX_ATTEMPTS', 3)) #<-- 3 attempts (aapki .env file ke mutabiq)
# === END FIX ===


# ============================
# VIP FIX FOR RECURSION ERROR
# (Injects current_year into all templates automatically)
# ============================
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}
# === END FIX ===


# ============================
# Generate Employee ID
# ============================
def generate_employee_id():
    count = users_col.count_documents({'status': 'approved'})
    # Ensure ID is formatted correctly, e.g., MT-001, MT-002
    return f"MT-{count+1:03d}"

# ============================
# Default Quiz Questions
# (Yeh code waisa hi hai, ismein koi change nahi)
# ============================
DEFAULT_QUIZ = {
    "questions": [
        {
            "question": "Capital of Pakistan?",
            "options": ["Lahore", "Islamabad", "Karachi"],
            "answer": "Islamabad"
        },
        {
            "question": "Python is a ____?",
            "options": ["Snake", "Programming Language", "Car"],
            "answer": "Programming Language"
        },
        {
            "question": "HTML stands for?",
            "options": ["HyperText Markup Language", "Home Tool Markup Language", "None"],
            "answer": "HyperText Markup Language"
        },
        {
            "question": "2 + 2 = ?",
            "options": ["3", "4", "5"],
            "answer": "4"
        },
        {
            "question": "Sun rises from?",
            "options": ["West", "East", "North"],
            "answer": "East"
        }
    ]
}


# ============================
# Home Page
# ============================
@app.route("/")
def index():
    # current_year = datetime.now().year (REMOVED: Now automatic)
    return render_template("home.html") # (REMOVED: current_year)

# ============================
# Signup
# ============================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get('name').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        if users_col.find_one({'email': email}):
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for('login'))

        hashed = hash_password(password)
        users_col.insert_one({
            'name': name,
            'email': email,
            'password': hashed,
            'status': 'pending',
            'attempts': 0,
            'employee_id': None,
            'joined': None,
            'role': 'candidate'
        })
        flash("Signup successful. Login to continue.", "success")
        return redirect(url_for('login'))

    # current_year = datetime.now().year (REMOVED: Now automatic)
    return render_template("signup.html") # (REMOVED: current_year)

# ============================
# Login
# ============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        # Admin login (CHANGED: Uses ENV Variable)
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['user_id'] = "admin"
            flash("Welcome Admin!", "success")
            return redirect(url_for('admin'))

        # Regular user login
        user = users_col.find_one({'email': email})
        if not user or not verify_password(password, user['password']):
            flash("Invalid credentials.", "danger")
            return redirect(url_for('login'))

        session['user_id'] = str(user['_id'])
        if user.get('status') == 'approved':
            flash("Welcome back! You already passed the quiz.", "success")
            return redirect(url_for('dashboard'))

        return redirect(url_for('instructions'))

    # current_year = datetime.now().year (REMOVED: Now automatic)
    return render_template("login.html") # (REMOVED: current_year)

# ============================
# Logout
# ============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

# ============================
# Instructions before quiz
# ============================
@app.route("/instructions")
def instructions():
    uid = session.get('user_id')
    # === ADMIN FIX ===
    if not uid:
        return redirect(url_for('login'))
    if uid == "admin":
        flash("Admin cannot access user pages.", "warning")
        return redirect(url_for('admin'))
    # === END FIX ===

    user = users_col.find_one({'_id': ObjectId(uid)})
    if user.get('status') == 'approved':
        return redirect(url_for('dashboard'))

    # current_year = datetime.now().year (REMOVED: Now automatic)
    return render_template("instructions.html", user=user, passing=PASSING_PERCENT) # (CHANGED & REMOVED: current_year)

# ============================
# Start Quiz
# ============================
@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    uid = session.get('user_id')
    # === ADMIN FIX ===
    if not uid:
        return redirect(url_for('login'))
    if uid == "admin":
        flash("Admin cannot access user pages.", "warning")
        return redirect(url_for('admin'))
    # === END FIX ===

    user = users_col.find_one({'_id': ObjectId(uid)})
    if user.get('status') == 'approved':
        flash("You already passed the quiz.", "success")
        return redirect(url_for('dashboard'))

    # Retrieve the user's latest attempts count from the database
    current_attempts = user.get('attempts', 0)
    
    if current_attempts >= MAX_ATTEMPTS: # (CHANGED)
        flash(f"You have already used your maximum attempt limit ({MAX_ATTEMPTS}).", "warning")
        return redirect(url_for('instructions'))

    # Find the quiz from database
    quiz = quizzes_col.find_one()
    
    if quiz:
        # If quiz found in DB, store its ID
        session['quiz'] = str(quiz['_id'])
    else:
        # If no quiz in DB, use the default quiz dictionary
        session['quiz'] = DEFAULT_QUIZ

    return redirect(url_for('quiz'))

# ============================
# Quiz Page
# ============================
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    uid = session.get('user_id')
    # === ADMIN FIX ===
    if not uid:
        return redirect(url_for('login'))
    if uid == "admin":
        flash("Admin cannot access user pages.", "warning")
        return redirect(url_for('admin'))
    # === END FIX ===

    quiz_session = session.get('quiz')
    user = users_col.find_one({'_id': ObjectId(uid)})

    quiz_doc = None
    if isinstance(quiz_session, dict):
        quiz_doc = quiz_session  # It's the DEFAULT_QUIZ
    elif quiz_session:
        try:
            # Try to fetch quiz from DB using the stored ObjectId string
            quiz_doc = quizzes_col.find_one({'_id': ObjectId(quiz_session)})
        except Exception as e:
            # Handle potential error if ID is invalid
            print(f"Error fetching quiz from DB: {e}")
            pass
            
    # ROBUSTNESS CHECK: If quiz data is missing, redirect the user
    if not quiz_doc or 'questions' not in quiz_doc:
        flash("Error loading quiz questions. Please contact the administrator.", "danger")
        session.pop('quiz', None) 
        return redirect(url_for('instructions'))
    
    # *** CRITICAL FIX: Explicitly assign index for robust Jinja2 template rendering ***
    # This is the key fix for radio button grouping in HTML.
    for i, q in enumerate(quiz_doc['questions']):
        q['index'] = i
    # *********************************************************************************

    if request.method == "POST":
        answers = []
        # Loop through the questions in the fetched quiz document
        for i, q in enumerate(quiz_doc['questions']):
            # Get answer using form field name 'q0', 'q1', 'q2', etc. (matching the HTML's q.index)
            ans = request.form.get(f"q{i}")
            answers.append(ans)

        score = sum(1 for i, q in enumerate(quiz_doc['questions']) if answers[i] == q['answer'])
        total = len(quiz_doc['questions'])
        percent = (score / total) * 100

        # 1. Increment attempt count in DB
        users_col.update_one({'_id': ObjectId(uid)}, {'$inc': {'attempts': 1}})

        # 2. === REATTEMPT LOGIC FIX === 
        # Update hone k baad wapis user ko fetch kro taake latest count mile
        updated_user = users_col.find_one({'_id': ObjectId(uid)})
        attempts_count = updated_user.get('attempts', 0)
        # ==============================

        status = 'failed'
        employee_id = None

        if percent >= PASSING_PERCENT: # (CHANGED)
            status = 'approved'
            employee_id = generate_employee_id()
            users_col.update_one({'_id': ObjectId(uid)}, {
                '$set': {
                    'status': 'approved',
                    'employee_id': employee_id,
                    'joined': datetime.utcnow()
                }
            })
            # Update local user object for display in result page
            user['status'] = 'approved'
            user['employee_id'] = employee_id
            user['joined'] = datetime.utcnow()
        else:
            # Only update status to 'failed' if not approved
            users_col.update_one({'_id': ObjectId(uid)}, {'$set': {'status': 'failed'}})

        # Insert result record
        results_col.insert_one({
            'user_id': ObjectId(uid),
            'score': score,
            'total': total,
            'percent': percent,
            'status': status,
            'date': datetime.utcnow()
        })
        
        # Clear quiz session after submission
        session.pop('quiz', None) 

        # 3. Pass 'attempts_count' to the template
        return render_template(
            "quiz_result.html",
            score=score,
            total=total,
            percent=percent,
            status=status,
            employee_id=employee_id,
            user=user,
            passing=PASSING_PERCENT,
            attempts_count=attempts_count # <--- YEH LINE ADD KI HAI
        )

    # GET Request: Render the quiz form
    # current_year = datetime.now().year (REMOVED: Now automatic)
    return render_template("quiz_question.html", quiz=quiz_doc, user=user) # (REMOVED: current_year)

# ============================
# Dashboard
# ============================
@app.route("/dashboard")
def dashboard():
    uid = session.get('user_id')
    # === ADMIN FIX ===
    if not uid:
        return redirect(url_for('login'))
    if uid == "admin":
        # Admin ko admin dashboard par hi rakhein
        return redirect(url_for('admin'))
    # === END FIX ===

    user = users_col.find_one({'_id': ObjectId(uid)})
    if user is None:
        session.clear()
        flash("User not found.", "danger")
        return redirect(url_for('login'))
        
    # User who is not approved goes back to instructions
    if user.get('status') != 'approved':
        return redirect(url_for('instructions'))

    res = list(results_col.find({'user_id': ObjectId(uid)}))
    
    # current_year = datetime.now().year (REMOVED: Now automatic)
    
    return render_template("employee_dashboard.html", user=user, results=res) # (REMOVED: current_year)

# ============================
# Admin Dashboard
# ============================
@app.route("/admin")
def admin():
    uid = session.get('user_id')
    # Use Admin credentials from config for robust check, not just "admin" string
    if uid != "admin": 
        flash("Access denied. Admin only.", "danger")
        return redirect(url_for('login'))

    users = list(users_col.find())
    quizzes = list(quizzes_col.find())
    results = list(results_col.find())
    # current_year = datetime.now().year (REMOVED: Now automatic)
    return render_template("admin_dashboard.html", users=users, quizzes=quizzes, results=results) # (REMOVED: current_year)

# ============================
# Download Employee ID (REMOVED)
# ============================
# (Old @app.route("/download_id") function removed)

# ============================
# NEW: View Employee ID Card
# ============================
@app.route("/view_id")
def view_id():
    uid = session.get('user_id')
    # === ADMIN FIX ===
    if not uid:
        return redirect(url_for('login'))
    if uid == "admin":
        flash("Admin cannot access user pages.", "warning")
        return redirect(url_for('admin'))
    # === END FIX ===

    user = users_col.find_one({'_id': ObjectId(uid)})
    if user.get('status') != 'approved':
        flash("No ID Card available.", "danger")
        return redirect(url_for('dashboard'))
    
    # current_year = datetime.now().year (REMOVED: Now automatic)
    # Render the new ID card template
    return render_template("id_card.html", user=user) # (REMOVED: current_year)


if __name__ == "__main__":
    app.run(debug=True)
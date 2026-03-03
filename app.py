from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from authlib.integrations.flask_client import OAuth
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import sqlite3
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask import send_from_directory, abort
from email_utils import init_mail, send_contact_email
from populate_db import populate_scholarships

load_dotenv()

app = Flask(__name__)

# SECRET KEY CONFIGURATION
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


# Initialize Mail
init_mail(app)

# OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')

oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(app.instance_path, 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database configuration
DATABASE = os.path.join(app.instance_path, 'scholarhub.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            phone TEXT,
            education_level TEXT,
            institution TEXT,
            major TEXT,
            bio TEXT
        )
    ''')
    

    
    # Scholarships table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount TEXT NOT NULL,
            deadline TEXT NOT NULL,
            eligibility TEXT NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL,
            level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scholarship_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            phone TEXT NOT NULL,
            gpa REAL NOT NULL,
            major TEXT,
            year TEXT,
            goal TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (scholarship_id) REFERENCES scholarships (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_type TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    ''')
    
    # Admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Super Admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


    
    # Saved Scholarships table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            scholarship_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (scholarship_id) REFERENCES scholarships (id),
            UNIQUE(user_id, scholarship_id)
        )
    ''')
    
    # Check if admin exists in admins table
    cursor.execute("SELECT * FROM admins WHERE email = ?", ('admin@scholarhub.com',))
    existing_admin_in_admins = cursor.fetchone()
    
    # If admin doesn't exist, create default
    if not existing_admin_in_admins:
        admin_password = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO admins (name, email, password) VALUES (?, ?, ?)",
            ('Admin', 'admin@scholarhub.com', admin_password)
        )
        print("Created default admin account.")

    # COMMIT tables and admin before calling external population script
    # This prevents "database is locked" errors
    conn.commit()
    
    # Check if scholarships exist, if not add sample data
    cursor.execute("SELECT COUNT(*) FROM scholarships")
    if cursor.fetchone()[0] == 0:
        print("Populating initial scholarships using populate_db.py...")
        # Note: populate_scholarships handles its own connection and commit
        populate_scholarships(DATABASE)
    
    conn.close()

# Initialize database on startup
with app.app_context():
    init_db()


@app.route('/')
def index():
    conn = get_db()
    
    # Get 3 latest scholarships
    recent_scholarships = conn.execute('SELECT * FROM scholarships ORDER BY created_at DESC LIMIT 3').fetchall()
    
    # Convert Rows to dicts to handle fields properly
    recent_scholarships_dicts = []
    for s in recent_scholarships:
        d = dict(s)
        if 'type' not in d or not d['type']: 
            d['type'] = 'Merit-Based'
        recent_scholarships_dicts.append(d)
        
    conn.close()
    
    return render_template('index.html', recent_scholarships=recent_scholarships_dicts)

@app.route('/scholarships')
def scholarships_page():
    return render_template('scholarships.html')

@app.route('/scholarship/<int:scholarship_id>')
def scholarship_detail(scholarship_id):
    conn = get_db()
    scholarship = conn.execute('SELECT * FROM scholarships WHERE id = ?', (scholarship_id,)).fetchone()
    
    is_saved = False
    if 'user_id' in session and not session.get('is_admin'):
        saved = conn.execute('SELECT 1 FROM saved_scholarships WHERE user_id = ? AND scholarship_id = ?', 
                           (session['user_id'], scholarship_id)).fetchone()
        is_saved = True if saved else False
        
    conn.close()
    if scholarship:
        # Convert Row to dict to ensure we can modify/access safely
        scholarship_dict = dict(scholarship)
        
        # Ensure new fields exist even if migration failed or data is old
        if 'type' not in scholarship_dict or not scholarship_dict['type']:
            scholarship_dict['type'] = 'Merit-Based'
        if 'level' not in scholarship_dict or not scholarship_dict['level']:
            scholarship_dict['level'] = 'All Levels'
            
        return render_template('scholarship_detail.html', scholarship=scholarship_dict, scholarship_id=scholarship_dict['id'], is_saved=is_saved)
    return redirect(url_for('scholarships_page'))

@app.route('/api/save/<int:scholarship_id>', methods=['POST'])
def toggle_save_scholarship(scholarship_id):
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Please login to save scholarships'}), 401
    
    if session.get('is_admin'):
        return jsonify({'status': 'error', 'message': 'Admins cannot save scholarships'}), 403
    
    conn = get_db()
    user_id = session['user_id']
    
    # Check if already saved
    existing = conn.execute('SELECT * FROM saved_scholarships WHERE user_id = ? AND scholarship_id = ?', 
                          (user_id, scholarship_id)).fetchone()
    
    if existing:
        conn.execute('DELETE FROM saved_scholarships WHERE user_id = ? AND scholarship_id = ?', 
                   (user_id, scholarship_id))
        status = 'removed'
        message = 'Scholarship removed from saved list'
    else:
        conn.execute('INSERT INTO saved_scholarships (user_id, scholarship_id) VALUES (?, ?)', 
                   (user_id, scholarship_id))
        status = 'saved'
        message = 'Scholarship saved successfully'
        
    conn.commit()
    conn.close()
    
    return jsonify({'status': status, 'message': message})

@app.route('/api/check_saved/<int:scholarship_id>')
def check_saved(scholarship_id):
    if 'user_id' not in session or session.get('is_admin'):
        return jsonify({'is_saved': False})
        
    conn = get_db()
    saved = conn.execute('SELECT 1 FROM saved_scholarships WHERE user_id = ? AND scholarship_id = ?', 
                       (session['user_id'], scholarship_id)).fetchone()
    conn.close()
    
    return jsonify({'is_saved': True if saved else False})

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect already logged-in users
    if 'user' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        # Check users table
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        # Check admins table (prevent user registering with admin email)
        existing_admin = conn.execute('SELECT * FROM admins WHERE email = ?', (email,)).fetchone()
        
        if existing_user or existing_admin:
            flash('Email already registered!', 'danger')
            conn.close()
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        conn.execute(
            'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
            (name, email, hashed_password)
        )
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect already logged-in users
    if 'user' in session:
        return redirect(url_for('dashboard') if not session.get('is_admin') else url_for('admin_dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db()
        
        # Check Admins table first
        admin = conn.execute('SELECT * FROM admins WHERE email = ?', (email,)).fetchone()
        
        if admin and check_password_hash(admin['password'], password):
            session['user_id'] = admin['id']
            session['user'] = admin['email']
            session['name'] = admin['name']
            session['is_admin'] = True
            conn.close()
            flash('Welcome Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        # Check Users table
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user'] = user['email']
            session['name'] = user['name']
            session['is_admin'] = False # Explicitly set false for users
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    
    # If userinfo is not in token (depends on provider), fetch it
    if not user_info:
        user_info = oauth.google.userinfo()
        
    email = user_info.get('email')
    name = user_info.get('name')
    
    if not email:
        flash('Could not fetch email from Google.', 'danger')
        return redirect(url_for('login'))
        
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if not user:
        # Create user
        password = secrets.token_urlsafe(16)
        hashed_password = generate_password_hash(password)
        
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
        conn.commit()
        
        # Fetch the new user
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        flash('Account created successfully via Google!', 'success')
        
    conn.close()
    
    # Login
    session['user_id'] = user['id']
    session['user'] = user['email']
    session['name'] = user['name']
    session['is_admin'] = user['is_admin']
    
    flash('Login successful!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        flash('Please login to view your profile.', 'warning')
        return redirect(url_for('login'))
        
    conn = get_db()
    
    if request.method == 'POST':
        # Handle Password Change
        if 'current_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Fetch current password hash
            if session.get('is_admin'):
                user_data = conn.execute('SELECT password FROM admins WHERE id = ?', (session['user_id'],)).fetchone()
                table = 'admins'
            else:
                user_data = conn.execute('SELECT password FROM users WHERE id = ?', (session['user_id'],)).fetchone()
                table = 'users'

            if not check_password_hash(user_data['password'], current_password):
                flash('Incorrect current password.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            else:
                hashed_new_password = generate_password_hash(new_password)
                conn.execute(f"UPDATE {table} SET password = ? WHERE id = ?", (hashed_new_password, session['user_id']))
                conn.commit()
                flash('Password updated successfully!', 'success')
            
            conn.close()
            return redirect(url_for('profile'))

        # Handle Profile Update (for students)
        if not session.get('is_admin'):
            # Name is read-only and not sent in form, so we don't update it
            phone = request.form.get('phone')
            education_level = request.form.get('education_level')
            institution = request.form.get('institution')
            major = request.form.get('major')
            bio = request.form.get('bio')
            
            conn.execute('''
                UPDATE users 
                SET phone = ?, education_level = ?, institution = ?, major = ?, bio = ?
                WHERE id = ?
            ''', (phone, education_level, institution, major, bio, session['user_id']))
            conn.commit()
            
            # session['name'] remains unchanged as we didn't update it
            flash('Profile updated successfully!', 'success')
            
            conn.close()
            return redirect(url_for('profile'))
    
    # Fetch user data
    if session.get('is_admin'):
        user = conn.execute('SELECT * FROM admins WHERE id = ?', (session['user_id'],)).fetchone()
    else:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
    conn.close()
    return render_template('profile.html', user=user, is_admin=session.get('is_admin', False))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or session.get('is_admin', False):
        return redirect(url_for('login'))
        
    conn = get_db()
    applications = conn.execute('''
        SELECT a.*, s.title as scholarship_title, s.amount,
               (SELECT COUNT(*) FROM documents d WHERE d.application_id = a.id) as doc_count
        FROM applications a 
        LEFT JOIN scholarships s ON a.scholarship_id = s.id 
        WHERE a.user_id = ?
        ORDER BY a.applied_date DESC
    ''', (session['user_id'],)).fetchall()
    
    # Fetch Saved Scholarships using LEFT JOIN to get scholarship details
    saved_scholarships = conn.execute('''
        SELECT s.*, ss.created_at as saved_at
        FROM saved_scholarships ss
        JOIN scholarships s ON ss.scholarship_id = s.id
        WHERE ss.user_id = ?
        ORDER BY ss.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    # Calculate deadline proximity for alerts
    deadline_alerts = []
    today = datetime.now().date()
    
    for scholarship in saved_scholarships:
        try:
            deadline_date = datetime.strptime(scholarship['deadline'], '%Y-%m-%d').date()
            days_left = (deadline_date - today).days
            
            if 0 <= days_left <= 7:
                deadline_alerts.append({
                    'title': scholarship['title'],
                    'days_left': days_left,
                    'id': scholarship['id']
                })
        except ValueError:
            pass # Skip invalid dates
            
    return render_template('dashboard.html', applications=applications, saved_scholarships=saved_scholarships, deadline_alerts=deadline_alerts)

@app.route('/apply/<int:scholarship_id>', methods=['GET', 'POST'])
def apply(scholarship_id):
    if 'user' not in session:
        flash('Please login to apply.', 'warning')
        return redirect(url_for('login'))
    
    if session.get('is_admin', False):
        flash('Admins cannot apply for scholarships.', 'warning')
        return redirect(url_for('scholarship_detail', scholarship_id=scholarship_id))

    conn = get_db()
    
    # Check if already applied
    existing_app = conn.execute(
        'SELECT * FROM applications WHERE user_id = ? AND scholarship_id = ?', 
        (session['user_id'], scholarship_id)
    ).fetchone()
    
    if existing_app:
        flash('You have already applied for this scholarship.', 'info')
        conn.close()
        return redirect(url_for('dashboard'))
    
    scholarship = conn.execute('SELECT * FROM scholarships WHERE id = ?', (scholarship_id,)).fetchone()
    
    # Fetch user details for auto-fill
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if request.method == 'POST':
        phone = request.form.get('phone')
        gpa = request.form.get('gpa')
        major = request.form.get('major') or user['major'] # Use form val or fallback to user profile
        education_level = request.form.get('year') # The form field name is 'year', maps to education_level logic
        goal = request.form.get('goal') # Bio/Statement
        
        # Update user profile with latest info if provided
        cursor = conn.cursor()
        if phone and phone != user['phone']:
             cursor.execute("UPDATE users SET phone = ? WHERE id = ?", (phone, session['user_id']))
        if major and major != user['major']:
             cursor.execute("UPDATE users SET major = ? WHERE id = ?", (major, session['user_id']))
        if education_level and education_level != user['education_level']:
             cursor.execute("UPDATE users SET education_level = ? WHERE id = ?", (education_level, session['user_id']))
        
        cursor = conn.execute('''
            INSERT INTO applications (scholarship_id, user_id, phone, gpa, major, year, goal)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (scholarship_id, session['user_id'], phone, gpa, major, education_level, goal))
        
        application_id = cursor.lastrowid
        uploaded_count = 0

        # specific check for documents
        if 'documents' not in request.files:
            flash('No document part', 'danger')
            return redirect(request.url)
            
        files = request.files.getlist('documents')
        
        # Check if user actually selected a file
        if not files or files[0].filename == '':
            flash('At least one supporting document is required.', 'danger')
            return redirect(request.url)


        for file in files:
            if file and allowed_file(file.filename):
                original_filename = secure_filename(file.filename)
                # Generate unique filename to prevent overwrites
                filename = f"{application_id}_{int(datetime.now().timestamp())}_{original_filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                conn.execute('''
                    INSERT INTO documents (application_id, filename, original_name, file_type)
                    VALUES (?, ?, ?, ?)
                ''', (application_id, filename, original_filename, file.content_type))
                uploaded_count += 1
        
        conn.commit()
        conn.close()
        
        msg = 'Application submitted successfully!'
        if uploaded_count > 0:
            msg += f' ({uploaded_count} document{"s" if uploaded_count > 1 else ""} uploaded)'
            
        flash(msg, 'success')
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('apply.html', scholarship=scholarship, user=user)

@app.route('/admin')
def admin_dashboard():
    if 'user' not in session or not session.get('is_admin', False):
        flash('Admin access required!', 'danger')
        return redirect(url_for('login'))
    
    conn = get_db()
    
    # Get statistics
    total_apps = conn.execute('SELECT COUNT(*) FROM applications').fetchone()[0]
    pending_apps = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Pending'").fetchone()[0]
    accepted_apps = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Accepted'").fetchone()[0]
    rejected_apps = conn.execute("SELECT COUNT(*) FROM applications WHERE status = 'Rejected'").fetchone()[0]
    total_users = conn.execute('SELECT COUNT(*) FROM users WHERE is_admin = 0').fetchone()[0]
    total_scholarships = conn.execute('SELECT COUNT(*) FROM scholarships').fetchone()[0]
    
    # Get all applications with user and scholarship details
    applications = conn.execute('''
        SELECT a.*, u.name as user_name, u.email as user_email, 
               s.title as scholarship_title, s.amount
        FROM applications a
        LEFT JOIN users u ON a.user_id = u.id
        LEFT JOIN scholarships s ON a.scholarship_id = s.id
        ORDER BY a.applied_date DESC
    ''').fetchall()
    
    conn.close()
    
    stats = {
        'total_apps': total_apps,
        'pending_apps': pending_apps,
        'accepted_apps': accepted_apps,
        'rejected_apps': rejected_apps,
        'total_users': total_users,
        'total_scholarships': total_scholarships
    }
    
    return render_template('admin_dashboard.html', applications=applications, stats=stats)

@app.route('/admin/update_status/<int:app_id>/<status>')
def update_status(app_id, status):
    if 'user' not in session or not session.get('is_admin'):
        flash('Admin access required!', 'danger')
        return redirect(url_for('login'))
    
    if status not in ['Pending', 'Accepted', 'Rejected']:
        flash('Invalid status!', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db()
    conn.execute('UPDATE applications SET status = ? WHERE id = ?', (status, app_id))
    
    # Fetch application details to send email
    application = conn.execute('''
        SELECT a.*, s.title as scholarship_title, u.email as applicant_email, u.name as applicant_name
        FROM applications a 
        LEFT JOIN scholarships s ON a.scholarship_id = s.id 
        JOIN users u ON a.user_id = u.id
        WHERE a.id = ?
    ''', (app_id,)).fetchone()
    
    conn.commit()
    conn.close()
    
    flash(f'Application marked as {status}.', 'success')
    return redirect(url_for('view_application', app_id=app_id))

@app.route('/admin/scholarships')
def admin_scholarships():
    if 'user' not in session or not session.get('is_admin'):
        flash('Admin access required!', 'danger')
        return redirect(url_for('login'))
    
    conn = get_db()
    scholarships = conn.execute('SELECT * FROM scholarships ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return render_template('admin_scholarships.html', scholarships=scholarships)

@app.route('/admin/scholarship/add', methods=['GET', 'POST'])
def add_scholarship():
    if 'user' not in session or not session.get('is_admin'):
        flash('Admin access required!', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        conn = get_db()
        conn.execute('''
            INSERT INTO scholarships (title, amount, deadline, eligibility, description, type, level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form.get('title'),
            request.form.get('amount'),
            request.form.get('deadline'),
            request.form.get('eligibility'),
            request.form.get('description'),
            request.form.get('type'),
            request.form.get('level')
        ))
        conn.commit()
        conn.close()
        
        flash('Scholarship added successfully!', 'success')
        return redirect(url_for('admin_scholarships'))
    
    return render_template('add_scholarship.html')

@app.route('/admin/scholarship/delete/<int:scholarship_id>')
def delete_scholarship(scholarship_id):
    if 'user' not in session or not session.get('is_admin'):
        flash('Admin access required!', 'danger')
        return redirect(url_for('login'))
    
    conn = get_db()
    
    # Check if there are applications for this scholarship
    app_count = conn.execute('SELECT COUNT(*) FROM applications WHERE scholarship_id = ?', (scholarship_id,)).fetchone()[0]
    
    if app_count > 0:
        conn.close()
        flash(f'Cannot delete scholarship. There are {app_count} active applications associated with it.', 'danger')
        return redirect(url_for('admin_scholarships'))
        
    conn.execute('DELETE FROM scholarships WHERE id = ?', (scholarship_id,))
    conn.commit()
    conn.close()
    
    flash('Scholarship deleted successfully!', 'success')
    return redirect(url_for('admin_scholarships'))

@app.route('/about')
def about():
    now = datetime.now()
    return render_template('about.html', now=now)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    now = datetime.now()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        try:
            # Send email
            if send_contact_email(name, email, subject, message):
                flash('Your message has been sent successfully! We will get back to you soon.', 'success')
            else:
                flash('There was an error sending your message. Please try again later.', 'danger')
                
        except Exception as e:
            print(f"Error processing contact form: {e}")
            flash('Something went wrong. Please try again.', 'danger')
            
        return redirect(url_for('contact'))
        
    return render_template('contact.html', now=now)

@app.route('/application/<int:app_id>')
def view_application(app_id):
    if 'user' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))
    
    conn = get_db()
    
    # query to get application with scholarship details
    query = '''
        SELECT a.*, s.title as scholarship_title, s.amount, s.deadline, 
               u.name as user_name, u.email as user_email
        FROM applications a
        LEFT JOIN scholarships s ON a.scholarship_id = s.id
        JOIN users u ON a.user_id = u.id
        WHERE a.id = ?
    '''
    application = conn.execute(query, (app_id,)).fetchone()
    
    # Fetch documents
    documents = conn.execute('SELECT * FROM documents WHERE application_id = ?', (app_id,)).fetchall()
    
    conn.close()
    
    if not application:
        flash('Application not found!', 'danger')
        return redirect(url_for('dashboard'))
        
    # Permission check: User must own the app OR be admin
    is_admin = session.get('is_admin')
    if application['user_id'] != session['user_id'] and not is_admin:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))
        
    return render_template('application_detail.html', app=application, documents=documents)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if 'user_id' not in session:
        abort(403)
        
    # Check permissions (must query DB to find who owns this file)
    conn = get_db()
    
    # Find which application this file belongs to
    doc = conn.execute('SELECT application_id FROM documents WHERE filename = ?', (filename,)).fetchone()
    
    if not doc:
        conn.close()
        abort(404)
        
    app_id = doc['application_id']
    application = conn.execute('SELECT user_id FROM applications WHERE id = ?', (app_id,)).fetchone()
    conn.close()
    
    is_admin = session.get('is_admin', False)
    
    # Allow if Admin OR if the current user is the owner of the application
    if is_admin or (application and application['user_id'] == session['user_id']):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        abort(403)

@app.route('/api/scholarships')
def get_scholarships_api():
    conn = get_db()
    scholarships = conn.execute('SELECT * FROM scholarships ORDER BY deadline').fetchall()
    conn.close()
    
    return jsonify([dict(s) for s in scholarships])

@app.route('/api/scholarships/<int:scholarship_id>')
def get_scholarship_detail_api(scholarship_id):
    conn = get_db()
    scholarship = conn.execute('SELECT * FROM scholarships WHERE id = ?', (scholarship_id,)).fetchone()
    conn.close()
    
    if scholarship:
        return jsonify(dict(scholarship))
    return jsonify({'error': 'Scholarship not found'}), 404

@app.route('/admin/fetch-external')
def fetch_external_scholarships():
    if 'user' not in session or not session.get('is_admin'):
        flash('Admin access required!', 'danger')
        return redirect(url_for('login'))
        
    conn = get_db()
    cursor = conn.cursor()
    
    # Simulate fetching from an external API
    # In a real app, this would be: response = requests.get('https://api.example.com/scholarships')
    
    
    # Generate some random "new" scholarships
    providers = ["TechFoundation", "GlobalEdu", "FutureScholars", "InnovateGrant", "EduSupport"]
    fields = ["Artificial Intelligence", "Green Energy", "Medical Research", "Digital Arts", "Social Justice"]
    
    new_items_count = 0
    
    for _ in range(5): # Fetch 5 new ones at a time
        provider = random.choice(providers)
        field = random.choice(fields)
        title = f"{provider} {field} Fellowship {random.randint(2026, 2027)}"
        
        # Check duplicates
        exists = cursor.execute("SELECT id FROM scholarships WHERE title = ?", (title,)).fetchone()
        if not exists:
            base_amounts = [5000, 10000, 12000, 20000, 25000, 30000, 50000]
            amount_val = random.choice(base_amounts)
            amount = f"₹{amount_val:,}/year"
            days = random.randint(14, 90)
            deadline = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO scholarships (title, amount, deadline, eligibility, description, type, level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                title,
                amount,
                deadline,
                "Open to all eligible applicants.",
                f"A generic scholarship provided by {provider} to support students in {field}.",
                random.choice(["Merit-Based", "Need-Based", "Research","Athletic"]),
                random.choice(["High School","Undergraduate", "Graduate", "All Levels","PhD"])
            ))
            new_items_count += 1
            
    conn.commit()
    conn.close()
    
    if new_items_count > 0:
        flash(f'Successfully fetched {new_items_count} new scholarships from external sources!', 'success')
    else:
        flash('No new scholarships found from external sources at this time.', 'info')
        
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
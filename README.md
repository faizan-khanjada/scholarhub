# 🎓 ScholarHub - Where Education Meets Opportunity
ScholarHub is a web-based scholarship management system that helps students discover and apply for relevant scholarships while enabling administrators to manage applications efficiently.

---

## 🚀 Key Features

### For Students 👨‍🎓
- **Personalized Dashboard**: Track application statuses, deadlines, and saved scholarships in one place.
- **Smart Scholarship Discovery**: Filter through a diverse range of scholarships (Merit-based, Financial Aid, All Levels).
- **One-Click "Save for Later"**: Bookmark scholarships you're interested in and get deadline alerts.
- **Secure Document Vault**: Upload and manage supporting documents (PDFs, Transcripts, Statements) with ease.
- **Google Authentication**: Seamless and secure sign-in with your Google account.

### For Administrators 👩‍💼
- **Comprehensive Admin Dashboard**: Monitor platform statistics at a glance (Total users, applications).
- **Application Management**: Review, accept, or reject applications with a streamlined workflow.
- **Dynamic Scholarship Control**: Easily add, edit, or remove scholarship listings.
- **Auto-Email Notifications**: Automated communication with applicants regarding their queries.

### 🌟 Platform-Wide
- 🌙 **Dark / Light mode** toggle with full theme persistence
- 🔐 **Google OAuth** login alongside standard email/password auth
- 🎞️ **AOS scroll animations** and smooth UI interactions
- 🔢 **Animated stat counters** on the landing page
- 📬 **Contact form** with email confirmation via Flask-Mail
- 📱 **Fully responsive** design for all screen sizes

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.8+, Flask 3.0.0 |
| **Frontend** | HTML5, Jinja2, Tailwind CSS (CDN), JavaScript |
| **Database** | SQLite via `sqlite3` |
| **Auth** | Werkzeug password hashing, Authlib (Google OAuth) |
| **Email** | Flask-Mail (SMTP / Mailtrap) |
| **Animations** | AOS.js, custom CSS keyframe animations |
| **Icons** | Font Awesome 6 |
| **Config** | python-dotenv |

---

## 🏁 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/faizan-khanjada/scholarhub.git
   cd scholarhub
   ```

2. **Set up a Virtual Environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory and add your credentials (refer to `.env.example`):
  ```env
    #SECRET KEY CONFIGURATION
    SECRET_KEY=your_secret_key_here

    # Google OAuth (get from https://console.cloud.google.com)
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret

    # Flask-Mail (example using Mailtrap for dev)
    MAIL_SERVER=your_smtp_server_here
    MAIL_PORT=your_smtp_port_here
    MAIL_USERNAME=your_email_here
    MAIL_PASSWORD=your_email_password_here
    MAIL_USE_TLS=True_or_False
    MAIL_USE_SSL=True_or_False
    MAIL_DEFAULT_SENDER=Your App Name <your_email_here>
```

5. **Initialize the Database**
   The application will automatically initialize the database on the first run, but you can also run:
   ```bash
   python populate_db.py
   ```
   This adds 20 pre-built scholarship entries to get you started.

6. **Run the Application**
   ```bash
   python app.py
   ```
   Access the app at `http://127.0.0.1:5000`

---

## 🔑 Default Admin Credentials

A default admin account is created automatically on first run:

| Field | Value |
|-------|-------|
| Email | `admin@scholarhub.com` |
| Password | `admin123` |

> ⚠️ **Change the default admin password immediately in production.**

---

## 📂 Project Structure

```text
scholarhub/
├── instance/            # Database and uploaded documents
├── static/              # CSS, Images, and Javascript
├── templates/           # Jinja2 HTML templates
├── app.py               # Main application entry point
├── email_utils.py       # Helper functions for email delivery
├── populate_db.py       # Script to seed initial data
├── reset_db.py          # Script to reset the database
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── .env.example         # Example environment variables  
├── .gitignore           # Git ignore file
└── README.md            
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


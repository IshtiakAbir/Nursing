# 🏥 Premier Medical And Technical Institute - Django Web Platform

A comprehensive, server-rendered web platform for nursing education built with Django following the "Batteries Included" philosophy. This platform provides a complete learning management system with courses, modules, exams, resources, and certificates.

## ✨ Features

### 🔐 Authentication & Security
- Django's built-in User authentication system
- Student profile management with One-to-One relationship
- Login required decorators for all student-facing views
- Secure password handling
- Session management

### 📚 Course Management
- **Courses**: Organized course structure with codes and descriptions
- **Modules**: Ordered learning modules with content and video support
- **Module Completion Tracking**: Students can mark modules as complete
- **Batch System**: Students restricted to their batch's courses and content

### 📄 Resource Library
- PDF and document management
- **Access Control**: Only enrolled students can download resources
- File type categorization (PDF, DOC, PPT, etc.)
- File size tracking

### 📝 Examination System
- **MCQ-based Exams**: Multiple choice question support
- **Auto-Grading**: Instant score calculation upon submission
- **Timer**: Countdown timer for exam duration
- **Detailed Results**: Question-by-question review with explanations
- **Attempt History**: Track all exam attempts
- **Passing Criteria**: Configurable passing scores

### 🏆 Certificate Generation
- **PDF Certificates**: Auto-generated using ReportLab
- **Eligibility Check**: Requires module completion + final exam pass
- **Unique Certificate Numbers**: Auto-generated certificate IDs
- **Download & Print**: Professional certificate design

### 📢 Announcements
- **Batch-specific**: Announcements targeted to specific batches
- **Global Announcements**: Platform-wide notifications
- **Bengali Support**: Full support for Bengali text

### 🎯 Bengali Bulletin
- **Scrolling Bulletin Bar**: CSS @keyframes animation (no marquee tag)
- **Admin Managed**: Toggle on/off from admin panel
- **Right-to-Left Scroll**: Continuous smooth animation

### 👨‍💼 Admin Panel
- **Comprehensive Admin Interface**: Manage all aspects without code
- **Student Management**: View profiles, track progress
- **Course Management**: Create courses, modules, exams
- **Resource Upload**: Upload PDFs and documents
- **Question Bank**: Create and manage MCQ questions
- **Certificate Issuance**: Generate and manage certificates
- **Bulletin Control**: Manage scrolling bulletin
- **Inline Editing**: Edit related objects inline

## 🛠️ Technology Stack

- **Backend**: Django 4.2
- **Database**: MySQL
- **PDF Generation**: ReportLab
- **Frontend**: HTML5, CSS3 (Vanilla CSS), JavaScript
- **Authentication**: Django Auth
- **File Handling**: Django File Storage

## 📋 Requirements

- Python 3.8+
- MySQL 5.7+ or MariaDB
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Install Python
Download and install Python from [python.org](https://www.python.org/downloads/)

### 2. Install MySQL
- Install XAMPP or standalone MySQL
- Start MySQL service
- Create a database named `nursing_center`

### 3. Install Dependencies

```bash
# Navigate to project directory
cd c:\xxampp\htdocs\Nursing

# Install required packages
pip install -r requirements.txt
```

### 4. Configure Database

Edit `.env` file with your MySQL credentials:

```env
DB_NAME=nursing_center
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### 5. Run Migrations

```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
# Create admin account
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 7. Collect Static Files

```bash
python manage.py collectstatic
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

## 🎨 Admin Panel Access

1. Navigate to: `http://127.0.0.1:8000/admin/`
2. Login with superuser credentials
3. Start managing your platform!

## 📖 Usage Guide

### For Administrators

1. **Create Batches**: Add batches with start/end dates
2. **Create Courses**: Add courses and assign to batches
3. **Add Modules**: Create ordered learning modules
4. **Upload Resources**: Add PDF files and documents
5. **Create Exams**: Build MCQ exams with questions
6. **Manage Students**: Register students and assign batches
7. **Post Announcements**: Communicate with students
8. **Set Bulletin**: Add scrolling Bengali bulletin text
9. **Configure Site**: Set hero title and background in Site Configuration

### For Students

1. **Register**: Create account with student ID
2. **Login**: Access your dashboard
3. **View Courses**: See courses assigned to your batch
4. **Study Modules**: Complete learning modules
5. **Download Resources**: Access course materials
6. **Take Exams**: Complete MCQ assessments
7. **View Results**: See detailed exam feedback
8. **Get Certificates**: Download completion certificates

## 🗂️ Project Structure

```
Nursing/
├── nursing_center/          # Project settings
│   ├── settings.py         # Django configuration
│   ├── urls.py            # Main URL routing
│   └── wsgi.py            # WSGI configuration
├── courses/                # Main application
│   ├── models.py          # Database models (User, Student, Course, etc.)
│   ├── views.py           # View functions
│   ├── admin.py           # Admin configuration
│   ├── forms.py           # Form definitions
│   ├── urls.py            # App URL routing
│   └── context_processors.py
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── home.html          # Homepage
│   ├── dashboard.html     # Student dashboard
│   ├── course_detail.html # Course page
│   ├── exam_detail.html   # Exam page
│   └── ...
├── static/                 # Static files
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       └── main.js        # JavaScript
├── media/                  # Uploaded files
├── manage.py              # Django management
├── requirements.txt       # Dependencies
└── .env                   # Environment config
```

---

# 📚 Admin Guide & Documentation

## 🎨 Admin Panel Features

### 1. 👥 **User & Student Management**

#### **Users**
- **What it does**: Manage all user accounts (students, staff, admins)
- **Key Features**:
  - ✅ View student ID and batch directly in the user list
  - ✅ Color-coded status indicators (Active/Inactive)
  - ✅ Inline student profile editing
  - ✅ Filter by batch, staff status, and activity

**How to add a student:**
1. Click "Users" → "Add User"
2. Fill in username and password
3. In the "Student Profile Information" section below:
   - Enter Student ID (required)
   - Enter Phone number (required)
   - Select Batch (required)
   - Add optional details (DOB, address, photo)
4. Click "Save"

#### **Student Profiles**
- **What it does**: Detailed student information and progress tracking
- **Key Features**:
  - 📊 Progress summary showing completed modules and passed exams
  - 📞 Contact information
  - 🔗 Quick link to view student's public profile
  - 📅 Date hierarchy for easy filtering by enrollment date

### 2. 📚 **Batch Management**

#### **Batches**
- **What it does**: Group students into batches for organized course delivery
- **Key Features**:
  - 📊 Visual status badges (Active/Inactive)
  - 👥 Student count display
  - 📖 Course count display
  - 📅 Date hierarchy for filtering

**Creating a new batch:**
1. Click "Batches" → "Add Batch"
2. Enter batch name (e.g., "Batch 2024-A")
3. Add description (optional but recommended)
4. Set start and end dates
5. Check "Active" to make it visible to students
6. Click "Save"

### 3. 📖 **Course Management**

#### **Courses**
- **What it does**: Create and manage courses with modules, exams, and resources
- **Key Features**:
  - 📖 Add modules directly within the course (inline)
  - 📝 Add exams directly within the course (inline)
  - 📄 Add resources directly within the course (inline)
  - 👥 Assign courses to multiple batches
  - 📊 Visual counters for modules, exams, and resources

**Creating a complete course (EASY WORKFLOW):**
1. Click "Courses" → "Add Course"
2. **Course Information Section:**
   - Enter course code (e.g., "NUR101")
   - Enter course title
   - Write description
   - Upload thumbnail image (optional)
3. **Course Settings:**
   - Set duration in weeks
   - Check "Active" to publish
4. **Assign to Batches:**
   - Select which batches can access this course
5. **Add Modules (scroll down):**
   - Click "Add another Module"
   - Enter section/module details
6. Click "Save"

---

# 🚀 Deployment Checklist

## Pre-Deployment Checklist

### ✅ Development Environment
- [ ] Python 3.8+ installed
- [ ] MySQL/MariaDB installed and running
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Database created (`nursing_center`)
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Development server runs successfully
- [ ] Admin panel accessible
- [ ] Student registration works
- [ ] Login/logout works
- [ ] All features tested

### ✅ Database Setup
- [ ] MySQL database created
- [ ] Correct character set (utf8mb4)
- [ ] Database user has proper permissions
- [ ] Connection settings in `.env` are correct
- [ ] Migrations completed without errors

### ✅ Admin Panel Configuration
- [ ] At least one Batch created
- [ ] At least one Course created
- [ ] Modules added to course
- [ ] Resources uploaded
- [ ] Exam with questions created
- [ ] Bulletin text added
- [ ] Announcement posted
- [ ] Test student registered

### ✅ Security
- [ ] SECRET_KEY changed from default
- [ ] DEBUG = False in production
- [ ] ALLOWED_HOSTS configured
- [ ] CSRF protection enabled
- [ ] SQL injection protection (using ORM)
- [ ] XSS protection (template escaping)
- [ ] File upload restrictions
- [ ] Login required on protected views

---

## 📅 Recent Updates & Fixes

### Registration System Fixes (Feb 2026)
1.  **Double-Submission Prevention**: Added frontend `onsubmit` handler to disable the submit button and show "Registering..." state. This prevents users from clicking multiple times and triggering "Email already registered" errors.
2.  **Simplified Email Validation**: Removed strict email validation logic that caused false positives.
3.  **Removed Google Sign-In**: Removed `django-allauth` dependencies to simplify the authentication flow. Registration now uses Username, First Name, Last Name, and optional Email.

### Dashboard Improvements
1.  **Welcome Message**: Fixed display issue where Welcome message would show template code. Now shows `Welcome, Name!` or `Welcome, Username!`.
2.  **Hero Title**: Fixed `{{ site_config.hero_title }}` display issue by adding `site_config_processor` to settings.



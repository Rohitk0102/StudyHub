# StudyHub - Online Learning Platform

A Django-based e-learning platform for teachers to create courses and students to enroll online.

## 🚀 Features

- **Course Management**: Create and manage courses
- **Student Enrollment**: Browse and enroll in courses  
- **OTP Authentication**: Secure 2-factor login
- **Modern UI**: Bootstrap 5 responsive design
- **Admin Panel**: Full administrative control

## 📋 Requirements

- Python 3.8+
- Django
- Modern web browser

## 🛠️ Quick Setup

### 1. Install & Setup
```bash
pip install django Pillow python-decouple
python manage.py makemigrations
python manage.py migrate
```

### 3. Run Server
```bash
# From project directory
python manage.py runserver

# OR with full path (from anywhere)
python3 manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## 🔑 Login Credentials

### Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@gmail.com`


## 🔐 OTP Authentication

**Important:** This app uses 2-factor authentication. When you login:

1. Enter username and password
2. **Check your terminal** where the server is running
3. **Copy the 6-digit OTP** from the terminal output
4. Enter the OTP in your browser to complete login

### What you'll see in terminal:
```
============================================================
🔐                OTP GENERATED FOR LOGIN                 🔐
============================================================
👤 USER EMAIL: admin@gmail.com
🔢 6-DIGIT OTP: 123456
⏰ EXPIRES IN: 5 minutes
============================================================
✅ OTP email sent successfully to admin@gmail.com
```

**Note:** The OTP appears in the terminal, NOT in email (for development).

## 🎯 Quick Start

1. **Start server:** `python manage.py runserver`
2. **Go to:** http://127.0.0.1:8000/login/
3. **Login with:** `admin` / `admin123`
4. **Check terminal** for OTP code
5. **Enter OTP** in browser
6. **Explore the platform!**

## 🔧 Admin Panel

Visit: **http://127.0.0.1:8000/admin/**
Login with admin credentials to manage users, courses, and content.

---

**Built with Django & Bootstrap 5** 

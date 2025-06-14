# 🚀 Django REST Authentication Auto-Setup Script

This repository contains a Python script that fully automates the setup of authentication in Django REST projects using JWT, email, CORS, environment configs, and more.

## 🎯 What It Does

- ✅ Detects and uses existing virtual environments
- ✅ Installs required packages from `requirements.txt`
- ✅ Creates a Django project and authentication app
- ✅ Copies your custom authentication files
- ✅ Sets up JWT authentication (access + refresh)
- ✅ Configures email backend for notifications
- ✅ Handles CORS and environment variables
- ✅ Runs migrations and optionally starts the dev server

## 🛠️ Key Features

- One-command project setup
- Smart virtualenv detection
- Pre-configured settings using best practices
- Cross-platform support (Windows/Linux/Mac)
- Environment-based configuration with `.env`
- Ready-to-use auth endpoints (register, login, profile)

## 📦 What's Included

- 🔐 JWT Authentication
- 👤 User registration/login/profile APIs
- 📧 Email backend configuration
- 🌐 CORS setup for frontend integration
- 🔐 Secure `.env` variable loading via `python-dotenv`

## 🚀 Getting Started

1. Clone the repository:
```bash
git clone https://github.com/berhab-zakarya/django-rest-auth-generator.git
cd django-rest-auth-generator

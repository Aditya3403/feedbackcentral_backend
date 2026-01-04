# Feedback Central - Backend
A high-performance backend service for Feedback Central built with FastAPI and Python, providing RESTful APIs for feedback management.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3.41+-003B57?logo=sqlite)](https://www.sqlite.org/)


## ✨ Features
- **FastAPI**: High-performance Python framework
- **SQLite Database**: Lightweight and efficient data storage
- **JWT Authentication**: Secure token-based auth
- **Docker Support**: Easy containerization
- **Logging**: Comprehensive request/error logging
- **Pydantic Models**: Type-safe data validation

## 🛠 Tech Stack

**Core:**
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: Python 3.11+
- **Database**: SQLite
- **ORM**: SQLAlchemy

## 📦 Getting Started

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aditya3403/feedbackcentral-backend.git
   cd feedbackcentral-backend

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   uvicorn app.main:app --reload

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

4. **Configure environment**
   ```bash
    EMAIL_FROM=your-email@gmail.com
    EMAIL_FROM_NAME=FeedbackCentral


    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=your-email@gmail.com
    SMTP_PASSWORD=your access token
    SMTP_USE_TLS=true
    SMTP_USE_SSL=false

    FRONTEND_URL=http://localhost:3000

3. **Start the server**
   ```bash
   uvicorn app.main:app --reload

Built with ❤️ using FastAPI and Python

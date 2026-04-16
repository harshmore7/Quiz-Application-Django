# 🧠 Quiz Application (Django)

A full-stack MCQ-based quiz platform built with **Django**. This application allows users to register, take subject-specific tests, and track their performance over time.

---

## 🚀 Features

* 👤 **User Authentication:** Secure registration and login system.
* 🧑 **Student Dashboard:** Personalized area to view available tests.
* 📝 **Subject-wise Tests:** Categorized quizzes for organized learning.
* ⏱ **Timer-based System:** Real-time countdown for quiz attempts.
* 📊 **Result Tracking:** Instant score generation upon submission.
* 🧾 **Answer Review:** Post-test review to check correct vs. incorrect answers.
* 🔐 **Admin Panel:** Easy-to-use interface for managing questions and categories.

---

## 🏗 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Django (Python) |
| **Frontend** | HTML5, CSS3, Bootstrap |
| **Database** | SQLite (Default) |

---

## 📂 Project Structure

```text
examapp/
├── models.py          # Database schemas for Quiz, Question, and Results
├── views.py           # Core logic for handling requests
└── templates/
    └── examapp/
        ├── base.html           # Main layout template
        ├── login.html          # Authentication page
        ├── test_question.html  # Active quiz interface
        ├── start_test.html     # Quiz instructions & start page
        └── result.html         # Score summary and review
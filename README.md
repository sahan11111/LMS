<div align="center">

# 🎓 Enhanced Learning Management System (LMS)

**A full-stack, role-based Learning Management System built with Django REST Framework & React**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

A feature-rich platform for **Admins**, **Instructors**, **Students**, and **Sponsors** — supporting course management, enrollment tracking, assessments, quizzes, sponsorship workflows, real-time notifications, and email updates.

</div>

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [User Roles & Permissions](#-user-roles--permissions)
- [Screenshots](#-screenshots)
- [Database Schema](#-database-schema)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🔐 Authentication & Security
- Email-based registration with **OTP verification**
- Token-based authentication (DRF TokenAuth)
- Forgot password flow with OTP email reset
- Role-based access control (RBAC)
- Auto-group assignment on signup

### 👥 Role-Based Dashboards
| Role | Capabilities |
|------|-------------|
| **Admin** | Full system control — manage all users, courses, enrollments, assessments, sponsors, and view platform analytics |
| **Instructor** | Create/manage own courses, quizzes, assessments; grade student submissions |
| **Student** | Browse/enroll in courses, take quizzes, submit assessments, apply for sponsorships |
| **Sponsor** | Create sponsor profiles, fund students, approve/reject sponsorship requests, track utilization |

### 📚 Course Management
- CRUD operations for courses with difficulty levels
- Modular course structure: **Course → Module → Lesson → Lesson Content**
- Support for multiple content types (PDF, Video, Text)
- Search and filtering by title
- Paginated course listings

### 📝 Assessments & Quizzes
- Create assessments linked to courses and modules
- Student submission with enrollment validation
- Instructor grading with score validation
- Interactive quizzes with multiple-choice questions
- Auto-scoring with pass/fail calculation
- One submission per student per quiz

### 💰 Sponsorship System
- Sponsors can create profiles and manage funds
- Students can apply for sponsorships
- Sponsors can approve/reject requests with automatic fund deduction
- Utilization tracking
- Notification on every sponsorship status change

### 🔔 Notifications & Email
- In-app notification system
- Email notifications on enrollment, OTP, and password reset
- Email logging for audit trail
- Mark-as-read functionality

### 📊 Analytics Dashboard
- Role-specific dashboard statistics
- Admin: platform-wide overview
- Instructor: personal course metrics
- Student: enrollment and quiz performance
- Sponsor: fund utilization and student tracking

### 🎨 Modern React Frontend
- Clean, responsive UI with Tailwind CSS
- Collapsible sidebar navigation
- Role-based menu filtering
- Modal forms for CRUD operations
- Toast notifications for user feedback
- Search, pagination, and data tables
- Loading states and empty state handling

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                    React Frontend                    │
│        (React 18 + Tailwind CSS + Axios)            │
│  ┌──────────┐ ┌──────────��� ┌──────────┐            │
│  │   Auth   │ │Dashboard │ │  Pages   │            │
│  │  Pages   │ │  Stats   │ │ (CRUD)   │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (Token Auth)
┌──────────────────────▼──────────────────────────────┐
│               Django REST Framework                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  core/   │ │   app/   │ │ project/ │            │
│  │  (Auth)  │ │  (LMS)   │ │(Settings)│            │
│  └──────────┘ └──────────┘ └──────────┘            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Signals  │ │ Permis-  │ │ Swagger  │            │
│  │ (Email)  │ │  sions   │ │  Docs    │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   SQLite / PG   │
              │    Database     │
              └─────────────────┘
```

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core language |
| **Django 4.2** | Web framework |
| **Django REST Framework 3.15** | REST API |
| **DRF TokenAuth** | Authentication |
| **drf-yasg** | Swagger/OpenAPI documentation |
| **django-filter** | Queryset filtering |
| **django-cors-headers** | Cross-origin requests |
| **django-seed** | Database seeding |
| **python-dotenv** | Environment variable management |
| **SQLite** (dev) / **PostgreSQL** (prod) | Database |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **React Router v6** | Client-side routing |
| **Tailwind CSS 3** | Utility-first styling |
| **Axios** | HTTP client |
| **react-hot-toast** | Toast notifications |
| **react-icons** | Icon library |

---

## 📂 Project Structure

```
LMS/
├── 📁 project/                 # Django project configuration
│   ├── settings.py             # Settings (DB, Auth, DRF, Email, CORS)
│   ├── urls.py                 # Root URL routing + Swagger
│   ├── wsgi.py
│   └── asgi.py
│
├── 📁 core/                    # Authentication & User Management
│   ├── models.py               # Custom User model (email-based, roles)
│   ├── managers.py             # Custom UserManager (auto-generated username)
│   ├── views.py                # Login, Register, OTP, Password Reset
│   ├── serializers.py          # User serializers with OTP logic
│   ├── signals.py              # Auto-create role groups & permissions
│   ├── urls.py                 # Auth endpoints
│   └── admin.py
│
├── 📁 app/                     # Main LMS Functionality
│   ├── models.py               # Course, Enrollment, Assessment, Quiz, Sponsor, etc.
│   ├── views.py                # ViewSets for all resources + Dashboard
│   ├── serializers.py          # DRF serializers with nested writes
│   ├── permissions.py          # Role-based permissions (IsAdmin, IsInstructor, etc.)
│   ├── signals.py              # Enrollment email notifications
│   ├── pagination.py           # Custom pagination
│   ├── urls.py                 # App endpoints
│   └── admin.py
│
├── 📁 lms-frontend/            # React Frontend
│   ├── 📁 src/
│   │   ├── 📁 api/             # Axios API layer
│   │   │   ├── axios.js        # Axios instance + interceptors
│   │   │   ├── auth.js         # Auth API calls
│   │   │   ├── courses.js      # Course CRUD
│   │   │   ├── enrollments.js  # Enrollment CRUD
│   │   │   ├── assessments.js  # Assessment CRUD
│   │   │   ├── submissions.js  # Submission CRUD + grading
│   │   │   ├── quizzes.js      # Quiz CRUD + submissions
│   │   │   ├── sponsors.js     # Sponsor + Sponsorship API
│   │   │   ├── dashboard.js    # Dashboard stats
│   │   │   └── notifications.js
│   │   ├── 📁 context/
│   │   │   └── AuthContext.js   # Auth state management
│   │   ├── 📁 components/
│   │   │   ├── 📁 Layout/
│   │   │   │   ├── AppLayout.jsx   # Protected layout wrapper
│   │   │   │   └── Sidebar.jsx     # Collapsible role-based sidebar
│   │   │   └── 📁 UI/
│   │   │       ├── PageHeader.jsx
│   │   │       ├── StatsCard.jsx
│   │   │       ├── DataTable.jsx
│   │   │       ├── Modal.jsx
│   │   │       ├── Pagination.jsx
│   │   │       └── StatusBadge.jsx
│   │   ├── 📁 pages/
│   │   │   ├── 📁 Auth/        # Login, Register, Verify, Forgot Password
│   │   │   ├── 📁 Dashboard/   # Role-specific analytics
│   │   │   ├── 📁 Courses/     # Course listing + CRUD modals
│   │   │   ├── 📁 Enrollments/ # Enrollment table with progress bars
│   │   │   ├── 📁 Assessments/ # Assessment management
│   │   │   ├── 📁 Submissions/ # Submission viewing + grading
│   │   │   ├── 📁 Quizzes/     # Quiz management
│   │   │   ├── 📁 Sponsors/    # Sponsor profiles
│   │   │   ├── 📁 Sponsorships/# Approve/reject workflows
│   │   │   ├── 📁 Notifications/
│   │   │   └── 📁 Users/       # Admin user listing
│   │   ├── App.js              # Root component + routes
│   │   ├── index.js            # React entry point
│   │   └── index.css           # Tailwind + custom utilities
│   ├── tailwind.config.js
│   ├── .env
│   └── package.json
│
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10 or higher
- **Node.js** 18+ and **npm** 9+
- **Git**

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/sahan11111/LMS.git
cd LMS

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (see Environment Variables section)
cp .env.example .env
# Edit .env with your values

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create a superuser (Admin)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

The backend API will be available at **http://localhost:8000**

> 📖 **Swagger Docs**: http://localhost:8000/swagger/
> 📖 **ReDoc**: http://localhost:8000/redoc/
> 🔧 **Admin Panel**: http://localhost:8000/admin/

### Frontend Setup

```bash
# 1. Navigate to the frontend directory
cd lms-frontend

# 2. Install dependencies
npm install

# 3. Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# 4. Start the development server
npm start
```

The frontend will be available at **http://localhost:3000**

---

## 🔑 Environment Variables

### Backend (`.env`)

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (Mailtrap for development)
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=587
EMAIL_HOST_USER=your-mailtrap-user
EMAIL_HOST_PASSWORD=your-mailtrap-password
SENDER_EMAIL_USER=noreply@lms.com
DEFAULT_FROM_EMAIL=noreply@lms.com

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (`.env`)

```env
REACT_APP_API_URL=http://localhost:8000
```

> ⚠️ **Security Warning**: Never commit `.env` files to version control. Add `.env` to your `.gitignore`.

---

## 📡 API Endpoints

### Authentication (`/user/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/user/` | Register new user | ❌ |
| `POST` | `/user/login/` | Login (returns token) | ❌ |
| `PUT` | `/user/verification/` | Verify email with OTP | ❌ |
| `POST` | `/user/send_otp_forgot_password/` | Send forgot password OTP | ❌ |
| `PUT` | `/user/update_forgot_password/` | Reset password with OTP | ❌ |
| `GET` | `/user/detail/` | Get current user details | ✅ |
| `GET` | `/user/list_users/` | List all users (Admin) | ✅ |

### Courses (`/Course/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/Course/` | List courses (paginated, searchable) | ✅ |
| `POST` | `/Course/` | Create course (Admin/Instructor) | ✅ |
| `GET` | `/Course/{id}/` | Get course detail | ✅ |
| `PUT` | `/Course/{id}/` | Update course | ✅ |
| `DELETE` | `/Course/{id}/` | Delete course | ✅ |

### Enrollments (`/Enrollment/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/Enrollment/` | List enrollments (role-filtered) | ✅ |
| `POST` | `/Enrollment/` | Enroll in a course (Student) | ✅ |
| `GET` | `/Enrollment/{id}/` | Get enrollment detail | ✅ |
| `PUT` | `/Enrollment/{id}/` | Update enrollment | ✅ |
| `DELETE` | `/Enrollment/{id}/` | Remove enrollment | ✅ |

### Assessments (`/Assessment/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/Assessment/` | List assessments | ✅ |
| `POST` | `/Assessment/` | Create assessment (Admin/Instructor) | ✅ |
| `GET` | `/Assessment/{id}/` | Get assessment detail | ✅ |
| `PUT` | `/Assessment/{id}/` | Update assessment | ✅ |
| `DELETE` | `/Assessment/{id}/` | Delete assessment | ✅ |

### Submissions (`/Submission/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/Submission/` | List submissions | ✅ |
| `POST` | `/Submission/` | Submit assessment (Student) | ✅ |
| `PATCH` | `/Submission/{id}/grade/` | Grade submission (Instructor) | ✅ |

### Quizzes (`/Quiz/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/Quiz/` | List quizzes | ✅ |
| `POST` | `/Quiz/` | Create quiz with questions (Admin/Instructor) | ✅ |
| `GET` | `/Quiz/{id}/` | Get quiz detail with questions | ✅ |
| `PUT` | `/Quiz/{id}/` | Update quiz | ✅ |
| `DELETE` | `/Quiz/{id}/` | Delete quiz | ✅ |
| `GET` | `/QuizSubmissions/` | List quiz submissions | ✅ |
| `POST` | `/QuizSubmissions/` | Submit quiz answers (Student) | ✅ |

### Sponsors & Sponsorships

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/Sponsor/` | List sponsor profiles | ✅ |
| `POST` | `/Sponsor/` | Create sponsor profile | ✅ |
| `GET` | `/Sponsorship/` | List sponsorships | ✅ |
| `POST` | `/Sponsorship/` | Create/apply for sponsorship | ✅ |
| `PUT` | `/Sponsorship/{id}/` | Approve/reject sponsorship (Sponsor) | ✅ |

### Dashboard & Notifications

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/Dashboard/` | Get role-specific dashboard stats | ✅ |
| `GET` | `/Notification/` | List notifications | ✅ |
| `PATCH` | `/Notification/{id}/` | Mark notification as read | ✅ |
| `GET` | `/EmailLog/` | List email logs | ✅ |

---

## 👥 User Roles & Permissions

```
┌──────────────┬───────────┬────────────┬───────────┬───────────┐
│   Feature    │   Admin   │ Instructor │  Student  │  Sponsor  │
├──────────────┼───────────┼────────────┼───────────┼───────────┤
│ Manage Users │    ✅     │     ❌     │    ❌     │    ❌     │
│ View All     │    ✅     │     ❌     │    ❌     │    ❌     │
│ Create Course│    ✅     │     ✅     │    ❌     │    ❌     │
│ Edit Course  │    ✅     │   Own ✅   │    ❌     │    ❌     │
│ View Courses │    ✅     │     ✅     │    ✅     │    ✅     │
│ Enroll       │    ❌     │     ❌     │    ✅     │    ❌     │
│ Create Quiz  │    ✅     │     ✅     │    ❌     │    ❌     │
│ Take Quiz    │    ❌     │     ❌     │    ✅     │    ❌     │
│ Create Assess│    ✅     │     ✅     │    ❌     │    ❌     │
│ Submit Work  │    ❌     │     ❌     │    ✅     │    ❌     │
│ Grade Work   │    ❌     │   Own ✅   │    ❌     │    ❌     │
│ Fund Students│    ❌     │     ❌     │    ❌     │    ✅     │
│ Apply Sponsor│    ❌     │     ❌     │    ✅     │    ❌     │
│ Approve Spons│    ❌     │     ❌     │    ❌     │    ✅     │
│ Dashboard    │  Full ✅  │  Own ✅    │  Own ✅   │  Own ✅   │
│ Notifications│    ✅     │     ✅     │    ✅     │    ✅     │
└──────────────┴───────────┴────────────┴───────────┴───────────┘
```

---

## 🖼 Screenshots

> Add your screenshots here by placing images in a `screenshots/` folder.

| Login Page | Dashboard (Admin) |
|:---:|:---:|
| ![Login](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) |

| Courses | Quiz Page |
|:---:|:---:|
| ![Courses](screenshots/courses.png) | ![Quizzes](screenshots/quizzes.png) |

| Notifications | Sponsorships |
|:---:|:---:|
| ![Notifications](screenshots/notifications.png) | ![Sponsorships](screenshots/sponsorships.png) |

---

## 🗄 Database Schema

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│     User      │     │    Course     │     │   Module      │
│───────────────│     │───────────────│     │───────────────│
│ id            │     │ id            │     │ id            │
│ email (PK)    │◄────│ created_by_id │     │ course_id     │
│ username      │     │ title         │     │ title         │
│ role          │     │ description   │     │ description   │
│ otp           │     │ difficulty    │     │ created_by_id │
│ otp_created_at│     │ created_at    │     │ created_at    │
│ is_active     │     │ updated_at    │     │ updated_at    │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        │              ┌──────▼──────┐       ┌──────▼──────┐
        │              │ Enrollment  │       │   Lesson    │
        │              │─────────────│       │─────────────│
        ├─────────────►│ student_id  │       │ module_id   │
        │              │ course_id   │       │ title       │
        │              │ status      │       │ content     │
        │              │ progress    │       └──────┬──────┘
        │              └─────────────┘              │
        │                                    ┌──────▼──────┐
        │              ┌─────────────┐       │LessonContent│
        │              │ Assessment  │       │─────────────│
        │              │─────────────│       │ lesson_id   │
        │              │ course_id   │       │ title       │
        │              │ module_id   │       │ content_type│
        │              │ title       │       │ file        │
        │              │ due_date    │       └─────────────┘
        │              │ max_score   │
        │              └──────┬──────┘
        │                     │
        │              ┌──────▼──────┐
        ├─────────────►│ Submission  │
        │              │─────────────│
        │              │ assessment  │
        │              │ student_id  │
        │              │ score       │
        │              │ content     │
        │              └─────────────┘
        │
        │  ┌──────────┐  ┌────────────┐  ┌──────────────┐
        │  │  Quiz    │  │  Question  │  │    Answer     │
        │  │──────────│  │────────────│  │──────────────│
        │  │ course_id│─►│ quiz_id    │─►│ question_id  │
        │  │ title    │  │ text       │  │ text         │
        │  │created_by│  └────────────┘  │ is_correct   │
        │  └──────────┘                  └──────────────┘
        │
        │  ┌──────────────┐     ┌──────────────┐
        │  │   Sponsor    │     │ Sponsorship  │
        │  │──────────────│     │──────────────│
        ├─►│ user_id      │────►│ sponsor_id   │
        │  │ company_name │     │ student_id   │◄──── User
        │  │ funds        │     │ amount       │
        │  └──────────────┘     │ status       │
        │                       │ utilization  │
        │                       └──────────────┘
        │
        │  ┌──────────────┐     ┌──────────────┐
        └─►│ Notification │     │  EmailLog    │
           │──────────────│     │──────────────│
           │ user_id      │     │ user_id      │
           │ message      │     │ subject      │
           │ type         │     │ body         │
           │ is_read      │     │ created_at   │
           └──────────────┘     └──────────────┘
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m "feat: add amazing feature"
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Commit Convention

| Prefix | Description |
|--------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `style:` | Formatting, no code change |
| `refactor:` | Code restructuring |
| `test:` | Adding tests |
| `chore:` | Maintenance tasks |

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [sahan11111](https://github.com/sahan11111)**

⭐ Star this repo if you find it helpful!

</div>
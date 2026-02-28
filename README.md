# 📚 Library Management System with Django REST Framework

<div align="center">

[![Django](https://img.shields.io/badge/Django-4.2+-green?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)

A comprehensive **library management system** built with **Django** and **Django REST Framework (DRF)**.

</div>

---

## 🌟 Project Overview

This project implements a modern library management system with features for managing books, authors, and library operations through a **RESTful API**. Designed for scalability and ease of use, it provides both administrative interfaces and programmatic access to library resources.

## ✨ Features

- 📖 **Book Management**: Add, edit, delete, and search books with rich metadata
- 👤 **Author Management**: Comprehensive author profiles and book associations
- 🔐 **User Authentication**: Secure login and role-based permissions
- 🌐 **RESTful API**: Clean, well-documented endpoints for integration
- ⚙️ **Admin Interface**: Intuitive dashboard for management tasks
- 📱 **Responsive Design**: Works seamlessly across devices

## 🛠️ Technologies Used

- **Python 3.x** - Programming language
- **Django** - Web framework
- **Django REST Framework** - API toolkit
- **PostgreSQL** - Useful database
- **HTML/CSS/JS** - Frontend components

## 🚀 Installation

Follow these simple steps to get started:

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser Account
```bash
python manage.py createsuperuser
```

### 6. Launch Development Server
```bash
python manage.py runserver
```

Your application will be available at `http://127.0.0.1:8000/`

## 🌐 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/` | Api root |
| `GET /api/books/` | Retrieve all books |
| `POST /api/books/` | Create a new book |
| `GET /api/books/{id}/` | Retrieve specific book |
| `PUT /api/books/{id}/` | Update specific book |
| `DELETE /api/books/{id}/` | Delete specific book |
| `GET /api/books/{id}/borrows` | Borrowing or reserving specific book |
| `GET /api/authors/` | Manage authors |
| `GET /api/authors/{id}/` | Retrieve specific authors |
| `GET /api/categories/` | Manage categories |
| `GET /api/categories/{id}/` | Retrieve specific category |
| `GET /api/publishers/` | Manage publishers |
| `GET /api/publishers/{id}/` | Retrieve specific publisher |
| `GET /api/borrows_history/` | View deposit history |
| `GET /api/reserv_history/` | View reservation history |

## 📁 Project Structure

```
Library_with_DRF/          # Django project settings
├── library/               # Main application
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── urls.py            # URL patterns
│   ├── admin.py           # Admin configuration
│   ├── forms.py           # Forms
│   ├── permissions.py     # Custom permissions
│   ├── static/            # Static files
│   ├── templates/         # HTML templates
│   └── migrations/        # Database migrations
├── manage.py              # Django management script
└── requirements.txt       # Project dependencies
```

## 💡 Usage

1. **Admin Panel**: Access the admin panel at `/admin/` to manage data manually
2. **API Integration**: Use the API endpoints to interact with the library system programmatically
3. **CRUD Operations**: The API supports standard Create, Read, Update, and Delete operations for books and authors
4. **Search Functionality**: Find books and authors quickly with search capabilities

## ⚙️ Configuration

The project uses Django's standard settings structure. Key configurations include:
- Database settings in `settings.py`
- Custom permissions in `library/permissions.py`
- API serialization in `library/serializers.py`
- URL routing in `library/urls.py`

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. 🍴 **Fork** the repository
2. 🌿 **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. ✏️ **Make your changes**
4. 🚀 **Submit a pull request**

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## 📞 Support

For support, please open an issue in the repository or contact the maintainers.

---

<div align="center">

Made with ❤️ using Django and Django REST Framework

</div>

# 🧾 Automated Mess Billing System

<div align="center">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3">
</div>

<div align="center">
  <h3>A comprehensive Django web application for hostel mess billing and student management</h3>
  <p>Developed for Women's Hostel administration to streamline billing processes and reduce manual errors</p>
</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technologies](#-technologies)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

## 🎯 Overview

The Automated Mess Billing System is a Django-based web application designed specifically for hostel management. It automates the complex process of calculating mess bills based on student attendance, manages room allocations, and provides a comprehensive dashboard for hostel administrators.

### Problem Solved
- **Manual Billing Errors**: Eliminates calculation mistakes in mess bill generation
- **Time-Consuming Processes**: Automates attendance tracking and bill calculation
- **Data Management**: Centralizes student information and room allocation
- **Administrative Overhead**: Reduces manual work for hostel staff

## ✨ Features

### 🏠 **Student Management**
- Complete student profile management with personal details
- Room allocation and management system
- Profile image optimization (auto-conversion to WebP format)

### 📊 **Attendance System**
- Daily attendance tracking interface
- Continuous absence monitoring

### 💰 **Billing Engine**
- Automated mess bill calculation based on attendance criteria
- Monthly bill generation with detailed breakdowns
- Bill history

### 🎛️ **Admin Dashboard**
- Intuitive interface for hostel staff
- Real-time statistics and analytics
- User role management
- System configuration settings

### 📱 **Responsive Design**
- Mobile-friendly interface
- Cross-browser compatibility

## 🛠️ Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Backend development |
| **Django** | 5.x | Web framework |
| **SQLite** | Latest | Database (development) |
| **Pillow** | Latest | Image processing |
| **HTML5/CSS3** | - | Frontend templates |
| **JavaScript** | ES6+ | Interactive features |

## 🚀 Installation

### Prerequisites

Make sure you have the following installed:
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Quick Start

1. **Clone the repository**
   \`\`\`bash
   git clone https://github.com/jitheshjr/Hostel_Manangement_System.git
   cd Hostel_Manangement_System
   \`\`\`

2. **Create a virtual environment**
   \`\`\`bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   \`\`\`

3. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Set up the database**
   \`\`\`bash
   python manage.py makemigrations
   python manage.py migrate
   \`\`\`

5. **Create a superuser**
   \`\`\`bash
   python manage.py createsuperuser
   \`\`\`

6. **Run the development server**
   \`\`\`bash
   python manage.py runserver
   \`\`\`

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`


## 📈 Performance

- **Database Optimization**: Indexed queries for faster lookups
- **Image Optimization**: WebP conversion reduces storage by 30%
- **Responsive Design**: Mobile-first approach

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Academic Use**: This project was developed for educational purposes. If you use or extend this project, please provide proper attribution.

## 🙏 Acknowledgments

- **Django Community** - For the excellent web framework
- **College Hostel Staff** - For valuable feature requirements and testing
- **Open Source Contributors** - For various libraries and tools used
- **Women's Hostel Administration** - For supporting this digital transformation

<div align="center">
  <p>Made with ❤️ for hostel management automation</p>
  <p>⭐ Star this repo if you found it helpful!</p>
</div>

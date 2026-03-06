Military Tanks Figurine Store

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Django Framework](https://img.shields.io/badge/framework-Django%205.0-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust, **Full-Stack E-commerce platform** built from scratch for enthusiasts of military history and scale model building. This project demonstrates the implementation of a complex MVT (Model-View-Template) architecture, user security, and dynamic frontend interactions.


Features

User Management & Security
* **Custom Authentication**: Secure registration and login system.
* **Email Confirmation**: Integration of automated verification emails upon sign-up.
* **Profile Management**: Personalized user dashboards and password recovery.
* **Access Control**: Middleware implementation for restricted areas and 403 error handling.

Shopping Experience
* **Dynamic Catalog**: Products organized by historical series (WWII, Modern, etc.) and categories.
* **Interactive Cart**: A seamless "Add to Cart" experience managed via Vanilla JavaScript.
* **Product Details**: High-quality image rendering and detailed specifications for each tank model.
* **Promotions System**: Dedicated views for special offers and discounted items.

Backend & Administration
* **Custom Admin Panel**: Tailored Django Admin interface for efficient inventory management.
* **Automated Backups**: Shell scripts (`.sh`) for SQL database backups.
* **Logging & Monitoring**: Custom middleware to track site activity and errors.
* **SEO Ready**: Built-in sitemaps for search engine optimization.

Tech Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Python, Django |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Database** | SQLite (Development) / PostgreSQL (Production) |
| **Tools** | Git, Docker, Linux, CMAKE |



<img width="1889" height="886" alt="image" src="https://github.com/user-attachments/assets/d3b83c2f-a4a0-496d-9076-bc35c0d0bfc8" />

<img width="1889" height="886" alt="image" src="https://github.com/user-attachments/assets/91770c73-1c7a-48d6-8838-85316764901f" />

<img width="1889" height="940" alt="image" src="https://github.com/user-attachments/assets/9f693703-da84-433c-89d2-196fbec0a3a3" />



# Installation & Setup
Follow these steps to get the project running locally on your machine.

# Prerequisites
Python 3.12 or higher installed.

Git installed.

# Clone the Repository
``` bash 
git clone https://github.com/ValentinB01/Military-Tanks-Figurines-shop-in-Django.git
cd Military-Tanks-Figurines-shop-in-Django
```

# Create and Activate a Virtual Environment
It is highly recommended to use a virtual environment to keep dependencies isolated.


Create venv
``` bash 
python -m venv venv
```

Activate on Windows:
``` bash 
venv\Scripts\activate
```

Activate on Linux/macOS:
``` bash 
source venv/bin/activate
```

## Install Dependencies
If you haven't created a requirements.txt yet, you should do so. To install them, run:

``` bash 
pip install django
```
Add any other libraries you used, like:
``` bash 
pip install pillow (for images)
```
(Note: If you already have a requirements.txt, just run pip install -r requirements.txt).

## Database Setup & Migrations
Initialize the SQLite database and create the necessary tables:

``` bash 
python manage.py makemigrations
python manage.py migrate
```
## Populate Initial Data (Optional)
To quickly see the shop with products (Tanks), run the population script:

``` bash 
python manage.py shell < proiectapp/populate_tancuri.py
```

## Create an Admin Account
To access the /admin dashboard and manage figurines or users:

``` bash 
python manage.py createsuperuser
```

Follow the prompts to set your username, email, and password.

## Run the Development Server
``` bash 
python manage.py runserver
```
Once started, open your browser and navigate to: http://127.0.0.1:8000/

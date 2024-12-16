# Library System API

This project is a Library System API built using Django and Django REST Framework. It supports managing books, authors, borrow records, and generating reports.

## Steps to Run the Project

### 1. Clone the Repository
Clone the repository to your local machine:

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
2. Set Up Virtual Environment (Optional but Recommended)
To create an isolated environment for your project, follow these steps:

Install virtualenv if you don't have it:

bash
Copy code
pip install virtualenv
Create a virtual environment:

bash
Copy code
virtualenv venv
Activate the virtual environment:

On Windows:

bash
Copy code
venv\Scripts\activate
On macOS/Linux:

bash
Copy code
source venv/bin/activate
3. Install Dependencies
Install all required dependencies using requirements.txt:

bash
Copy code
pip install -r requirements.txt
4. Set Up Celery
To handle background tasks, we use Celery with Redis as the broker.

Install Redis (either locally or use a Redis cloud service like Redis Labs).

In the settings.py file of your Django project, configure Celery with Redis as the broker:

python
Copy code
CELERY_BROKER_URL = 'redis://localhost:6379/0'
Start Celery in a new terminal window:

bash
Copy code
celery -A your_project_name worker --loglevel=info
5. Run Migrations
Apply migrations to set up the database:

bash
Copy code
python manage.py migrate
6. Create Superuser (Admin)
Create a superuser account to access the Django admin panel:

bash
Copy code
python manage.py createsuperuser
7. Run the Development Server
Start the development server:

bash
Copy code
python manage.py runserver
The API will be available at http://127.0.0.1:8000.

API Documentation
The API documentation is available at http://127.0.0.1:8000/docs.

API Endpoints
POST /api/token/ - Obtain JWT token (username, password).
POST /api/token/refresh/ - Refresh JWT token.
POST /api/borrow/ - Borrow a book (JWT required).
PUT /api/borrow/<id>/return/ - Return a borrowed book (JWT required).
GET /api/reports/latest/ - Get the latest report (JWT required).
GET /api/books/ - Get the list of books (JWT required).
GET /api/authors/ - Get the list of authors (JWT required).
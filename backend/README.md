# Auto Triage Backend

## Environment Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env File
Create a `.env` file in the root directory with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Configuration
DB_NAME=auto_triage
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```

### 3. PostgreSQL Setup
1. Install PostgreSQL on your system
2. Create a database named `auto_triage`
3. Update the `.env` file with your PostgreSQL credentials

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

## Environment Variables

- `SECRET_KEY`: Django secret key for security
- `DEBUG`: Set to 'True' for development, 'False' for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: PostgreSQL username
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: PostgreSQL host (usually localhost)
- `DB_PORT`: PostgreSQL port (default: 5432)

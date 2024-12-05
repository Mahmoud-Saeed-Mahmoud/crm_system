# CRM System

A Customer Relationship Management (CRM) system designed to help sales and customer service teams manage their customer interactions effectively. Created with [Windsurf](https://www.windsurfai.com/), the world's first agentic IDE.

## Features

- User Authentication
- Customer Management
- Interaction Tracking
- Dashboard with Key Metrics
- Responsive Design

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

- `app.py`: Main application file with routes and models
- `templates/`: HTML templates
  - `base.html`: Base template with common layout
  - `index.html`: Dashboard template
  - `login.html`: Login page
  - `customer_form.html`: New customer form
  - `customer_detail.html`: Customer details page
- `requirements.txt`: Project dependencies

## Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- SQLite (database)
- Bootstrap 5 (frontend)

## Security Note

Make sure to change the secret key in `app.py` before deploying to production.

## Credits

This project was created using [Windsurf](https://www.windsurfai.com/), an innovative AI-powered IDE that enables rapid application development through natural language interaction.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

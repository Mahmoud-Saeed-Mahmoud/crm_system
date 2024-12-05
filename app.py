from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    interactions = db.relationship('Interaction', backref='customer', lazy=True)

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    type = db.Column(db.String(20))
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('Please log in to access this page.')
    return redirect(url_for('login'))

# Routes
@app.route('/')
@login_required
def index():
    customers = Customer.query.all()
    return render_template('index.html', customers=customers)

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if User.query.first():
        return "Setup already completed."
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if username and email and password:
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            flash('Admin user created successfully!')
            return redirect(url_for('login'))
    
    return render_template('setup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/analytics')
@login_required
def analytics():
    # Get customer statistics
    total_customers = Customer.query.count()
    new_customers_month = Customer.query.filter(
        Customer.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    # Get interaction statistics
    total_interactions = Interaction.query.count()
    interactions_by_type = db.session.query(
        Interaction.type, 
        func.count(Interaction.id)
    ).group_by(Interaction.type).all()
    
    # Get customer status distribution
    status_distribution = db.session.query(
        Customer.status, 
        func.count(Customer.id)
    ).group_by(Customer.status).all()
    
    return render_template('analytics.html',
                         total_customers=total_customers,
                         new_customers_month=new_customers_month,
                         total_interactions=total_interactions,
                         interactions_by_type=interactions_by_type,
                         status_distribution=status_distribution)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Handle profile update
        current_user.email = request.form.get('email', current_user.email)
        if request.form.get('new_password'):
            current_user.password = generate_password_hash(request.form.get('new_password'))
        db.session.commit()
        flash('Settings updated successfully!')
        return redirect(url_for('settings'))
    
    return render_template('settings.html')

@app.route('/customer/new', methods=['GET', 'POST'])
@login_required
def new_customer():
    if request.method == 'POST':
        customer = Customer(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            company=request.form.get('company'),
            status=request.form.get('status')
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!')
        return redirect(url_for('customer_detail', id=customer.id))
    return render_template('customer_form.html')

@app.route('/customer/<int:id>')
@login_required
def customer_detail(id):
    customer = Customer.query.get_or_404(id)
    return render_template('customer_detail.html', customer=customer)

@app.route('/customer/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form.get('name', customer.name)
        customer.email = request.form.get('email', customer.email)
        customer.phone = request.form.get('phone', customer.phone)
        customer.company = request.form.get('company', customer.company)
        customer.status = request.form.get('status', customer.status)
        db.session.commit()
        flash('Customer updated successfully!')
        return redirect(url_for('customer_detail', id=customer.id))
    return render_template('customer_form.html', customer=customer)

@app.route('/customer/<int:id>/interaction', methods=['POST'])
@login_required
def add_interaction(id):
    customer = Customer.query.get_or_404(id)
    interaction = Interaction(
        customer_id=customer.id,
        type=request.form.get('type'),
        notes=request.form.get('notes'),
        user_id=current_user.id
    )
    db.session.add(interaction)
    db.session.commit()
    flash('Interaction added successfully!')
    return redirect(url_for('customer_detail', id=customer.id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

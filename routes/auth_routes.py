import functools
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from database.db import query_db, execute_db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def role_required(allowed_roles):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if 'user_id' not in session:
                flash('Please log in to continue.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = session.get('user_role', 'student')
            if user_role not in allowed_roles:
                flash('You are not authorized to access this section.', 'danger')
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'staff':
                    return redirect(url_for('staff.dashboard'))
                else:
                    return redirect(url_for('student.dashboard'))
            return view(**kwargs)
        return wrapped_view
    return decorator

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        student_id = request.form.get('student_id', '').strip().upper()
        dietary_pref = request.form.get('dietary_pref', 'veg')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name or not email or not password:
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match. Please re-enter.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')

        existing_user = query_db("SELECT id FROM users WHERE email = %s OR (student_id IS NOT NULL AND student_id = %s)", (email, student_id), one=True)
        if existing_user:
            flash('An account with this email or Student ID already exists.', 'warning')
            return render_template('auth/register.html')

        # Hash password with bcrypt
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        new_id = execute_db("""
            INSERT INTO users (name, email, phone, student_id, password_hash, role, wallet_balance, dietary_pref, created_at)
            VALUES (%s, %s, %s, %s, %s, 'student', 500.00, %s, NOW())
        """, (name, email, phone, student_id if student_id else None, pw_hash, dietary_pref))

        flash('Registration successful! Welcome to Smart Canteen. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('user_role', 'student')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        login_identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not login_identifier or not password:
            flash('Please enter both Email/Student ID and Password.', 'danger')
            return render_template('auth/login.html')

        user = query_db("""
            SELECT * FROM users 
            WHERE email = %s OR student_id = %s
        """, (login_identifier.lower(), login_identifier.upper()), one=True)

        if not user:
            flash('Invalid email/student ID or password.', 'danger')
            return render_template('auth/login.html')

        # Check bcrypt hash
        try:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))
        except Exception:
            is_valid = False

        if not is_valid:
            flash('Invalid email/student ID or password.', 'danger')
            return render_template('auth/login.html')

        # Establish secure session
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']
        session['student_id'] = user.get('student_id')
        session['wallet_balance'] = float(user.get('wallet_balance', 500.0))

        flash(f"Welcome back, {user['name']}!", 'success')

        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)

        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user['role'] == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = query_db("SELECT * FROM users WHERE id = %s", (session['user_id'],), one=True)

    if request.method == 'POST':
        action = request.form.get('action', 'update_profile')

        if action == 'change_password':
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not bcrypt.checkpw(old_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('auth.profile'))

            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'warning')
                return redirect(url_for('auth.profile'))

            if new_password != confirm_password:
                flash('New password and confirmation do not match.', 'danger')
                return redirect(url_for('auth.profile'))

            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            execute_db("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, session['user_id']))
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))

        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        dietary_pref = request.form.get('dietary_pref', 'veg')
        topup_amount = float(request.form.get('topup_amount', 0) or 0)

        new_balance = float(user['wallet_balance']) + topup_amount

        execute_db("""
            UPDATE users 
            SET name = %s, phone = %s, dietary_pref = %s, wallet_balance = %s
            WHERE id = %s
        """, (name, phone, dietary_pref, new_balance, session['user_id']))

        session['user_name'] = name
        session['wallet_balance'] = new_balance

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('student/profile.html', user=user)

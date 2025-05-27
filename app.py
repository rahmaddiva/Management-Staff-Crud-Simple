from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import json
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'rahasia123'  # Ganti dengan secret key yang lebih aman

# Path untuk file JSON
KARYAWAN_JSON = 'data/karyawan.json'
USERS_JSON = 'data/users.json'

# Membuat direktori data jika belum ada
if not os.path.exists('data'):
    os.makedirs('data')

# Inisialisasi file JSON jika belum ada
def init_json_files():
    if not os.path.exists(KARYAWAN_JSON):
        with open(KARYAWAN_JSON, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(USERS_JSON):
        with open(USERS_JSON, 'w') as f:
            json.dump({
                "users": [
                    {
                        "username": "admin",
                        "email": "admin@example.com",
                        "password": "admin123"  # Dalam praktik nyata, gunakan password hashing
                    }
                ]
            }, f)

init_json_files()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Silakan login terlebih dahulu!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route untuk login
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        with open(USERS_JSON) as f:
            users = json.load(f)['users']
            
        user = next((user for user in users if user['email'] == email and user['password'] == password), None)
        
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email atau password salah!', 'error')
            
    return render_template('login.html')

# Route untuk logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout!', 'info')
    return redirect(url_for('login'))

# Route untuk dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    with open(KARYAWAN_JSON) as f:
        karyawan = json.load(f)
    return render_template('dashboard.html', karyawan=karyawan)

# Route untuk menampilkan semua karyawan
@app.route('/karyawan')
@login_required
def list_karyawan():
    with open(KARYAWAN_JSON) as f:
        karyawan = json.load(f)
    return render_template('karyawan/index.html', karyawan=karyawan)

# Route untuk menambah karyawan
@app.route('/karyawan/add', methods=['GET', 'POST'])
@login_required
def add_karyawan():
    if request.method == 'POST':
        with open(KARYAWAN_JSON) as f:
            karyawan = json.load(f)
            
        new_karyawan = {
            'id': str(len(karyawan) + 1),
            'nama': request.form['nama'],
            'jabatan': request.form['jabatan'],
            'departemen': request.form['departemen'],
            'gaji': request.form['gaji'],
            'tanggal_masuk': request.form['tanggal_masuk']
        }
        
        karyawan.append(new_karyawan)
        
        with open(KARYAWAN_JSON, 'w') as f:
            json.dump(karyawan, f, indent=4)
            
        flash('Data karyawan berhasil ditambahkan!', 'success')
        return redirect(url_for('list_karyawan'))
        
    return render_template('karyawan/add.html')

# Route untuk edit karyawan
@app.route('/karyawan/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_karyawan(id):
    with open(KARYAWAN_JSON) as f:
        karyawan = json.load(f)
    
    karyawan_data = next((k for k in karyawan if k['id'] == id), None)
    
    if request.method == 'POST':
        karyawan_data['nama'] = request.form['nama']
        karyawan_data['jabatan'] = request.form['jabatan']
        karyawan_data['departemen'] = request.form['departemen']
        karyawan_data['gaji'] = request.form['gaji']
        karyawan_data['tanggal_masuk'] = request.form['tanggal_masuk']
        
        with open(KARYAWAN_JSON, 'w') as f:
            json.dump(karyawan, f, indent=4)
            
        flash('Data karyawan berhasil diupdate!', 'success')
        return redirect(url_for('list_karyawan'))
        
    return render_template('karyawan/edit.html', karyawan=karyawan_data)

# Route untuk hapus karyawan
@app.route('/karyawan/delete/<string:id>')
@login_required
def delete_karyawan(id):
    with open(KARYAWAN_JSON) as f:
        karyawan = json.load(f)
    
    karyawan = [k for k in karyawan if k['id'] != id]
    
    with open(KARYAWAN_JSON, 'w') as f:
        json.dump(karyawan, f, indent=4)
        
    flash('Data karyawan berhasil dihapus!', 'success')
    return redirect(url_for('list_karyawan'))

if __name__ == '__main__':
    app.run(debug=True)
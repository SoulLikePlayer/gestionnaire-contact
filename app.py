from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from contextlib import contextmanager
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'database/contacts.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def validate_phone_number(country, phone):
    if country == '+1' and len(phone) != 10:
        return False, 'Le numéro de téléphone doit contenir 10 chiffres pour les États-Unis/Canada.'
    if country == '+33' and len(phone) != 9:
        return False, 'Le numéro de téléphone doit contenir 9 chiffres pour la France.'
    if country == '+44' and len(phone) != 10:
        return False, 'Le numéro de téléphone doit contenir 10 chiffres pour le Royaume-Uni.'
    if country == '+49' and len(phone) != 10:
        return False, 'Le numéro de téléphone doit contenir 10 chiffres pour l’Allemagne.'
    return True, ''

def get_paginated_contacts(page_num, limit=3, query=None):
    offset = (page_num - 1) * limit
    with get_db_connection() as conn:
        if query:
            contacts = conn.execute(
                "SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? LIMIT ? OFFSET ?", 
                ('%' + query + '%', '%' + query + '%', '%' + query + '%', limit, offset)
            ).fetchall()
            total_contacts = conn.execute(
                "SELECT COUNT(*) FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?", 
                ('%' + query + '%', '%' + query + '%', '%' + query + '%')
            ).fetchone()[0]
        else:
            contacts = conn.execute("SELECT * FROM contacts LIMIT ? OFFSET ?", (limit, offset)).fetchall()
            total_contacts = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]

    total_pages = (total_contacts + limit - 1) // limit
    return contacts, total_pages

# Fonction utilitaire pour obtenir la longueur d'une chaîne
def get_length(value):
    return len(value)

# Ajouter la fonction utilitaire à l'environnement Jinja2
app.jinja_env.globals.update(get_length=get_length)

@app.route('/')
def index():
    return redirect(url_for('paginate', page_num=1))

@app.route('/page/<int:page_num>')
def paginate(page_num):
    contacts, total_pages = get_paginated_contacts(page_num)
    return render_template('index.html', contacts=contacts, total_pages=total_pages, current_page=page_num)

@app.route('/add', methods=('GET', 'POST'))
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        country = request.form['country']
        phone = request.form['phone']
        email = request.form['email']
        category = request.form['category']

        valid, message = validate_phone_number(country, phone)
        if not valid:
            flash(message)
            return redirect(url_for('add_contact'))

        phone = country + phone

        with get_db_connection() as conn:
            conn.execute('INSERT INTO contacts (name, phone, email, category) VALUES (?, ?, ?, ?)', (name, phone, email, category))
            conn.commit()

        return redirect(url_for('index'))

    return render_template('add_contact.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_contact(id):
    with get_db_connection() as conn:
        contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (id,)).fetchone()

        if request.method == 'POST':
            name = request.form['name']
            country = request.form['country']
            phone = request.form['phone']
            email = request.form['email']
            category = request.form['category']

            valid, message = validate_phone_number(country, phone)
            if not valid:
                flash(message)
                return redirect(url_for('edit_contact', id=id))

            phone = country + phone

            conn.execute('UPDATE contacts SET name = ?, phone = ?, email = ?, category = ? WHERE id = ?', (name, phone, email, category, id))
            conn.commit()

            return redirect(url_for('index'))

    return render_template('edit_contact.html', contact=contact)

@app.route('/delete/<int:id>', methods=('POST',))
def delete_contact(id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM contacts WHERE id = ?', (id,))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/search', methods=('GET', 'POST'))
def search():
    query = request.args.get('query')
    page_num = request.args.get('page', 1, type=int)
    contacts, total_pages = get_paginated_contacts(page_num, query=query)
    return render_template('index.html', contacts=contacts, total_pages=total_pages, current_page=page_num, query=query)

if __name__ == '__main__':
    app.run(debug=True)

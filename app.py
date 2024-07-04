from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from contextlib import contextmanager

app = Flask(__name__)

DATABASE = 'database/contacts.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.route('/')
def index():
    with get_db_connection() as conn:
        contacts = conn.execute('SELECT * FROM contacts').fetchall()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=('GET', 'POST'))
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']

        with get_db_connection() as conn:
            conn.execute('INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)', (name, phone, email))
            conn.commit()

        return redirect(url_for('index'))

    return render_template('add_contact.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_contact(id):
    with get_db_connection() as conn:
        contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (id,)).fetchone()

        if request.method == 'POST':
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']

            conn.execute('UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?', (name, phone, email, id))
            conn.commit()

            return redirect(url_for('index'))

    return render_template('edit_contact.html', contact=contact)

@app.route('/delete/<int:id>', methods=('POST',))
def delete_contact(id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM contacts WHERE id = ?', (id,))
        conn.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

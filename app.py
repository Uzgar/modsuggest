from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import *

# Database configuration
db = SqliteDatabase('mods.db')

class ModSuggestion(Model):
    name = CharField()
    link = CharField()
    status = CharField()

    class Meta:
        database = db

db.connect()
db.create_tables([ModSuggestion])

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Dummy admin password hash for demo purposes
ADMIN_PASSWORD_HASH = generate_password_hash('admin_password')

@app.route('/')
def index():
    accepted_mods = ModSuggestion.select().where(ModSuggestion.status == 'accepted')
    return render_template('index.html', mods=accepted_mods)

@app.route('/suggest', methods=['GET', 'POST'])
def suggest():
    if request.method == 'POST':
        mod_name = request.form['mod_name']
        mod_link = request.form['mod_link']
        if mod_name and mod_link:
            ModSuggestion.create(name=mod_name, link=mod_link, status='pending')
            return redirect(url_for('index'))
    return render_template('suggest.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        action = request.form.get('action')
        mod_index = int(request.form.get('mod_index'))

        if action == 'accept':
            mod = ModSuggestion.select().where(ModSuggestion.status == 'pending')[mod_index]
            mod.status = 'accepted'
            mod.save()
        elif action == 'reject':
            mod = ModSuggestion.select().where(ModSuggestion.status == 'pending')[mod_index]
            mod.delete_instance()
        elif action == 'delete':
            mod = ModSuggestion.select().where(ModSuggestion.status == 'accepted')[mod_index]
            mod.delete_instance()

    accepted_mods = ModSuggestion.select().where(ModSuggestion.status == 'accepted')
    pending_mods = ModSuggestion.select().where(ModSuggestion.status == 'pending')
    return render_template('admin_dashboard.html', accepted=accepted_mods, pending=pending_mods)

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)

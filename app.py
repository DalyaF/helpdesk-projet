from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'helpdesk_secret_key'

@app.context_processor
def inject_now():
    return {'now': datetime.now()}
    
# Configuration de la base de données
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'dalosh@1D',
    'database': 'helpdesk2'
}

# Initialisation de la connexion à la base de données
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Création de la base de données et des tables si elles n'existent pas
def init_db():
    # Se connecter au serveur MySQL sans spécifier de base de données
    connection = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password']
    )
    cursor = connection.cursor()
    
    # Créer la base de données si elle n'existe pas
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
    cursor.execute(f"USE {db_config['database']}")
    
    # Créer les tables nécessaires
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            priority ENUM('Basse', 'Moyenne', 'Haute', 'Urgente') NOT NULL,
            status ENUM('Nouveau', 'En cours', 'En attente', 'Résolu', 'Fermé') NOT NULL DEFAULT 'Nouveau',
            department_id INT NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ticket_id INT NOT NULL,
            comment TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
        )
    ''')
    
    # Insérer des départements par défaut s'ils n'existent pas
    cursor.execute("SELECT COUNT(*) FROM departments")
    count = cursor.fetchone()[0]
    
    if count == 0:
        departments = ['IT', 'RH', 'Logistique']
        for dept in departments:
            cursor.execute("INSERT INTO departments (name) VALUES (%s)", (dept,))
    
    connection.commit()
    cursor.close()
    connection.close()

# Route principale - Liste des tickets
@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Récupérer tous les tickets avec le nom du département
    cursor.execute('''
        SELECT t.*, d.name as department_name 
        FROM tickets t
        JOIN departments d ON t.department_id = d.id
        ORDER BY 
            CASE 
                WHEN t.priority = 'Urgente' THEN 1
                WHEN t.priority = 'Haute' THEN 2
                WHEN t.priority = 'Moyenne' THEN 3
                WHEN t.priority = 'Basse' THEN 4
            END,
            t.created_at DESC
    ''')
    tickets = cursor.fetchall()
    
    # Récupérer tous les départements pour le formulaire
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('index.html', tickets=tickets, departments=departments)

# Route pour créer un nouveau ticket
@app.route('/tickets/create', methods=['POST'])
def create_ticket():
    title = request.form['title']
    description = request.form['description']
    priority = request.form['priority']
    department_id = request.form['department']
    
    # Validation des champs
    if not title or not description:
        flash('Tous les champs sont obligatoires', 'error')
        return redirect(url_for('index'))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Insérer le nouveau ticket
    now = datetime.now()
    cursor.execute('''
        INSERT INTO tickets (title, description, priority, department_id, created_at, updated_at, status) 
        VALUES (%s, %s, %s, %s, %s, %s, 'Nouveau')
    ''', (title, description, priority, department_id, now, now))
    
    connection.commit()
    ticket_id = cursor.lastrowid
    
    cursor.close()
    connection.close()
    
    flash('Ticket créé avec succès!', 'success')
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

# Route pour voir les détails d'un ticket
@app.route('/tickets/<int:ticket_id>')
def view_ticket(ticket_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Récupérer les informations du ticket
    cursor.execute('''
        SELECT t.*, d.name as department_name 
        FROM tickets t
        JOIN departments d ON t.department_id = d.id
        WHERE t.id = %s
    ''', (ticket_id,))
    ticket = cursor.fetchone()
    
    if not ticket:
        cursor.close()
        connection.close()
        flash('Ticket non trouvé', 'error')
        return redirect(url_for('index'))
    
    # Récupérer les commentaires associés au ticket
    cursor.execute('''
        SELECT * FROM comments
        WHERE ticket_id = %s
        ORDER BY created_at DESC
    ''', (ticket_id,))
    comments = cursor.fetchall()
    
    # Récupérer tous les départements pour le formulaire
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('view_ticket.html', ticket=ticket, comments=comments, departments=departments)

# Route pour mettre à jour le statut d'un ticket
@app.route('/tickets/<int:ticket_id>/update', methods=['POST'])
def update_ticket(ticket_id):
    status = request.form['status']
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Mettre à jour le statut du ticket
    now = datetime.now()
    cursor.execute('''
        UPDATE tickets
        SET status = %s, updated_at = %s
        WHERE id = %s
    ''', (status, now, ticket_id))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    flash('Statut du ticket mis à jour avec succès!', 'success')
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

# Route pour ajouter un commentaire à un ticket
@app.route('/tickets/<int:ticket_id>/comment', methods=['POST'])
def add_comment(ticket_id):
    comment = request.form['comment']
    
    if not comment:
        flash('Le commentaire ne peut pas être vide', 'error')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Ajouter le commentaire
    now = datetime.now()
    cursor.execute('''
        INSERT INTO comments (ticket_id, comment, created_at)
        VALUES (%s, %s, %s)
    ''', (ticket_id, comment, now))
    
    # Mettre à jour la date de modification du ticket
    cursor.execute('''
        UPDATE tickets
        SET updated_at = %s
        WHERE id = %s
    ''', (now, ticket_id))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    flash('Commentaire ajouté avec succès!', 'success')
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

# Page de recherche et filtres
@app.route('/search')
def search():
    query = request.args.get('q', '')
    department = request.args.get('department', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Construction de la requête SQL avec filtres
    sql = '''
        SELECT t.*, d.name as department_name 
        FROM tickets t
        JOIN departments d ON t.department_id = d.id
        WHERE 1=1
    '''
    params = []
    
    if query:
        sql += " AND (t.title LIKE %s OR t.description LIKE %s)"
        query_param = f"%{query}%"
        params.extend([query_param, query_param])
    
    if department:
        sql += " AND t.department_id = %s"
        params.append(department)
    
    if status:
        sql += " AND t.status = %s"
        params.append(status)
    
    if priority:
        sql += " AND t.priority = %s"
        params.append(priority)
    
    sql += " ORDER BY t.created_at DESC"
    
    cursor.execute(sql, params)
    tickets = cursor.fetchall()
    
    # Récupérer tous les départements pour le formulaire
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('search.html', 
                          tickets=tickets, 
                          departments=departments, 
                          query=query,
                          selected_department=department,
                          selected_status=status,
                          selected_priority=priority)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
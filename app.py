from flask import Flask, render_template, request , redirect ,url_for , session
import mysql.connector
import random
import os
from transformers import pipeline , AutoTokenizer , AutoModelForSeq2SeqLM
from TestHug import generate_phrases
from dotenv import dotenv_values

app = Flask(__name__)

# On Définit la secret_key pour votre application

app.secret_key = '94df62cv32ch64dg97dgef'

# Chargement des variables
secrets = dotenv_values('hf.env')
hf_email = secrets['EMAIL']
hf_pass = secrets['PASS']

# Établir une connexion à la base de données
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        port=3307,  
        user="root",
        password="example",  
        database="Turing"  
    )
    return connection


@app.route('/')
def home():
    # Rediriger vers la page de login si Utilisateur non connecté
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        # Redirection selon le rôle
        if session['role'] == 'Formateur':
            return redirect(url_for('formateur_page'))
        else:
            return redirect(url_for('quiz_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Connexion à la BDD pour vérifier l'utilisateur
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Utilisateurs WHERE NomUtilisateur = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and user['MotDePasseHash'] == password:  
            session['logged_in'] = True
            session['role'] = user['Role']
            session['username'] = user['NomUtilisateur']
            return redirect(url_for('home'))
        else:
            return 'Erreur de login'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()  # On efface toutes les données de session
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # Il faut s'assurer d'avoir un champ pour le rôle 
        # Hashage du mot de passe et insertion dans la base de données
    
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Utilisateurs (NomUtilisateur, MotDePasseHash, Role) VALUES (%s, %s, %s)',
                       (username, password, role))  # Remplacer password par password_hash si on a utilisé le hashage
        conn.commit()
        cursor.close()
        conn.close()
        return 'Inscription réussie'
    return render_template('register.html')

@app.route('/formateur', methods=['GET', 'POST'])
def formateur_page():
    if not session.get('logged_in') or session.get('role') != 'Formateur':
        return redirect(url_for('login'))

    if request.method == 'POST':
        nom_theme = request.form.get('theme_choisi').strip()
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT ThemeID FROM Themes WHERE NomTheme = %s", (nom_theme,))
        theme_row = cursor.fetchone()
        
        if theme_row:
            theme_id = theme_row[0]
        else:
            cursor.execute("INSERT INTO Themes (NomTheme) VALUES (%s)", (nom_theme,))
            theme_id = cursor.lastrowid
        
        session['theme_id'] = theme_id

        for i in range(1, 6):
            phrase_texte = request.form.get(f'phrase_{i}')
            if phrase_texte:
                # On utilise l'AuteurID '1' pour les phrases saisies par le formateur
                cursor.execute("INSERT INTO Phrases (Contenu, ThemeID, AuteurID) VALUES (%s, %s, %s)", (phrase_texte, theme_id, 1))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        session['theme_choisi'] = nom_theme
        return redirect(url_for('confirmation'))
    else:
        return render_template('Formateur.html')



@app.route('/result', methods=['POST'])
def result():
    score = 0
    total = 0
    phrases_and_answers = []

    for key, value in request.form.items():
        if key.startswith('type'):
            index = key[4:]  # On extrait le numéro d'index à partir du nom du champ
            phrase = request.form[f'phrase{index}']
            expected = value.lower()  # Conversion en minuscule pour une comparaison uniforme
            answer = request.form.get(f'answer{index}', '').lower()

            phrases_and_answers.append((phrase, expected, answer))

            if expected == answer:
                score += 1
            total += 1

    return render_template('result.html', score=score, total=total, phrases_and_answers=phrases_and_answers)







@app.route('/confirmation')
def confirmation():
    if not session.get('logged_in') or session.get('role') != 'Formateur':
        return redirect(url_for('login'))
    # Affichage de la page de confirmation avec le bouton pour générer les phrases par LLM
    return render_template('confirmation.html')


@app.route('/generate_phrases', methods=['GET', 'POST'])
def generate_phrases_route():
    if not session.get('logged_in') or session.get('role') != 'Formateur' or 'theme_id' not in session:
        return redirect(url_for('formateur_page'))
    
    theme_id = session['theme_id']  # On utilise le ThemeID de la session
    theme = session.get('theme_choisi', 'Aucun thème sélectionné')
    if theme == 'Aucun thème sélectionné':
        return redirect(url_for('formateur_page'))

    if request.method == 'POST':
        # Liste de prompts différents
        prompts = [
            f"Fais moi une phrase entre quinze et vingt-cinq mots sur {theme} ",
            f"Fais moi une nouvelle phrase sur {theme} ",
            f"Fais moi une nouvelle phrase sur {theme}",
            f"Fais moi une nouvelle phrase sur {theme} ",
            f"Fais moi une nouvelle phrase sur {theme} ",
            # On peut meme en ajouter d'autres prompts si nécessaire et les modifier pour une meilleure précision
        ]
        phrases_generees = generate_phrases(prompts)
    else:
        phrases_generees = ["Cliquez sur 'Générer 5 nouvelles phrases' pour commencer."]
    
    return render_template('generated_phrases.html', phrases=phrases_generees, theme=theme)




@app.route('/save_phrases', methods=['POST'])
def save_phrases():
    if not session.get('logged_in') or session.get('role') != 'Formateur' or 'theme_id' not in session:
        return redirect(url_for('login'))

    phrases = request.form.getlist('phrases')
    theme_id = session['theme_id']  # Utilisation du ThemeID de la session

    conn = get_db_connection()
    try:
        cursor = conn.cursor(buffered=True)
        for phrase in phrases:
            # Utilisation de l'AuteurID '2' pour les phrases générées par le bot
            cursor.execute("INSERT INTO Phrases (Contenu, ThemeID, AuteurID) VALUES (%s, %s, %s)", (phrase, theme_id, 2))
        conn.commit()
    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('confirmation'))









@app.route('/quiz', methods=['GET', 'POST'])
def quiz_page():
    if session.get('logged_in') and session.get('role') == 'Eleve':
        if request.method == 'POST':
            theme_id = request.form.get('theme')
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT PhraseID, Contenu, AuteurID FROM Phrases WHERE ThemeID = %s", (theme_id,))
            phrases = cursor.fetchall()
            cursor.close()
            conn.close()

            # Mélange aléatoire des phrases récupérées par shuffle
            random.shuffle(phrases)

            return render_template('quiz_questions.html', phrases=phrases)
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT ThemeID, NomTheme FROM Themes")
            themes = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('quiz.html', themes=themes)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
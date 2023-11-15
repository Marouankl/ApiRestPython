import MySQLdb
from _curses import *

import os
from flask import Flask, render_template, jsonify, json, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import collections
# -------------------------------------------------------------------------------------------
# |                                                                                         |
# |                          Partie 1                                                       |
# |                         Connction avec mysql                                            |
# |                                                                                         |
# |                                                                                         |
# |                                                                                         |
# -------------------------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = 'your secret key'
# MySQL configurations
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "root"
app.config['MYSQL_DB'] = "apirestpython"
mysql = MySQL(app)


@app.route('/home')
def hello_world():
    return render_template('home.html')
# -------------------------------------------------------------------------------------------
# |                                                                                         |
# |                          Partie 1                                                       |
# |                           Login                                                         |
# |                                                                                         |
# |                                                                                         |
# |                                                                                         |
# -------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------
@app.route('/login')
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (email, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            msg = 'Logged in successfully !'
            return render_template('home.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

#------
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('login'))
#----------------------------------------------------------------------------------------------------------------------------------------
#Get pokemons with fatchall
#1) GET - /api/pokemons : Récupère la liste de tous les pokémons:
@app.route('/api/pokemons', methods=['GET'])
def getPokemon():
    conn = mysql.connection.cursor()
    conn.execute(
        'SELECT p.id_Pokemon, p.name, p.size, p.weight, p.statistical, p.picture '
        'FROM pokemon p '
                )
    result = conn.fetchall()
    return render_template('pokemon.html', pokemons=result)


#----------------------------------------------------------------------------------------------------------------------------------------
# pokmen with id
#2)  GET - /api/pokemons/:id : Récupère les détails du pokémon précisé par :id
@app.route('/api/pokemons/<int:id>', methods=['GET'])
def getPokemonById(id):
    conn = mysql.connection.cursor()
    conn.execute('SELECT p.id_Pokemon, p.name, p.size, p.weight, p.statistical, p.picture, s.powers, s.description, s.precisions, s.PPMax, t.typeName '
        'FROM pokemon p '
        'INNER JOIN fastSkils fs ON p.id_Pokemon = fs.id_Pokemon '
        'JOIN skils s ON fs.id_Competance = s.id_Competance '
        'LEFT JOIN type t ON s.id_Competance = t.id_Type '
        'WHERE p.id_Pokemon=%s', [id])
    result = conn.fetchall()
    return render_template('pokemonById.html', pokemon=result)

#----------------------------------------------------------------------------------------------------------------------------------------
# 3) GET - /api/types/:id : Récupère les détails du type précisé par :id

@app.route('/api/types/<int:id>', methods=['GET'])
def getTypeById(id):
    conn = mysql.connection.cursor()
    conn.execute('SELECT * FROM type WHERE id_Type=%s', [id])
    result = conn.fetchall()
    return render_template('typeId.html', types=result)  # Use 'type' instead of 'types'

#----------------------------------------------------------------------------------------------------------------------------------------
# 3) GET - /api/types/:id : Récupère les détails du type précisé par :id

@app.route('/api/types/update/<int:id>', methods=['GET','PUT'])
def updateTypeById(id):
    conn = mysql.connection.cursor()

    if request.method == 'POST':
        typeName = request.form.get('typeName')
        sql = 'UPDATE type SET typeName=%s WHERE id_Type=%s'
        data = (typeName, id)
        conn.execute(sql, data)
        mysql.connection.commit()
        conn.close()
        flash('Type mis à jour avec succès', 'success')
        return redirect(url_for('getTypesById'))
    else:
        # Chargez les données existantes pour les afficher dans le formulaire
        sql = 'SELECT typeName FROM type WHERE id_Type = %s'
        conn.execute(sql, (id,))
        data = conn.fetchone()
        conn.close()

        if data:
            typeName = data[0]
        else:
            # Gérer le cas où l'ID n'existe pas
            flash('Type not found', 'danger')
            return redirect(url_for('getTypesById'))

        # Redirigez vers la page de gestion des compétences ou une autre vue
        return render_template('updatetype.html', id=id, typeName=typeName)


#----------------------------------------------------------------------------------------------------------------------------------------
# 4) GET - /api/abilities : Récupère la liste de toutes les compétences
@app.route('/api/abilities', methods=['GET'])
def getSkils():
    conn = mysql.connection.cursor()
    conn.execute(
        'SELECT p.id_Pokemon, p.name, s.id_Competance, s.powers, s.description, s.precisions, s.PPMax, t.typeName '
        'FROM skils s '
        'INNER JOIN type t ON s.id_Competance = t.id_Type '
        'INNER JOIN typing ty ON t.id_Type = ty.id_Type '
        'INNER JOIN pokemon p ON ty.id_Pokemon = p.id_Pokemon')
    results = conn.fetchall()
    return render_template('skils.html', skils=results)

#----------------------------------------------------------------------------------------------------------------------------------------
#5)POST - /api/pokemons : Ajout d’un pokémon
#creaded new pokemon
type = [
    {"id": 1, "name": "Plante"},
    {"id": 2, "name": "Feu"},
    {"id": 3, "name": "Water"},
    {"id": 4, "name": "Comba"},
]
@app.route('/api/pokemons/create', methods=['GEt','POST'])
def createPokemon():
    if request.method == 'POST':
        name = request.form['name']
        size = request.form['size']
        weight = request.form['weight']
        statistical = request.form['statistical']
        picture = request.form['picture']
        powers = request.form['powers']
        description = request.form['description']
        precisions = request.form['precisions']
        PPMax = request.form['PPMax']
        type_id = request.form['type']

        try:
            conn = mysql.connection.cursor()

            # Insérer les données dans la table "pokemon"
            conn.execute("INSERT INTO pokemon (name, size, weight, statistical, picture) VALUES (%s, %s, %s, %s, %s)",
                         (name, size, weight, statistical, picture))
            pokemon_id = conn.lastrowid

            # Insérer les données dans la table "skils"
            conn.execute("INSERT INTO skils (powers, description, precisions, PPMax, id_Type) VALUES (%s, %s, %s, %s, %s)",
                         (powers, description, precisions, PPMax, type_id))
            competance_id = conn.lastrowid  # Récupérer l'ID de la compétence

            # Associer le Pokémon à son type
            conn.execute("INSERT INTO typing (id_Pokemon, id_Type) VALUES (%s, %s)", (pokemon_id, type_id))

            # Associer le Pokémon à sa compétence
            conn.execute("INSERT INTO fastSkils (id_Pokemon, id_Competance) VALUES (%s, %s)", (pokemon_id, competance_id))

            mysql.connection.commit()
            conn.close()

            return redirect(url_for('getPokemon'))

        except Exception as e:
            mysql.connection.rollback()
            conn.close()
            return f'Erreur lors de la création du Pokémon : {str(e)}'
    return render_template('createPokemon.html', types=type)
#----------------------------------------------------------------------------------------------------------------------------------------
#creaded new pokemon
#6) POST - /api/types : Ajout d’un type
@app.route('/api/types/create', methods=['POST'])
def createType():
    if request.method == 'POST':
        conn = mysql.connection.cursor()
        typeName = request.form['typeName']
        sql = 'INSERT INTO type (typeName) VALUES (%s)'
        data = (typeName,)
        conn.execute(sql,data)  # Execute the SQL query
        conn.connection.commit()  # Commit the changes
        conn.close()

        # Return a JSON response to indicate success
        return render_template('pokemon.html')
    else:
        return 'error'
#----------------------------------------------------------------------------------------------------------------------------------------
#7)PUT - /api/pokemons/:id : Modification du pokémon précisé par :id
@app.route('/api/pokemons/update/<int:id>', methods=['GEt','POST' ])
def UpdateForm(id):
    if request.method == 'POST':
        conn = mysql.connection.cursor()
        name = request.form.get('name')
        size = request.form.get('size')
        weight = request.form.get('weight')
        statistical = request.form.get('statistical')
        picture = request.form.get('picture')

        sql = (
            'UPDATE pokemon '
            'SET name=%s, size=%s, weight=%s, statistical=%s, picture=%s '
            'WHERE id_Pokemon=%s'
        )
        data = (name, size, weight, statistical, picture, id)

        conn.execute(sql, data)
        mysql.connection.commit()
        conn.close()

        # Return a success message or redirect to a page
        flash('Pokemon updated successfully', 'success')
        return redirect(url_for('getPokemon', id=id))  # Add id=id to the URL parameters
    else:
        # Load the existing data to display in the form
        conn = mysql.connection.cursor()
        sql = 'SELECT name, size, weight, statistical, picture FROM pokemon WHERE id_Pokemon = %s'
        conn.execute(sql, (id,))
        data = conn.fetchone()

        if data:
            name, size, weight, statistical, picture = data  # Update variable names here
        else:
            # Handle the case where the ID doesn't exist
            flash('Pokemon not found', 'danger')
            conn.close()
            return redirect(url_for('getPokemon'))

    # Render the update form by passing the data in the context
    conn.close()
    return render_template('updatePokemon.html', id=id, name=name, size=size, weight=weight, statistical=statistical, picture=picture)
# ----------------------------------------------------------------------------------------------------------------------------------------
#8)PUT - /api/abilities/:id : Modification de la compétence précisé par :id
@app.route('/api/abilities/update/<int:id>', methods=['GEt','POST' ])
def Updateabilities(id):
    conn = mysql.connection.cursor()

    if request.method == 'POST':
        # Traitement du formulaire de mise à jour
        powers = request.form.get('powers')
        description = request.form.get('description')
        precisions = request.form.get('precisions')
        PPMax = request.form.get('PPMax')

        sql = (
            'UPDATE skils '
            'SET powers=%s, description=%s, precisions=%s, PPMax=%s '
            'WHERE id_Competance=%s'
        )
        data = (powers, description, precisions, PPMax, id)

        conn.execute(sql, data)
        conn.connection.commit()
        conn.close()

        flash('Skills updated successfully', 'success')
        return redirect(url_for('getSkils'))

    else:
        # Chargez les données existantes pour les afficher dans le formulaire
        sql = 'SELECT powers, description, precisions, PPMax FROM skils WHERE id_Competance = %s'
        conn.execute(sql, (id,))
        data = conn.fetchone()
        if data:
            powers, description, precisions, PPMax = data
        else:
            # Gérer le cas où l'ID n'existe pas
            flash('Skills not found', 'danger')
            return redirect(url_for('getSkils'))  # Redirigez vers la page de gestion des compétences ou une autre vue

        conn.close()

        # Rendre le formulaire de mise à jour en passant les données dans le contexte
        return render_template('updateAbilities.html', id=id, powers=powers, description=description, precisions=precisions, PPMax=PPMax)

# ----------------------------------------------------------------------------------------------------------------------------------------
#9. PUT - /api/type/:id : Modification du type précisé par :id
@app.route('/api/type/update/<int:id>', methods=['GEt', 'POST'])
def Updatetype(id):
    if request.method == 'POST':
        conn = mysql.connection.cursor()
        typeName = request.form.get('typeName')
        sql = (
            'UPDATE type '
            'SET typeName=%s '  
            'WHERE id_Type=%s'
        )
        data = (typeName, id)
        conn.execute(sql, data)
        mysql.connection.commit()
        conn.close()

        flash('Type updated successfully', 'success')
        return render_template('pokemon.html', id=id)
    else:
        conn = mysql.connection.cursor()
        # Load existing data to display in the form
        sql = 'SELECT typeName FROM type WHERE id_Type = %s'
        conn.execute(sql, (id,))
        data = conn.fetchone()
        conn.close()

        if data:
            typeName = data[0]  # Extract the typeName from the result
        else:
            # Handle the case where the ID doesn't exist
            flash('Type not found', 'danger')
            return redirect(url_for('getTypeById', id=id))  # Redirect to a suitable route

        # Render the update form and pass the data to the template context
        return render_template('updateType.html', id=id, typeName=typeName)
#----------------------------------------------------------------------------------------------------------------------------------------
# 10) DELETE - /api/pokemons/:id : Supression du pokémon précisé par :id
# La methode pour supprimer un pokemon avec son id
@app.route('/api/pokemons/delete/<int:id>', methods=['GET','POST'])
def deleteTask(id):
    conn = mysql.connection.cursor()  # Pour connecter à la base de données
    conn.execute('DELETE FROM pokemon WHERE id_Pokemon=%s', [id])  # Requête SQL pour supprimer un Pokémon avec un ID
    conn.connection.commit()

    # Rediriger l'utilisateur vers la page 'pokemon.html'
    return redirect(url_for('getPokemon',id=id))


#-------------------------------

@app.route('/api/pokemons/create', methods=['GET'])
def createPokemons():
    return render_template('createPokemon.html')

@app.route('/api/types/create', methods=['GET'])
def createTypes():
    return render_template('createType.html')

@app.route('/api/types/', methods=['GET'])
def getTypesById():
    conn = mysql.connection.cursor()
    conn.execute('SELECT * FROM type ')
    resultats = conn.fetchall()
    return render_template('typeId.html',types=resultats)


@app.route('/api/abilities/update', methods=['GET'])
def updateSkils():
    return render_template('updateAbilities.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

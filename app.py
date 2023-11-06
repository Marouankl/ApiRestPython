import MySQLdb
from _curses import *

import os
from flask import Flask, render_template, jsonify, json, request, redirect, url_for, session
from flask_mysqldb import MySQL
import collections

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


#------
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('login'))
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
    conn.execute('SELECT typeName FROM type WHERE id_Type=%s', [id])
    result = conn.fetchone()
    if result:
        data = {
            'id_Type': id,
            'typeName': result[0],
        }
        return jsonify(data)
    else:
        return "Type with id {} not found"

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
    data = []

    for row in results:
        skill_data = {
            'id_Pokemon': row[0],
            'name': row[1],
            'id_Competance': row[2],
            'powers': row[3],
            'description': row[4],
            'precisions': row[5],
            'PPMax': row[6],
            'type': row[7]
        }
        data.append(skill_data)

    if data:
        return jsonify(data)
    else:
        return "Compétences non trouvées"

#----------------------------------------------------------------------------------------------------------------------------------------
#5)POST - /api/pokemons : Ajout d’un pokémon
#creaded new pokemon
@app.route('/api/pokemons/create', methods=['POST'])
def createPokemon():
    if request.method == 'POST':
        conn = mysql.connection.cursor()
        name = request.form['name']
        size = request.form['size']
        weight = request.form['weight']
        statistical = request.form['statistical']
        picture = request.form['picture']
        powers = request.form['powers']
        description = request.form['description']
        precisions = request.form['precisions']
        PPMax = request.form['PPMax']
        typeName = request.form['typeName']

        sql = 'INSERT INTO pokemon (name, size, weight, statistical, picture) VALUES (%s, %s, %s, %s, %s)'
        data = (name, size, weight, statistical, picture)
        conn.execute(sql, data)

        idPokemon = conn.lastrowid

        sql = 'SELECT id_Type FROM type WHERE typeName = %s'
        conn.execute(sql, (typeName,))
        type_id = conn.fetchone()

        sql = 'INSERT INTO skils  (powers, description, precisions, PPMax, id_Type) VALUES (%s, %s, %s, %s, %s)'
        data = (powers, description, precisions, PPMax, type_id)
        conn.execute(sql, data)

        sql = 'INSERT INTO fastSkils  (id_Pokemon, id_Competence) VALUES (%s, %s)'
        data = (idPokemon, conn.lastrowid)
        conn.execute(sql, data)

        conn.connection.commit()
        return redirect(url_for('getPokemon'))
    else:
        return 'error'

#----------------------------------------------------------------------------------------------------------------------------------------
#creaded new pokemon
#6) POST - /api/types : Ajout d’un type
@app.route('/api/types/create', methods=['POST'])
def createTypes():
    if request.method == 'POST':
        conn = mysql.connection.cursor()
        sql = (
            'INSERT INTO type (id_Type,typeName, id_Competance,powers, description, precisions, PPMax,id_Pokmeon, name, size, weight, statistics, picture) '
            'SELECT t.typeName, s.powers, s.description, s.precisions, s.PPMax, p.name, p.size, p.weight, p.statistics, p.picture '
            'FROM Type t '
            'LEFT JOIN Skils s ON t.id_Type = s.id_Competance '
            'INNER JOIN FastSkils fs ON fs.id_Pokemon = t.id_Pokemon '
            'INNER JOIN Pokemon p ON p.id_Pokemon = fs.id_Pokemon'
        )
        conn.execute(sql)  # Execute the SQL query
        conn.connection.commit()  # Commit the changes
        conn.close()

        # Return a JSON response to indicate success
        return render_template('createType.html')
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
        statistics = request.form.get('statistics')
        picture = request.form.get('picture')

        sql = (
            'UPDATE pokemon '
            'SET name=%s, size=%s, weight=%s, statistics=%s, picture=%s '
            'WHERE id_Pokemon=%s'
        )
        data = (name, size, weight, statistics, picture, id)

        conn.execute(sql, data)
        conn.connection.commit()
        conn.close()

        # Return a success message or redirect to a page
        flash('Pokemon updated successfully', 'success')
        return render_template('pokemon.html', id=id)
    else:
        # You can render an update form for editing here
        return render_template('updatePokemon.html', id=id)

# ----------------------------------------------------------------------------------------------------------------------------------------
#8)PUT - /api/abilities/:id : Modification de la compétence précisé par :id
@app.route('/api/abilities/update/<int:id>', methods=['GEt','POST' ])
def Updateabilities(id):
    if request.method == 'POST':
        conn = mysql.connection.cursor()
        powers = request.form.get('powers')
        description = request.form.get('description')
        precisions = request.form.get('precisions')
        PPMax = request.form.get('	PPMax')

        sql = (
            'UPDATE skils '
            'SET powers=%s, description=%s, precisions=%s, PPMax=%s '
            'WHERE id_Competance=%s'
        )
        data = (powers, description, precisions, PPMax,  id)

        conn.execute(sql, data)
        conn.connection.commit()
        conn.close()

        # Return a success message or redirect to a page
        flash('Skils updated successfully', 'success')
        return render_template('pokemon.html', id=id)
    else:
        # You can render an update form for editing here
        return render_template('updateAbilities.html', id=id)

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
        conn.connection.commit()
        conn.close()

        # Return a success message or redirect to a page
        flash('Type updated successfully', 'success')
        return render_template('pokemon.html', id=id)
    else:
        # You can render an update form for editing here
        return render_template('updateType.html', id=id)
#----------------------------------------------------------------------------------------------------------------------------------------
# 10) DELETE - /api/pokemons/:id : Supression du pokémon précisé par :id
# La methode pour supprimer un pokemon avec son id
@app.route('/api/pokemons/delete/<int:id>', methods=['POST'])
def deleteTask(id):
    conn = mysql.connection.cursor()  # Pour connecter à la base de données
    conn.execute('DELETE FROM pokemon WHERE id_Pokemon=%s', [id])  # Requête SQL pour supprimer un Pokémon avec un ID
    conn.connection.commit()

    # Rediriger l'utilisateur vers la page 'pokemon.html'
    return redirect(url_for('getPokemon'))


#-------------------------------

@app.route('/api/pokemons/create', methods=['GET'])
def createPokemons():
    return render_template('createPokemon.html')
# @app.route('/api/pokemons/update/<id>', methods=['GET'])
# def updatePokemons(id):
#     return render_template('updatePokemon.html' , id=id)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

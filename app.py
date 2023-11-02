from _curses import *

import os
from flask import Flask, render_template, jsonify, json, request, redirect, url_for
from flask_mysqldb import MySQL
import collections

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "root"
app.config['MYSQL_DB'] = "apirestpython"
mysql = MySQL(app)


@app.route('/')
def hello_world():
    return render_template('home.html')

#
#----------------------------------------------------------------------------------------------------------------------------------------
#Get pokemons with fatchall
#1) GET - /api/pokemons : Récupère la liste de tous les pokémons:
@app.route('/api/pokemons', methods=['GET'])
def getPokemon():
    conn = mysql.connection.cursor()
    conn.execute(
        'SELECT p.id_Pokemon, p.name, p.size, p.weight, p.Statistics, p.picture '
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
    conn.execute('SELECT p.id_Pokemon, p.name, p.size, p.weight, p.Statistics, p.picture, s.powers, s.description, s.precisions, s.PPMax, t.typeName '
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
@app.route('/api/abilities')
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
# 10) DELETE - /api/pokemons/:id : Supression du pokémon précisé par :id
# La methode pour supprimer un pokemon avec son id
@app.route('/api/pokemons/delete/<int:id>', methods=['GET', 'POST'])
def deleteTask(id):
    conn = mysql.connection.cursor()  # Pour connecter à la base de données
    conn.execute('DELETE FROM pokemon WHERE id_Pokemon=%s', [id])  # Requête SQL pour supprimer un Pokémon avec un ID
    conn.connection.commit()

    # Rediriger l'utilisateur vers la page 'pokemon.html'
    return redirect(url_for('getPokemon'))

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
        Statistics = request.form['Statistics']  # Utilisez une minuscule pour le nom de la variable
        picture = request.form['picture']
        sql = "INSERT INTO pokemon (name, size, weight, Statistics, picture) VALUES (%s, %s, %s, %s, %s)"
        data = (name, size, weight, Statistics, picture)
        conn.execute(sql, data)
        # return le résultat  en forma  JSON response
        return redirect(url_for('pokemon.html'))
    else:
        return ('error')




#----------------------------------------------------------------------------------------------------------------------------------------
#creaded new pokemon
#6) POST - /api/types : Ajout d’un type
@app.route('/api/types/create', methods=['POST'])
def createTypes():
    if request.method == 'POST':
        conn = mysql.connection.cursor()
        sql = (
            'INSERT INTO type (id_Type,typeName, id_Competance,powers, description, precisions, PPMax,id_Pokmeon, name, size, weight, Statistics, picture) '
            'SELECT t.typeName, s.powers, s.description, s.precisions, s.PPMax, p.name, p.size, p.weight, p.Statistics, p.picture '
            'FROM Type t '
            'LEFT JOIN Skils s ON t.id_Type = s.id_Competance '
            'INNER JOIN FastSkils fs ON fs.id_Pokemon = t.id_Pokemon '
            'INNER JOIN Pokemon p ON p.id_Pokemon = fs.id_Pokemon'
        )
        conn.execute(sql)  # Execute the SQL query
        conn.connection.commit()  # Commit the changes
        conn.close()

        # Return a JSON response to indicate success
        return json.dumps({'message': 'Votre tache bien ajoutée !'})
    else:
        return 'error'

#----------------------------------------------------------------------------------------------------------------------------------------
@app.route('/api/pokemons/update/<int:id>', methods=['PUT' ])
def UpdateForm(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == 'PUT':
        id_Pokemon = request.form['id_Pokemon']
        name = request.form['name']
        size = request.form['size']
        weight = request.form['weight']
        statistics = request.form['statistics']
        picture = request.form['picture']
        sql = ('UPDATE pokemon '
            'SET name=%s, size=%s, weight=%s, Statistics=%s, picture=%s '
            'WHERE id_Pokemon=%s')
        data = (id_Pokemon,name, size, weight, statistics, picture, id)
        cursor.execute(sql, data)
        conn.commit()
        # return le résultat  en forma  JSON response
        return render_template('updatePokemon.html', id=id)
    else:
        return ('error')





#-------------------------------

@app.route('/api/pokemons/create', methods=['GET'])
def createPokemons():
    return render_template('createPokemon.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

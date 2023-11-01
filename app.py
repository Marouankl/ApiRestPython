from _curses import *

import os
from flask import Flask, render_template, jsonify, json, request
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
#5)POST - /api/pokemons : Ajout d’un pokémon
#creaded new pokemon
@app.route('/api/pokemons/create', methods=['POST'])
def createPokemon():
    if request.method == 'POST':
        try:
            # Établir une connexion à la base de données
            conn = mysql.connection.cursor()

            # Exécutez la requête SQL pour insérer des données dans the table 'pokemon'
            conn.execute(
                'INSERT INTO pokemon (name, size, weight, Statistics, picture, powers, description, precisions, PPMax, typeName) '
                'SELECT p.name, p.size, p.weight, p.Statistics, p.picture, s.powers, s.description, s.precisions, s.PPMax, t.typeName '
                'FROM pokemon p '
                'INNER JOIN fastSkils fs ON p.id_Pokemon = fs.id_Pokemon '
                'INNER JOIN skils s ON fs.id_Competance = s.id_Competance '
                'LEFT JOIN type t ON s.id_Competance = t.id_Type'
            )
            conn.connection.commit()
            conn.close()

            response = {'message': 'Votre Pokémon a bien été ajouté !'}
            return jsonify(response), 201  # 201 Created
        except Exception as e:
            return jsonify({'error': str(e)}), 500  # 500 Internal Server Error
    else:
        # Méthode de requête incorrecte
        return jsonify({'error': 'Méthode non autorisée'}), 405


#----------------------------------------------------------------------------------------------------------------------------------------
# 6) POST - /api/types : Ajout d’un type

#----------------------------------------------------------------------------------------------------------------------------------------
#creaded new pokemon
@app.route('/api/types/create', methods=['POST'])
def createTypes():
    conn = mysql.connection.cursor()
    if request.method == 'POST':
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
@app.route('/api/pokemons/update/<int:id>', methods=['GET'])
def showUpdateForm(id):
    conn = mysql.connection.cursor()
    conn.execute('SELECT * FROM pokemon WHERE id_Pokemon = %s', (id,))
    result = conn.fetchone()
    conn.close()

    if result:
        return render_template('update.html', id=id, pokemon=result)
    else:
        return jsonify({'message': 'Pokémon not found'})




# DELETE - /api/pokemons/:id : Supression du pokémon précisé par :id
# La methode pour supprimer un pokemon avec son id
@app.route('/api/pokemons/<id>', methods=['GET', 'POST'])
def deleteTask(id):
    conn = mysql.connection.cursor()  # Pour connceter a la base de donnée
    conn.execute('DELETE FROM pokemon WHERE id_Pokemon=%s', [id])  # requette sql pour supprimer un pokemon avec un ID
    conn.commit()
    return json.dumps({'message': 'tache supprimée !'})  # return le résultat  en forma  JSON response


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

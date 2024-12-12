from flask import Flask, Response, jsonify, request
import psycopg2

app = Flask(__name__)

hostname = "db"
port = 5432
db_name = "user"
username = "user"
password = "pass"

db_conn = psycopg2.connect(host=hostname, port=port, dbname=db_name, user=username, password=password)
db_cursor = db_conn.cursor()

# Countries

def record_into_json_country():
    global db_cursor
    rows = db_cursor.fetchall()
    records = []
    for row in rows:
        record = {}
        record["id"] = row[0]
        record["nume"] = row[1]
        record["lat"] = row[2]
        record["lon"] = row[3]
        records.append(record)
    return records

@app.route("/api/countries", methods=["POST"])
def post_countries():
    global country_counter, db_cursor, country_keys, country_types

    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"nume", "lat", "lon"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["nume"], str)) and (isinstance(data["lat"], float)) and (isinstance(data["lon"], float))):
        return Response(status=400)

    new_country = {"name" : data["nume"], "lat" : data["lat"], "long" : data["lon"]}
    
    # Verificam daca tara deja exista in db
    db_cursor.execute("SELECT * FROM TARI WHERE nume_tara = %s", (new_country["name"],))
    if db_cursor.fetchone():
        return Response(status=409)

    # Verificam in cazul in care exista deja cheia in db
    try:
        db_cursor.execute("INSERT INTO TARI (nume_tara, latitudine, longitudine) VALUES (%s, %s, %s)", (new_country["name"], new_country["lat"], new_country["long"]))
        db_cursor.execute("COMMIT")
    except:
        db_conn.rollback()
        return Response(status=409)

    # Selectam id-ul tarii adaugate
    db_cursor.execute("SELECT id_tara FROM TARI WHERE nume_tara = %s", (new_country["name"],))
    response = {"id": db_cursor.fetchone()[0]}
    return jsonify(response), 201


@app.route("/api/countries", methods=["GET"])
def get_countries():
    global db_cursor
    db_cursor.execute("SELECT * FROM TARI")
    return jsonify(record_into_json_country()), 200

@app.route("/api/countries/<int:id>", methods=["PUT"])
def put_country(id):
    global db_cursor, country_keys, country_types
    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"nume", "lat", "lon"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["nume"], str)) and (isinstance(data["lat"], float)) and (isinstance(data["lon"], float))):
        return Response(status=400)
    
    query = "SELECT * FROM TARI WHERE id_tara = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        db_cursor.execute("UPDATE TARI SET nume_tara = %s, latitudine = %s, longitudine = %s WHERE id_tara = %s", (data["nume"], data["lat"], data["lon"], id))
        db_cursor.execute("COMMIT")
        return Response(status=200)
    else:
        return Response(status=404)
 

@app.route("/api/countries/<int:id>", methods=["DELETE"])
def delete_country(id):
    global db_cursor

    query = "SELECT * FROM TARI WHERE id_tara = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        db_cursor.execute("DELETE FROM TARI WHERE id_tara = %s", (id,))
        db_cursor.execute("COMMIT")
        return Response(status=200)
    else:
        return Response(status=404)

# Cities

def record_into_json_city():
    global db_cursor
    rows = db_cursor.fetchall()
    records = []

    for row in rows:
        record = {}
        record["id"] = row[0]
        record["idTara"] = row[1]
        record["nume"] = row[2]
        record["lat"] = row[3]
        record["lon"] = row[4]
        records.append(record)

    return records

@app.route("/api/cities", methods=["POST"])
def post_cities():
    global db_cursor, city_keys, city_types

    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"idTara","nume", "lat", "lon"} != data.keys():
        return Response(status=400)
    if data["nume"] == "" or data["nume"] is None or data["lat"] == "" or data["lat"] is None or data["lon"] == "" or data["lon"] is None or data["idTara"] == "" or data["idTara"] is None:
        return Response(status=400)

    # Verificam daca tara deja exista in db
    db_cursor.execute("SELECT * FROM ORASE WHERE nume_oras = %s", (data["nume"],))
    if db_cursor.fetchone():
        return Response(status=409)

    # Verificam in cazul in care exista deja cheia in db
    try:
        db_cursor.execute("INSERT INTO ORASE (id_tara, nume_oras, latitudine, longitudine) VALUES (%s, %s, %s, %s)", (data["idTara"], data["nume"], data["lat"], data["lon"]))
        db_cursor.execute("COMMIT")
    except:
        db_conn.rollback()
        return Response(status=409)

    # Selectam id-ul tarii adaugate
    db_cursor.execute("SELECT id_tara FROM ORASE WHERE nume_oras = %s", (data["nume"],))
    response = {"id": db_cursor.fetchone()[0]}
    return jsonify(response), 201
    
@app.route("/api/cities", methods=["GET"])
def get_cities():
    global db_cursor
    db_cursor.execute("SELECT * FROM ORASE")
    return jsonify(record_into_json_city()), 200

@app.route("/api/cities/country/<int:id>", methods=["GET"])
def get_citites_in_country(id):
    global db_cursor
    query = "SELECT * FROM ORASE WHERE id_tara = CAST(%s as INT)" % id
    db_cursor.execute(query)
    return jsonify(record_into_json_city()), 200

@app.route("/api/cities/<int:id>", methods=["PUT"])
def put_city(id):
    global db_cursor

    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"id", "idTara","nume", "lat", "lon"} != data.keys():
        return Response(status=400)
    if data["nume"] == "" or data["nume"] is None or data["lat"] == "" or data["lat"] is None or data["lon"] == "" or data["lon"] is None or data["idTara"] == "" or data["idTara"] is None:
        return Response(status=400)
    if id != data["id"]:
        return Response(status=400)
    
    query = "SELECT * FROM ORASE WHERE id_oras = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        try:
            db_cursor.execute("UPDATE ORASE SET id_tara = %s, nume_oras = %s, latitudine = %s, longitudine = %s WHERE id_oras = %s", (data["idTara"], data["nume"], data["lat"], data["lon"], id))
            db_cursor.execute("COMMIT")
            return Response(status=200)
        except:
            db_conn.rollback()
            return Response(status=409)
    else:
        return Response(status=404)
    

@app.route("/api/cities/<int:id>", methods=["DELETE"])
def delete_city(id):
    global db_cursor
    query = "SELECT * FROM ORASE WHERE id_oras = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        db_cursor.execute("DELETE FROM ORASE WHERE id_oras = %s", (id,))
        db_cursor.execute("COMMIT")
        return Response(status=200)
    else:
        return Response(status=404)


    

if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
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

    # Verificam in cazul in care exista deja cheia in db
    try:
        db_cursor.execute("INSERT INTO TARI (nume_tara, latitudine, longitudine) VALUES (%s, %s, %s)", (new_country["name"], new_country["lat"], new_country["long"]))
        db_cursor.execute("COMMIT")
    except:
        db_conn.rollback()
        return Response(status=409)

    # Selectam id-ul tarii adaugate
    db_cursor.execute("SELECT id FROM TARI WHERE nume_tara = %s", (new_country["name"],))
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
    if {"id", "nume", "lat", "lon"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["nume"], str)) and (isinstance(data["lat"], float)) and
            (isinstance(data["lon"], float)) and (isinstance(data["id"], int))):
        return Response(status=400)
    if id != data["id"]:
        return Response(status=400)
    
    query = "SELECT * FROM TARI WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        try:
            db_cursor.execute("UPDATE TARI SET nume_tara = %s, latitudine = %s, longitudine = %s WHERE id_tara = %s", (data["nume"], data["lat"], data["lon"], id))
            db_cursor.execute("COMMIT")
            return Response(status=200)
        except:
            db_conn.rollback()
            return Response(status=409)
    else:
        return Response(status=404)
 

@app.route("/api/countries/<int:id>", methods=["DELETE"])
def delete_country(id):
    global db_cursor

    query = "SELECT * FROM TARI WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        db_cursor.execute("DELETE FROM TARI WHERE id = %s", (id,))
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
    if not ((isinstance(data["nume"], str)) and (isinstance(data["lat"], float)) and (isinstance(data["lon"], float)) and (isinstance(data["idTara"], int))):
        return Response(status=400)

    # Verificam in cazul in care exista deja cheia in db
    try:
        db_cursor.execute("INSERT INTO ORASE (id_tara, nume_oras, latitudine, longitudine) VALUES (%s, %s, %s, %s)", (data["idTara"], data["nume"], data["lat"], data["lon"]))
        db_cursor.execute("COMMIT")
    except:
        db_conn.rollback()
        return Response(status=409)

    # Selectam id-ul tarii adaugate
    db_cursor.execute("SELECT id FROM ORASE WHERE nume_oras = %s", (data["nume"],))
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
    if not ((isinstance(data["nume"], str)) and (isinstance(data["lat"], float)) and
            (isinstance(data["lon"], float)) and (isinstance(data["idTara"], int)) and (isinstance(data["id"], int))):
        return Response(status=400)
    if id != data["id"]:
        return Response(status=400)
    
    query = "SELECT * FROM ORASE WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        try:
            db_cursor.execute("UPDATE ORASE SET id_tara = %s, nume_oras = %s, latitudine = %s, longitudine = %s WHERE id= %s", (data["idTara"], data["nume"], data["lat"], data["lon"], id))
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
    query = "SELECT * FROM ORASE WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        db_cursor.execute("DELETE FROM ORASE WHERE id = %s", (id,))
        db_cursor.execute("COMMIT")
        return Response(status=200)
    else:
        return Response(status=404)

# Temperature

def record_into_json_temperature():
    global db_cursor
    rows = db_cursor.fetchall()
    records = []

    for row in rows:
        record = {}
        record["id"] = row[0]
        #record["idOras"] = row[1]
        record["valoare"] = row[2]
        #record["timp"] = row[3]
        records.append(record)

    return records

@app.route("/api/temperatures", methods=["POST"])
def post_temperature():
    global db_cursor
    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"idOras","valoare"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["idOras"], int)) and (isinstance(data["valoare"], float))):
        return Response(status=400)

    # Verificam in cazul in care exista deja cheia in db
    try:
        db_cursor.execute("INSERT INTO TEMPERATURI (id_oras, valoare) VALUES (%s, %s)", (data["idOras"], data["valoare"]))
        db_cursor.execute("COMMIT")
    except:
        db_conn.rollback()
        return Response(status=409)

    # Selectam id-ul tarii adaugate
    db_cursor.execute("SELECT MAX(id) FROM Temperaturi;")
    response = {"id": db_cursor.fetchone()[0]}
    return jsonify(response), 201

@app.route("/api/temperatures/<int:id>", methods=["PUT"])
def put_temp(id):
    global db_cursor

    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"id", "idOras","valoare"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["valoare"], float)) and (isinstance(data["idOras"], int)) and (isinstance(data["id"], int))):
        return Response(status=400)
    if id != data["id"]:
        return Response(status=400)
    
    query = "SELECT * FROM TEMPERATURI WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        try:
            db_cursor.execute("UPDATE TEMPERATURI SET id_oras = %s, valoare = %s WHERE id = %s", (data["idOras"], data["valoare"], id))
            db_cursor.execute("COMMIT")
            return Response(status=200)
        except:
            db_conn.rollback()
            return Response(status=409)
    else:
        return Response(status=404)

@app.route("/api/temperatures/<int:id>", methods=["DELETE"])
def delete_temp(id):
    global db_cursor
    query = "SELECT * FROM TEMPERATURI WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()
    if response:
        db_cursor.execute("DELETE FROM TEMPERATURI WHERE id = %s", (id,))
        db_cursor.execute("COMMIT")
        return Response(status=200)
    else:
        return Response(status=404)

@app.route("/api/temperatures", methods=["GET"])
def get_temperatures():
    global db_cursor
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    from_date = request.args.get("from", type=str)
    until_date = request.args.get("until", type=str)

    if lat and lon and from_date and until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.latitudine = %s AND o.longitudine = %s\
                    and t.timestamp BETWEEN TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD') AND TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (lat, lon, from_date, until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature()), 200
    elif lat and lon:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.latitudine = %s AND o.longitudine = %s" % (lat, lon)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature()), 200
    elif from_date and until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                WHERE t.timestamp BETWEEN TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD') AND TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (from_date, until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature()), 200
    elif lat:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.latitudine = %s " % lat
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature()), 200
    elif lon:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.longitudine = %s" % (lon)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature()), 200
    elif from_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                WHERE t.timestamp >= TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (from_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature()), 200
    elif until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                WHERE t.timestamp <= TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature()), 200
    else:
        db_cursor.execute("SELECT * FROM TEMPERATURI")
        return jsonify(record_into_json_temperature()), 200



if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
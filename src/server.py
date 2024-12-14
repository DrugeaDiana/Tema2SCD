from flask import Flask, Response, jsonify, request
import psycopg2
import os

'''
-------------------------------------------------------------------
INITIALIZARE BAZA DE DATE + APLICATIE
-------------------------------------------------------------------
'''

app = Flask(__name__)

# Variabilele pentru conectarea la baza de date
hostname = os.getenv("POSTGRES_HOST", "db")
port = os.getenv("POSTGRES_PORT", 5432)
db_name = os.getenv("POSTGRES_DB", "scd")
username = os.getenv("POSTGRES_USER", "user")
password = os.getenv("POSTGRES_PASSWORD", "password")

# Conectarea la baza de date
db_conn = psycopg2.connect(host=hostname, port=port, dbname=db_name, user=username, password=password)
db_cursor = db_conn.cursor()

'''
-------------------------------------------------------------------
ENDPOINT-URILE PENTRU TABELA TARI
-------------------------------------------------------------------
'''

# Transforma datele colectate de Select-ul din db in formatul JSON pentru tari
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

# Endpoint pentru adaugarea unei tari in baza de date
@app.route("/api/countries", methods=["POST"])
def post_countries():
    global db_cursor

    # Verificam daca datele trimise sunt corecte
    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"nume", "lat", "lon"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["nume"], str)) and 
            ((isinstance(data["lat"], float)) or (isinstance(data["lat"], int))) and
            ((isinstance(data["lon"], float)) or (isinstance(data["lon"], int)))):
        return Response(status=400)

    # Try-catch pentru a verifica daca exista deja tara in db
    try:
        db_cursor.execute("INSERT INTO TARI (nume_tara, latitudine, longitudine) VALUES (%s, %s, %s)", (data["nume"], data["lat"], data["lon"]))
        db_cursor.execute("COMMIT")
    except:
        db_conn.rollback()
        return Response(status=409)

    # Selectam id-ul tarii adaugate
    db_cursor.execute("SELECT id FROM TARI WHERE nume_tara = %s", (data["nume"],))
    response = {"id": db_cursor.fetchone()[0]}
    return jsonify(response), 201

# Endpoint pentru afisarea tuturor tarilor
@app.route("/api/countries", methods=["GET"])
def get_countries():
    global db_cursor
    db_cursor.execute("SELECT * FROM TARI")
    return jsonify(record_into_json_country()), 200

# Endpoint pentru modificarea unei tari cu id-ul dat
@app.route("/api/countries/<int:id>", methods=["PUT"])
def put_country(id):
    global db_cursor

    data = request.get_json()
    # Verificam daca datele trimise sunt corecte
    if not data:
        return Response(status=400)
    if {"id", "nume", "lat", "lon"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["nume"], str)) and 
            ((isinstance(data["lat"], float)) or (isinstance(data["lat"], int))) and
            ((isinstance(data["lon"], float)) or (isinstance(data["lon"], int))) and
            (isinstance(data["id"], int))):
        return Response(status=400)
    if id != data["id"]:
        return Response(status=400)
    
    # Verificam daca tara cu id-ul dat exista in db
    query = "SELECT * FROM TARI WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()

    # Daca exista, incercam sa modificam datele -> daca avem conflict, dam rollback si trimitem 409
    # Daca nu exista -> 404
    if response:
        try:
            db_cursor.execute("UPDATE TARI SET nume_tara = %s, latitudine = %s, longitudine = %s \
                              WHERE id = %s", (data["nume"], data["lat"], data["lon"], id))
            db_cursor.execute("COMMIT")
            return Response(status=200)
        except:
            db_conn.rollback()
            return Response(status=409)
    else:
        return Response(status=404)
 
# Endpoint pentru stergerea unei tari cu id-ul dat
@app.route("/api/countries/<int:id>", methods=["DELETE"])
def delete_country(id):
    global db_cursor

    # Verificam daca tara cu id-ul dat exista in db
    query = "SELECT * FROM TARI WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()

    # Daca exista, stergem intrarea. Daca nu, trimitem 404
    if response:
        try:
            db_cursor.execute("DELETE FROM TARI WHERE id = %s", (id,))
            db_cursor.execute("COMMIT")
            return Response(status=200)
        except:
            db_conn.rollback()
            return Response(status=400)
    else:
        return Response(status=404)

'''
-------------------------------------------------------------------
ENDPOINT-URILE PENTRU TABELA ORASE
-------------------------------------------------------------------
'''

# Transforma datele colectate de Select-ul din db in formatul JSON pentru orase
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

# Endpoint pentru adaugarea unui oras in baza de date
@app.route("/api/cities", methods=["POST"])
def post_cities():
    global db_cursor, city_keys, city_types

    # Verificam daca datele trimise sunt corecte
    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"idTara","nume", "lat", "lon"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["nume"], str)) and 
            ((isinstance(data["lat"], float)) or (isinstance(data["lat"], int))) and
            ((isinstance(data["lon"], float)) or (isinstance(data["lon"], int))) and
            (isinstance(data["idTara"], int))):
        return Response(status=400)

    # Verificam in cazul in care exista deja cheia in db
    try:
        db_cursor.execute("INSERT INTO ORASE (id_tara, nume_oras, latitudine, longitudine) VALUES (%s, %s, %s, %s)", (data["idTara"], data["nume"], data["lat"], data["lon"]))
        db_cursor.execute("COMMIT")
    except psycopg2.errors.UniqueViolation:
        db_conn.rollback()
        return Response(status=409)
    except psycopg2.errors.ForeignKeyViolation:
        db_conn.rollback()
        return Response(status=404)

    # Selectam id-ul orasului adaugat
    db_cursor.execute("SELECT id FROM ORASE WHERE nume_oras = %s", (data["nume"],))
    response = {"id": db_cursor.fetchone()[0]}
    return jsonify(response), 201

# Endpoint pentru afisarea tuturor oraselor
@app.route("/api/cities", methods=["GET"])
def get_cities():
    global db_cursor
    db_cursor.execute("SELECT * FROM ORASE")
    return jsonify(record_into_json_city()), 200

# Endpoint pentru afisarea unui oras cu id-ul dat
@app.route("/api/cities/country/<int:id>", methods=["GET"])
def get_citites_in_country(id):
    global db_cursor
    query = "SELECT * FROM ORASE WHERE id_tara = CAST(%s as INT)" % id
    db_cursor.execute(query)
    return jsonify(record_into_json_city()), 200

# Endpoint pentru modificarea unui oras cu id-ul dat
@app.route("/api/cities/<int:id>", methods=["PUT"])
def put_city(id):
    global db_cursor

    # Verificam daca datele trimise sunt corecte
    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"id", "idTara","nume", "lat", "lon"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["nume"], str)) and 
            ((isinstance(data["lat"], float)) or (isinstance(data["lat"], int))) and
            ((isinstance(data["lon"], float)) or (isinstance(data["lon"], int))) and
            (isinstance(data["idTara"], int)) and (isinstance(data["id"], int))):
        return Response(status=400)
    if id != data["id"]:
        return Response(status=400)
    
    # Verificam daca exista orasul cu id-ul dat in db
    query = "SELECT * FROM ORASE WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()

    # Daca exista, incercam sa modificam datele -> daca avem conflict, dam rollback si trimitem 409
    # Daca nu exista -> 404
    if response:
        try:
            db_cursor.execute("UPDATE ORASE SET id_tara = %s, nume_oras = %s, latitudine = %s, longitudine = %s WHERE id= %s", (data["idTara"], data["nume"], data["lat"], data["lon"], id))
            db_cursor.execute("COMMIT")
            return Response(status=200)
        except psycopg2.errors.UniqueViolation:
            db_conn.rollback()
            return Response(status=409)
        except psycopg2.errors.ForeignKeyViolation:
            db_conn.rollback()
            return Response(status=404)
    else:
        return Response(status=404)
    
# Endpoint pentru stergerea unui oras cu id-ul dat
@app.route("/api/cities/<int:id>", methods=["DELETE"])
def delete_city(id):
    global db_cursor

    # Verificam daca orasul cu id-ul dat exista in db
    query = "SELECT * FROM ORASE WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()

    # Daca exista, stergem intrarea. Daca nu, trimitem 404
    if response:
        try:
            db_cursor.execute("DELETE FROM ORASE WHERE id = %s", (id,))
            db_cursor.execute("COMMIT")
            return Response(status=200)
        except:
            db_conn.rollback()
            return Response(status=400)
    else:
        return Response(status=404)

'''
-------------------------------------------------------------------
ENDPOINT-URILE PENTRU TABELA TEMPERATURI
-------------------------------------------------------------------
'''

# Transforma datele colectate de Select-ul din db in formatul JSON pentru temperaturi
# date = 0 -> fara timestamp
# date = 1 -> cu timestamp
def record_into_json_temperature(date):
    global db_cursor
    rows = db_cursor.fetchall()

    records = []
    for row in rows:
        record = {}
        record["id"] = row[0]
        record["valoare"] = row[2]
        if date == 1:
            record["timestamp"] = row[3]
        records.append(record)

    return records

# Endpoint pentru adaugarea unei temperaturi in baza de date
@app.route("/api/temperatures", methods=["POST"])
def post_temperature():
    global db_cursor

    # Verificam daca datele trimise sunt corecte
    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"idOras","valoare"} != data.keys():
        return Response(status=400)
    if not ((isinstance(data["idOras"], int)) and
            ((isinstance(data["valoare"], float)) or (isinstance(data["valoare"], int)))):
        return Response(status=400)

    # Verificam in cazul in care exista deja cheia in db
    try:
        db_cursor.execute("INSERT INTO TEMPERATURI (id_oras, valoare) VALUES (%s, %s)", (data["idOras"], data["valoare"]))
        db_cursor.execute("COMMIT")
    except psycopg2.errors.UniqueViolation:
        db_conn.rollback()
        return Response(status=409)
    except psycopg2.errors.ForeignKeyViolation:
        db_conn.rollback()
        return Response(status=404)

    # Selectam id-ul temperaturii adaugate
    db_cursor.execute("SELECT MAX(id) FROM Temperaturi;")
    response = {"id": db_cursor.fetchone()[0]}
    return jsonify(response), 201

# Endpoint pentru modificarea unei temperaturi cu id-ul dat
@app.route("/api/temperatures/<int:id>", methods=["PUT"])
def put_temp(id):
    global db_cursor

    # Verificam daca datele trimise sunt corecte
    data = request.get_json()
    if not data:
        return Response(status=400)
    if {"id", "idOras","valoare"} != data.keys():
        return Response(status=400)
    if not (((isinstance(data["valoare"], float)) or (isinstance(data["valoare"], int)))
            and (isinstance(data["idOras"], int)) and (isinstance(data["id"], int))):
        return Response(status=400)
    if id != data["id"]:
        return Response(status=400)
    
    # Verificam daca exista temperatura cu id-ul dat in db
    query = "SELECT * FROM TEMPERATURI WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)
    response = db_cursor.fetchone()

    # Daca exista, incercam sa modificam datele -> daca avem conflict, dam rollback si trimitem 409
    # Daca nu exista -> 404
    if response:
        try:
            db_cursor.execute("UPDATE TEMPERATURI SET id_oras = %s, valoare = %s WHERE id = %s", (data["idOras"], data["valoare"], id))
            db_cursor.execute("COMMIT")
            return Response(status=200)
        except psycopg2.errors.UniqueViolation:
            db_conn.rollback()
            return Response(status=409)
        except psycopg2.errors.ForeignKeyViolation:
            db_conn.rollback()
            return Response(status=404)
    else:
        return Response(status=404)

# Endpoint pentru stergerea unei temperaturi cu id-ul dat
@app.route("/api/temperatures/<int:id>", methods=["DELETE"])
def delete_temp(id):
    global db_cursor

    # Verificam daca temperatura cu id-ul dat exista in db
    query = "SELECT * FROM TEMPERATURI WHERE id = CAST(%s as INT)" % id
    db_cursor.execute(query)

    # Daca exista, stergem intrarea. Daca nu, trimitem 404
    response = db_cursor.fetchone()
    if response:
        try:
            db_cursor.execute("DELETE FROM TEMPERATURI WHERE id = %s", (id,))
            db_cursor.execute("COMMIT")
            return Response(status=200)
        except:
            db_conn.rollback()
            return Response(status=400)
    else:
        return Response(status=404)

# Endpoint pentru afisarea temperaturilor in functie de parametrii dati
# Pentru ruta asta nu trebuie sa afisam timestamp-ul din baza de date -> date = 0
@app.route("/api/temperatures", methods=["GET"])
def get_temperatures():
    global db_cursor

    # Extragerea parametrilor din request
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    from_date = request.args.get("from", type=str)
    until_date = request.args.get("until", type=str)

    # Verificam daca exista parametrii in request si construim query-ul in functie de ce exista
    if lat and lon and from_date and until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.latitudine = %s AND o.longitudine = %s\
                    and t.timestamp BETWEEN TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD') AND TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (lat, lon, from_date, until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(0)), 200

    elif lat and lon:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.latitudine = %s AND o.longitudine = %s" % (lat, lon)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(0)), 200

    elif from_date and until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                WHERE t.timestamp BETWEEN TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD') AND TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (from_date, until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(0)), 200

    elif lat:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.latitudine = %s " % lat
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(0)), 200

    elif lon:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.longitudine = %s" % (lon)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(0)), 200

    elif from_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                WHERE t.timestamp >= TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (from_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(0)), 200

    elif until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t\
                WHERE t.timestamp <= TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(0)), 200

    else:
        db_cursor.execute("SELECT * FROM TEMPERATURI")
        return jsonify(record_into_json_temperature(0)), 200

# Endpoint pentru afisarea temperaturilor in functie de oras si parametrii dati
# Pentru ruta asta trebuie sa afisam timestamp-ul din baza de date -> date = 1
@app.route("/api/temperatures/cities/<int:id>", methods=["GET"])
def get_temperatures_city(id):
    global db_cursor

    # Extragerea parametrilor din request
    from_date = request.args.get("from", type=str)
    until_date = request.args.get("until", type=str)

    # Verificam daca exista parametrii in request si construim query-ul in functie de ce exista
    if from_date and until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                WHERE t.id_oras = %s AND t.timestamp BETWEEN TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD') \
                    AND TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (id, from_date, until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(1)), 200

    elif from_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                WHERE t.id_oras = %s AND t.timestamp >= TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (id, from_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(1)), 200

    elif until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                WHERE t.id_oras = %s AND t.timestamp <= TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (id, until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(1)), 200

    else:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                WHERE t.id_oras = %s" % id
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(1)), 200

# Endpoint pentru afisarea temperaturilor in functie de tara si parametrii dati
# Pentru ruta asta trebuie sa afisam timestamp-ul din baza de date -> date = 1
@app.route("/api/temperatures/countries/<int:id>", methods=["GET"])
def get_temperature_country(id):
    global db_cursor

    # Extragerea parametrilor din request
    from_date = request.args.get("from", type=str)
    until_date = request.args.get("until", type=str)

    # Verificam daca exista parametrii in request si construim query-ul in functie de ce exista
    if from_date and until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.id_tara = %s AND t.timestamp BETWEEN TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD') \
                    AND TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (id, from_date, until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(1)), 200

    elif from_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.id_tara = %s AND t.timestamp >= TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (id, from_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(1)), 200

    elif until_date:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.id_tara = %s AND t.timestamp <= TO_DATE(CAST(%s AS varchar), 'YYYY-MM-DD')" % (id, until_date)
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(1)), 200

    else:
        query = "SELECT t.id, t.id_oras, t.valoare, TO_CHAR(t.timestamp, 'YYYY-MM-DD') \
                FROM TEMPERATURI t \
                    INNER JOIN ORASE o ON t.id_oras = o.id\
                WHERE o.id_tara = %s" % id
        db_cursor.execute(query)
        return jsonify(record_into_json_temperature(1)), 200

if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
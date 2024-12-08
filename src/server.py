from flask import Flask, Response, jsonify, request
import psycopg2

app = Flask(__name__)
countries_list = [] # debuging for now
country_counter = 0
cities_list = [] # debuging for now
cities_counter = 0
temperature_list = [] # debuging for now
temperature_counter = 0

hostname = "db"
port = 5432
db_name = "user"
username = "user"
password = "pass"

db_conn = psycopg2.connect(host=hostname, port=port, dbname=db_name, user=username, password=password)
db_cursor = db_conn.cursor()
# Countries

def record_into_json():
    global db_cursor
    rows = db_cursor.fetchall()
    records = []
    for row in rows:
        record = {}
        for i, column in enumerate(db_cursor.description):
            record[column.name] = row[i]
        records.append(record)
    return records

@app.route("/api/countries", methods=["POST"])
def post_countries():
    global countries_list, country_counter
    data = request.get_json()
    if data:
        if data["nume"]:
            if data["lat"] and data["lon"]:
                new_country = {"id" : country_counter, "name" : data["nume"], "lat" : data["lat"], "long" : data["lon"]}
                db_cursor.execute("SELECT * FROM TARI WHERE id_tara = CAST(%s as INT)", (new_country["id"],))
                response = db_cursor.fetchone()
                if response:
                    country_counter += 1
                    return Response(status=409)
                country_counter += 1
                db_cursor.execute("INSERT INTO TARI (id_tara, nume_tara, latitudine, longitudine) VALUES (%s, %s, %s, %s)", (new_country["id"], new_country["name"], new_country["lat"], new_country["long"]))
                db_cursor.execute("COMMIT")
                db_cursor.execute("SELECT id_tara FROM TARI WHERE nume_tara = %s", (new_country["name"],))
                return Response(status=201, response=str(db_cursor.fetchone()[0]))
            else:
                return Response(status=400)
        else:
            return Response(status=400)
    else:
        return Response(status=400)
    
    # if country exists already -> 409

@app.route("/api/countries", methods=["GET"])
def get_countries():
    global db_cursor
    db_cursor.execute("SELECT * FROM TARI")
    return jsonify(record_into_json()), 200



if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
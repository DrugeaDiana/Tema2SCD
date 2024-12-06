from flask import Flask, Response, jsonify, request
import psycopg2

app = Flask(__name__)
countries_list = [] # debuging for now
country_counter = 0
cities_list = [] # debuging for now
cities_counter = 0
temperature_list = [] # debuging for now
temperature_counter = 0

# Countries

@app.route("/api/countries", methods=["POST"])
def post_countries():
    global countries_list, country_counter
    data = request.get_json()
    if data:
        if data["name"]:
            if data["lat"] and data["long"]:
                
            return Response(status=201, response=new_country["id"])
        else:
            return Response(status=400)
    else:
        return Response(status=400)
    
    # if country exists already -> 409

@app.route("/api/countries", methods=["GET"])
def get_countries():
    global countries_list
    return jsonify(countries_list), 200

@app.route("/api/countries/<int:id>", methods=["PUT"])
def put_country(id):
    global countries_list
    data = request.get_json()
    if data:
        if data["name"]:
            found = 0
            for country in countries_list:
                if country["id"] == id:
                    country["name"] = data["name"]
                    found = 1
            if found == 0:
                return Response(status= 404)
        else:
            return Response(status = 400)
    else:
        return Response(status= 400)
    return Response(status = 200)

@app.route("/api/countries/<int:id>", methods=["DELETE"])
def delete_country(id):
    global countries_list
    # 400 -> nu da datele bune
    for country in countries_list:
        if country["id"] == id:
            countries_list.remove(country)
            return Response(status= 200)
    return Response(status= 404)

# Cities
@app.route("/api/cities", methods=["POST"])
def post_cities():
    global cities_list, cities_counter
    data = request.get_json()
    if data:
        if data["name"]:
            for city in cities_list:
                if city["name"] == data["name"]:
                    return Response(status=409)
            new_city = {"id" : cities_counter, "name" : data["name"]}
            cities_list.append(new_city)
            cities_counter = cities_counter + 1
            return Response(status=201, response=new_city["id"])
        else:
            return Response(status=400)
    else:
        return Response(status=404)

@app.route("/api/cities", methods=["GET"])
def get_cities():
    global cities_list
    return jsonify(cities_list), 200

@app.route("/api/cities/<int:id>", methods=["PUT"])
def put_city(id):
    global cities_list
    data = request.get_json()
    if data:
        if data["name"]:
            found = 0
            for city in cities_list:
                if city["id"] == id:
                    city["name"] = data["name"]
                    found = 1
            if found == 0:
                return Response(status= 404)
        else:
            return Response(status = 400)
    else:
        return Response(status= 400)
    return Response(status = 200)

@app.route("/api/cities/<int:id>", methods=["DELETE"])
def delete_city(id):
    global cities_list
    for city in cities_list:
        if city["id"] == id:
            cities_list.remove(city)
            return Response(status= 200)
    return Response(status= 404)

# Temperature
@app.route("/api/temperature", methods=["POST"])
def post_temperature():
    global temperature_list, temperature_counter
    data = request.get_json()
    if data:
        if data["value"] and data["city_id"]:
            new_temperature = {"id" : temperature_counter, "value" : data["value"], "city_id" : data["city_id"]}
            temperature_list.append(new_temperature)
            temperature_counter = temperature_counter + 1
            return Response(status=201, response=new_temperature["id"])
        else:
            return Response(status=400)
    else:
        return Response(status=400)

@app.route("/api/temperature", methods=["GET"])
def get_temperature():
    global temperature_list
    lat = request.args.get('lat', 'type=float')
    long = request.args.get('long', 'type=float')
    start_date = request.args.get('from', 'type=date')
    end_date = request.args.get('until', 'type=date')

    return jsonify(temperature_list), 200

@app.route("/api/temperature/cities/<int:id_oras>", methods=["GET"])
def get_temperature_city(id_oras):
    global temperature_list
    start_date = request.args.get('from', 'type=date')
    end_date = request.args.get('until', 'type=date')

@app.route("/api/temperature/countries/<int:id_tara>", methods=["GET"])
def get_temperature_country(id_tara):
    global temperature_list
    start_date = request.args.get('from', 'type=date')
    end_date = request.args.get('until', 'type=date')

@app.route("/api/temperature/<int:id>", methods=["PUT"])
def put_temperature(id):
    global temperature_list
    data = request.get_json()
    if data:
        if data["value"]:
            found = 0
            for temperature in temperature_list:
                if temperature["id"] == id:
                    temperature["value"] = data["value"]
                    found = 1
            if found == 0:
                return Response(status= 404)
        else:
            return Response(status = 400)
    else:
        return Response(status= 400)
    return Response(status = 200)

@app.route("/api/temperature/<int:id>", methods=["DELETE"])
def delete_temperature(id):
    global temperature_list
    for temperature in temperature_list:
        if temperature["id"] == id:
            temperature_list.remove(temperature)
            return Response(status= 200)
    return Response(status= 404)

if __name__ == "__main__":
    app.run()
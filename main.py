from google.cloud import datastore
from flask import Flask, request
import json
import constants

app = Flask(__name__)
client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /lodgings to use this API"\

@app.route('/lodgings', methods=['POST','GET'])
def lodgings_get_post():
    if request.method == 'POST':
        content = request.get_json()
        new_lodging = datastore.entity.Entity(key=client.key(constants.lodgings))
        new_lodging.update({"name": content["name"], "description": content["description"],
          "price": content["price"]})
        client.put(new_lodging)
        return str(new_lodging.key.id)
    elif request.method == 'GET':
        query = client.query(kind=constants.lodgings)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        return json.dumps(results)
    else:
        return 'Method not recogonized'

@app.route('/lodgings/<id>', methods=['PUT','DELETE'])
def lodgings_put_delete(id):
    if request.method == 'PUT':
        content = request.get_json()
        lodging_key = client.key(constants.lodgings, int(id))
        lodging = client.get(key=lodging_key)
        lodging.update({"name": content["name"], "description": content["description"],
          "price": content["price"]})
        client.put(lodging)
        return ('',200)
    elif request.method == 'DELETE':
        key = client.key(constants.lodgings, int(id))
        client.delete(key)
        return ('',200)
    else:
        return 'Method not recogonized'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
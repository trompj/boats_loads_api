from google.cloud import datastore
from flask import Flask, request, jsonify
import json
import constants

app = Flask(__name__)
client = datastore.Client()

host = "http://localhost:8080/"
# host = https://appdomain/

@app.route('/')
def index():
    return "Please navigate to /slips or /boats to use this API"

@app.route('/boats', methods={'GET', 'POST'})
def boat_get_add():
    # Add a boat with provided values in JSON
    if request.method == 'POST':
        content = request.get_json()

        # Check that all three required JSON attributes are present
        if all([field in content.keys() for field in ['name', 'type', 'length']]):
            # Create a boat entity with given values
            new_boat = datastore.entity.Entity(key=client.key(constants.boat))
            new_boat.update({"name": content["name"], "type": content["type"],
                             "length": content["length"]})

            # Send created boat to datastore
            client.put(new_boat)

            # Set response
            response = content
            response.update(id=new_boat.id)

            live_link = host + "boats/" + str(new_boat.id)
            response.update(self=live_link)

            return response, 201

        else:
            return jsonify(Error="The request object is missing at least one of the required attributes"), 400

    # Get all boats and output
    elif request.method == 'GET':
        query = client.query(kind=constants.boat)
        results = list(query.fetch())

        result_list = []
        for e in results:
            dict_result = dict(e)

            entity_dict = {}

            entity_dict.update(id=e.key.id)
            entity_dict.update(name=dict_result.get("name"))
            entity_dict.update(type=dict_result.get("type"))
            entity_dict.update(length=dict_result.get("length"))

            live_link = host + "boats/" + str(e.key.id)
            entity_dict.update(self=live_link)

            result_list.append(entity_dict)
        return jsonify(result_list), 200

    # Incorrect request found
    else:
        return jsonify(Error='Method not accepted')


@app.route('/boats/<id>', methods={'GET', 'PATCH', 'DELETE'})
def boat_get_delete(id):
    # Create key based on ID for boat
    key = client.key(constants.boat, int(id))

    # Find boat with created key
    if request.method == 'GET':
        # Create query
        query = client.query(kind=constants.boat)
        query.key_filter(key, '=')

        # Return found result
        result = list(query.fetch())

        # If an entity is found, return it
        if len(result) == 1:

            dict_result = dict(result[0])

            # Set response
            response = {}
            response.update(id=id)
            response.update(name=dict_result.get("name"))
            response.update(type=dict_result.get("type"))
            response.update(length=dict_result.get("length"))

            live_link = host + "boats/" + str(id)
            response.update(self=live_link)

            return response, 200

        # No entity found, return not found
        else:
            return jsonify(Error="No boat with this boat_id exists"), 404

    # Update boat information based on created key
    elif request.method == 'PATCH':
        content = request.get_json()

        if len(content) == 3:
            # Get boat based on key and update values
            boat = client.get(key=key)

            # If the boat is not found, return 404
            if boat == None:
                return jsonify(Error="No boat with this boat_id exists"), 404

            # Loop through fields that were updated in JSON and update on boat
            for field in content:
                boat.update({field: content[field]})

            client.put(boat)

            response = {}
            response.update(id=boat.id)
            response.update(name=boat.get("name"))
            response.update(type=boat.get("type"))
            response.update(length=boat.get("length"))

            live_link = host + "boats/" + str(id)
            response.update(self=live_link)

            return response, 200

        else:
            return jsonify(Error="The request object is missing at least one of the required attributes"), 400

    # Delete a boat based on created key
    elif request.method == 'DELETE':
        # Get boat based on key and update values
        boat = client.get(key=key)

        # If boat with ID is found, remove it and check if it exists at a slip as current_boat
        # Set to current_boat to null if found
        if boat != None:

            # Search for slip that has current_boat with the ID of deleted boat
            slip_query = client.query(kind=constants.slip)
            slip_query.add_filter('current_boat', '=', boat.id)

            slip_result = list(slip_query.fetch())

            # If a slip is found with query, remove the boat being deleted
            if len(slip_result):
                slip = slip_result[0]

                # Update boat in slip to None
                slip.update(current_boat=None)
                client.put(slip)

            client.delete(key)

            return '', 204
        # Boat with ID is not found, return error and 404
        else:
            return jsonify(Error="No boat with this boat_id exists"), 404

    # Incorrect request found
    else:
        return jsonify(Error='Method not accepted')


@app.route('/slips', methods={'GET', 'POST'})
def slips_get_add():
    # Add a slip with provided values in JSON
    if request.method == 'POST':
        content = request.get_json()

        # Check for correct content, if does not exist, throw error and 400
        if len(content) != 1:
            return jsonify(Error="The request object is missing the required number"), 400
        # Correct content received
        else:
            # Create a slip entity with given value and set current_boat to None/null
            new_slip = datastore.entity.Entity(key=client.key(constants.slip))
            new_slip.update({"number": content["number"]})

            # Send created slip to datastore
            client.put(new_slip)

            response = {}
            response.update(id=new_slip.id)
            response.update(number=new_slip.get("number"))
            response.update(current_boat=None)

            live_link = host + "slips/" + str(new_slip.id)
            response.update(self=live_link)

            return response, 201

    # Get all slips and output
    elif request.method == 'GET':
        query = client.query(kind=constants.slip)
        results = list(query.fetch())

        result_list = []
        for e in results:
            dict_result = dict(e)

            entity_dict = {}

            entity_dict.update(id=e.key.id)
            entity_dict.update(number=dict_result.get("number"))
            entity_dict.update(current_boat=dict_result.get("current_boat"))

            live_link = host + "slips/" + str(e.key.id)
            entity_dict.update(self=live_link)

            result_list.append(entity_dict)
        return jsonify(result_list), 200

    # Incorrect request found
    else:
        return jsonify(Error='Method not accepted')


@app.route('/slips/<id>', methods={'GET', 'DELETE'})
def slip_get_delete(id):
    # Create key based on ID for slip
    key = client.key(constants.slip, int(id))

    if request.method == 'GET':
        # Create query
        query = client.query(kind=constants.slip)
        query.key_filter(key, '=')

        # Return found result
        result = list(query.fetch())

        # If an entity is found, return it
        if len(result) == 1:

            dict_result = dict(result[0])

            # Set response
            response = {}
            response.update(id=id)
            response.update(number=dict_result.get("number"))
            response.update(current_boat=dict_result.get("current_boat"))

            live_link = host + "slips/" + str(id)
            response.update(self=live_link)

            return response, 200
        # If no slip was found, return error and 404
        else:
            return jsonify(Error="No slip with this slip_id exists"), 404

    # Delete a slip based on ID provided
    elif request.method == 'DELETE':
        # Get slip based on key and update values
        slip = client.get(key=key)

        # If boat with ID is found, remove it
        if slip != None:
            client.delete(key)
            return '', 204
        # Slip with ID is not found, return error and 404
        else:
            return jsonify(Error="No slip with this slip_id exists"), 404


@app.route('/slips/<slip_id>/<boat_id>', methods={'PUT', 'DELETE'})
def boat_arrive_slip(slip_id, boat_id):
    # Create key based on ID for slip
    slip_key = client.key(constants.slip, int(slip_id))
    # Create key based on ID for boat
    boat_key = client.key(constants.boat, int(boat_id))

    # Create slip query
    query = client.query(kind=constants.slip)
    query.key_filter(slip_key, '=')

    # Return found result
    slip_result = list(query.fetch())

    # Create boat query
    query = client.query(kind=constants.boat)
    query.key_filter(boat_key, '=')

    # Return found result
    boat_result = list(query.fetch())

    # Sets boat to slip
    if request.method == 'PUT':
        # If either a boat or a slip are not found, return error and 404
        if len(slip_result) == 0 or len(boat_result) == 0:
            return jsonify(Error="The specified boat and/or slip don’t exist"), 404

        # Sets slip with the boat
        else:
            slip = slip_result[0]
            boat = boat_result[0]

            # If the slip is not empty, return 403 and error
            if slip.get("current_boat") != None:
                return jsonify(Error="The slip is not empty"), 403
            # If the slip is empty, set boat to slip and return 204
            else:
                slip.update(current_boat=int(boat_id))

                client.put(slip)

                return '', 204

    # Removes boat from slip
    elif request.method == 'DELETE':

        # If slip or boat are found, attempt to remove boat from slip
        if len(slip_result) != 0 and len(boat_result) != 0:
            slip = slip_result[0]
            boat = boat_result[0]

            # If the slip does not match the boat_id, then return 404 and error
            if slip.get("current_boat") != int(boat_id):
                return jsonify(Error="No boat with this boat_id is at the slip with this slip_id"), 404

            # Matches ID, so update slips boat to None and return 204
            else:
                slip.update(current_boat=None)
                client.put(slip)
                return '', 204

        # Return 404 and error as boat could not be removed from slip
        else:
            return jsonify(Error="No boat with this boat_id is at the slip with this slip_id"), 404

    # Method not found
    else:
        return jsonify(Error='Method not accepted')




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
# Justin Tromp
# 04/16/2020
# Boat/Load API: Allows users to access boat/load data and manipulate data in a RESTful fashion. User may create a boat,
# create a load, add a load to a boat, and delete/view them respectively.

from google.cloud import datastore
from flask import Flask, request, jsonify
import constants

app = Flask(__name__)
client = datastore.Client()


@app.route('/')
def index():
    return "Please navigate to /loads or /boats to use this API"


# Get all boats and add a boat
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
                             "length": content["length"], "loads": []})

            # Send created boat to datastore
            client.put(new_boat)

            live_link = request.base_url + "boats/" + str(new_boat.id)
            # Set response
            response = {
                'id': new_boat.id,
                'name': new_boat.get("name"),
                'type': new_boat.get("type"),
                'length': new_boat.get("length"),
                'loads': new_boat.get("loads"),
                'self': live_link
            }

            return jsonify(response), 201

        else:
            return jsonify(Error="The request object is missing at least one of the required attributes"), 400

    # Get all boats and output
    elif request.method == 'GET':
        query = client.query(kind=constants.boat)

        # Implement pagination of 3 entities
        q_limit = int(request.args.get('limit', '3'))
        q_offset = int(request.args.get('offset', '0'))
        list_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = list_iterator.pages
        results = list(next(pages))

        if list_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None

        # Loop through entities to be output in response and create response
        for e in results:
            dict_result = dict(e)

            live_link = request.base_url + "boats/" + str(e.key.id)

            e["id"] = e.key.id
            e["name"] = dict_result.get("name")
            e["type"] = dict_result.get("type")
            e["length"] = dict_result.get("length")
            e["loads"] = dict_result.get("loads")
            e["self"] = live_link

        output = {"boats": results}

        # Add count of page of results and total count of entities
        list_all = list(query.fetch())
        output["count"] = len(results)
        output["total"] = len(list_all)

        # Add next_url to the list outputted
        if next_url:
            output["next"] = next_url

        return jsonify(output), 200

    # Incorrect request found
    else:
        return jsonify(Error='Method not accepted')


# Get a boat and delete a boat
@app.route('/boats/<id>', methods={'GET', 'DELETE'})
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

            live_link = request.base_url + "boats/" + str(id)
            # Set response
            response = {
                'id': id,
                'name': dict_result.get("name"),
                'type': dict_result.get("type"),
                'length': dict_result.get("length"),
                'loads': dict_result.get("loads"),
                'self': live_link
            }

            return jsonify(response), 200

        # No entity found, return not found
        else:
            return jsonify(Error="No boat with this ID exists"), 404

    # Delete a boat based on created key from ID
    elif request.method == 'DELETE':
        # Get boat based on key and update values
        boat = client.get(key=key)

        # If boat exists, check for loads and remove carrier from loads found.
        if boat != None:
            # Check if boat has loads
            if boat.get("loads") != None:

                # Find load to be removed and delete it
                for e in boat.get("loads"):
                    # Create key based on ID for load
                    load_key = client.key(constants.load, int(e.get("id")))
                    load = client.get(key=load_key)

                    load.update(carrier=None)

                    client.put(load)

            client.delete(key)
            return '', 204
        else:
            return jsonify(Error="No boat with this ID exists"), 404

    # Incorrect request found
    else:
        return jsonify(Error='Method not accepted')


# Get all loads or add a load
@app.route('/loads', methods={'GET', 'POST'})
def load_get_add():
    # Add a load with provided values in JSON
    if request.method == 'POST':
        content = request.get_json()

        # Check that all three required JSON attributes are present
        if all([field in content.keys() for field in ['weight', 'content', 'delivery_date']]):
            # Create a load entity with given values
            new_load = datastore.entity.Entity(key=client.key(constants.load))
            new_load.update({"weight": content["weight"], "content": content["content"], "carrier": None,
                             "delivery_date": content["delivery_date"]})

            # Send created load to datastore
            client.put(new_load)

            live_link = request.base_url + "loads/" + str(new_load.id)


            # Set response
            response = {
                'id': new_load.id,
                'weight': new_load.get("weight"),
                'content': new_load.get("content"),
                'carrier': new_load.get("carrier"),
                'delivery_date': new_load.get("delivery_date"),
                'self': live_link
            }

            return jsonify(response), 201

        else:
            return jsonify(Error="The request object is missing at least one of the required attributes"), 400

    # Get all loads and output
    elif request.method == 'GET':
        query = client.query(kind=constants.load)

        # Implement pagination of 3 entities
        q_limit = int(request.args.get('limit', '3'))
        q_offset = int(request.args.get('offset', '0'))
        list_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = list_iterator.pages
        results = list(next(pages))

        if list_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None

        result_list = []
        for e in results:
            dict_result = dict(e)

            live_link = request.base_url + "loads/" + str(e.key.id)

            e["id"] = e.key.id
            e["weight"] = dict_result.get("weight")
            e["carrier"] = dict_result.get("carrier")
            e["content"] = dict_result.get("content")
            e["delivery_date"] = dict_result.get("delivery_date")
            e["self"] = live_link

        output = {"loads": results}

        # Add count of page of results and total count of entities
        list_all = list(query.fetch())
        output["count"] = len(results)
        output["total"] = len(list_all)

        # Add next_url to the list outputted
        if next_url:
            output["next"] = next_url

        return jsonify(output), 200

    # Incorrect request found
    else:
        return jsonify(Error='Method not accepted')


# Get a load or delete a load
@app.route('/loads/<id>', methods={'GET', 'DELETE'})
def load_get_delete(id):
    # Create key based on ID for load
    key = client.key(constants.load, int(id))

    # Find load with created key
    if request.method == 'GET':
        # Create query
        query = client.query(kind=constants.load)
        query.key_filter(key, '=')

        # Return found result
        result = list(query.fetch())

        # If an entity is found, return it
        if len(result) == 1:

            dict_result = dict(result[0])

            live_link = request.base_url + "loads/" + str(id)
            # Set response
            response = {
                'id': id,
                'weight': dict_result.get("weight"),
                'carrier': dict_result.get("carrier"),
                'content': dict_result.get("content"),
                'delivery_date': dict_result.get("delivery_date"),
                'self': live_link
            }

            return jsonify(response), 200

        # No entity found, return not found
        else:
            return jsonify(Error="No load with this ID exists"), 404

    # Delete a load based on created key from ID
    elif request.method == 'DELETE':
        # Get boat based on key and update values
        load = client.get(key=key)

        # If load with ID is found, remove it and check if it exists on a boat.
        if load != None:
            # Check if load has a carrier, if not just delete the load, otherwise remove load from boat first
            if load.get("carrier") != None:
                # Create key based on ID for boat
                boat_key = client.key(constants.boat, int(load.get("carrier").get("id")))
                boat = client.get(key=boat_key)

                # Find load to be removed and delete it
                for e in boat.get("loads"):
                    if e.get("id") == id:
                        boat.get("loads").remove(e)

                # Update boat with load removed
                client.put(boat)

            client.delete(key)
            return '', 204

        # Load with ID is not found, return error and 404
        else:
            return jsonify(Error="No load with this ID exists"), 404

    # Incorrect request found
    else:
        return jsonify(Error='Method not accepted')


# Managing loads: can be removed from a boat by DELETE or added to a boat with PUT
@app.route('/boats/<boat_id>/loads/<load_id>', methods={'PUT'})
def load_add_remove (boat_id, load_id):
    # Create key based on ID for load
    load_key = client.key(constants.load, int(load_id))
    # Create key based on ID for boat
    boat_key = client.key(constants.boat, int(boat_id))

    # Create load query
    query = client.query(kind=constants.load)
    query.key_filter(load_key, '=')

    # Return found result
    load_result = list(query.fetch())

    # Create boat query
    query = client.query(kind=constants.boat)
    query.key_filter(boat_key, '=')

    # Return found result
    boat_result = list(query.fetch())

    # Adds a load to a boat
    if request.method == 'PUT':
        # If either a boat or a load are not found, return error and 404
        if len(load_result) == 0 or len(boat_result) == 0:
            return jsonify(Error="The specified boat and/or load don’t exist"), 404

        # Sets load with the boat and adds load to the boat
        else:
            load = load_result[0]
            boat = boat_result[0]

            # If the load is already assigned, return 403 and error
            if load.get("carrier") != None:
                return jsonify(Error="The load is already assigned to a boat"), 403
            # If the load is not assigned already, set load to boat 204
            else:
                boat_link = request.base_url + "boats/" + str(boat_id)
                # Set response for boat and add to load
                boat_obj = {
                    'id': boat_id,
                    'name': boat.get("name"),
                    'self': boat_link
                }
                load.update(carrier=boat_obj)

                load_link = request.base_url + "loads/" + str(load_id)
                # Set response for load and add to boat
                load_obj = {
                    'id': load_id,
                    'self': load_link
                }
                boat['loads'].append(load_obj)

                client.put(load)
                client.put(boat)

                return '', 204


# GET all loads associated with a boat
@app.route('/boats/<boat_id>/loads', methods={'GET'})
def get_boat_loads (boat_id):
    # Create key based on ID for boat
    boat_key = client.key(constants.boat, int(boat_id))

    # Create boat query
    query = client.query(kind=constants.boat)
    query.key_filter(boat_key, '=')

    # Return found result
    boat_result = list(query.fetch())

    if request.method == "GET":
        # If an entity is found, return it
        if len(boat_result) == 1:

            dict_result = dict(boat_result[0])

            result_list = []
            # Set load values to output and add live link
            for e in dict_result.get("loads"):
                load_result = dict(e)

                # Create key based on ID for load
                load_key = client.key(constants.load, int(load_result.get("id")))

                # Create load query
                query = client.query(kind=constants.load)
                query.key_filter(load_key, '=')

                # Get load
                load = list(query.fetch())
                load_dict = dict(load[0])

                # Set results to be returned
                live_link = request.base_url + "loads/" + str(load_result.get("id"))
                e["id"] = load_result.get("id")
                e["weight"] = load_dict.get("weight")
                e["content"] = load_dict.get("content")
                e["delivery_date"] = load_dict.get("delivery_date")
                e["self"] = live_link

                result_list.append(e)

            return jsonify(result_list), 200

        # Boat could not be found, return error
        else:
            return jsonify(Error="Boat could not be found with that ID"), 404

    else:
        return jsonify(Error="No method found"), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

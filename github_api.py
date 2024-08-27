#Implement a small HTTP service to store objects organized by repository. Clients of this service should be able to GET, PUT, and DELETE objects.
from flask import Flask, jsonify, request
import sys
import hashlib
import os

# BUF_SIZE is totally arbitrary, change for your app!
BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
sha256 = hashlib.sha256()

# The service should de-duplicate data objects by repository.
# The service should listen on port 8282.
# The included tests should pass and not be modified. Adding additional tests is encouraged.
# The service must implement the API as described below.
# The data can be persisted in memory, on disk, or wherever you like.
# Do not include any extra dependencies.

#init the api 
app = Flask(__name__)

#init our in 'in memory' cache/data_storage
# data_storage = {
# "carlos_repo":{
#   'object1' : { oid: sha256,
#                 size: 'size'},
#   'object2': { oid: sha256,
#                size: 'size'},
#}

data_storage = {}

#setup the routes
#GET
@app.route('/data/<repository>/<objectid>', methods=['GET'])
# this function should get objects inside of the specified repository, and the given objectid
# function receives the repository name <string>, objectid <string>
def get_data_from_repository(repository, objectid):
    print("line 38")
    # check to see if that item we want to get exists
    if data_storage[repository][objectid]:
        # if it does, then simply return it
        return jsonify(data = data_storage[repository][objectid], statusCode = 200, message = "success")
    else:
         # else return a 404 error
        return jsonify( statusCode = 404, message = "object not found in server")



#PUT - ROUTES CAN CREATE NEW ITEMS AS WELL AS UPDATE EXISTING ITEMS
@app.route('/data/<repository>', methods=['PUT'])
# this function should create new objects inside of the specified repository
# function recieves repository name <string>
def put_repository(repository):
    # check if the request has the file part
    try:
        if 'file' in request.files:
            file = request.files['file']
            #calculate sha256 of the data
            objectdata = calculate_sha_256_and_size(file.filename)
            formed_data_dictionary= form_object_data(objectdata[0], objectdata[1])
            #check if the name exists inside of the data_storage
            # if name does not exist, add that into the the data storage along with an orgID #TODO GENERATE A RANDOM UNIQUE Objectid
            if repository not in data_storage:
                #update data repository under the key to = sha256
                data_storage[repository] = formed_data_dictionary
                return jsonify(data = data_storage[repository], responseMessage="Successfully created your object", response=200)
            # if repository name already exists
            if repository in data_storage:
                #append formed data onto the data_storages for the given key 'repository'
                data_storage[repository].update(formed_data_dictionary)
                return jsonify(data = data_storage[repository], responseMessage="Successfully created your object", response=200)

            return jsonify(data_storage[repository]), 200
        else:
            return "no file to upload, client error", 400
    except:
        return "server error", 500
    

#DELETE
@app.route('/data/<repository>/<objectid>', methods=['DELETE'])
# this function should create new objects inside of the specified repository
# function recieves repository name <string>, objectid <string>
def delete_data_from_repository(repository, objectid):
    # this function should delete objects from the specified repository
    if objectid in data_storage[repository]:
        del data_storage[repository][objectid]
        return jsonify(200)
    else:
        return jsonify(message="object does not exist in server", statusCode=404)



#scratch
# for end user to interact with this api, first the PUT route must be called to create the object, or update that object if it already exists
# then we can call the GET and DELETE ROUTES

def form_object_data(sha256, size):
    res = { sha256 : {'oid': sha256, 
                      "size": size}}

    return res



#helper methods
def calculate_sha_256_and_size(file):
    size = 0
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
            size += len(data)
    print("SHA256: {0}".format(sha256.hexdigest()))
    return [sha256.hexdigest(), size]

if __name__ == '__main__':
    app.run()

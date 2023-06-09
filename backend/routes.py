from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys
from bson.json_util import dumps
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################
@app.route("/health", methods=["GET"])
def health():
    return  {"status":"OK"}


@app.route("/count")
def count():
    """return length of data"""
    count = len(songs_list)

    return {"count": count}, 200    



@app.route("/song",methods=["GET"])
def songs():
   docs = db.songs.find({}) 
   docs = list(docs)
   docs = dumps(docs)
   return {"songs":docs} , 200    

@app.route("/song/<int:id>",methods=["GET"])
def get_song_by_id(id):
    try:
        doc = db.songs.find_one({"id": id})
        doc = dumps(doc)
        if doc:
            return jsonify(doc), 200
        else:
            return jsonify({"message": "Song with ID not found"}), 404
    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500    


@app.route("/song",methods=["POST"])
def create_song():
    song = request.json
    if not song:
        return {"Message": f"not data"}, 404
    try:
        for d in songs_list:
            if d["id"] == song["id"]:
                return {"Message": f"Song with id {song['id']} already present"}, 404
        songs_list.append(song)
        return song, 200
    except: 
        return {"message": "data not defined"}, 500


@app.route("/song/<int:id>", methods=["PUT"])
def update_song(id):
    try:
        song = request.json
        if not song:
            return {"Message": "No data provided"}, 404
        existing_song = db.songs.find_one({"id": id})
        if not existing_song:
            return {"message": "Song not found"}, 404

        db.songs.update_one({"id": id}, {"$set": song})
        updated_song = db.songs.find_one({"id": id})
        d = dumps(updated_song)
        return jsonify(d),200
    except Exception as e:
        return jsonify({"message": "Internal Server Errorsd", "error": str(e)}), 500  


@app.route("/song/<int:id>", methods=["DELETE"])
def delete_song(id):
    try:
        res = db.songs.delete_one({"id": id})
        if res.deleted_count == 0 :
            return {"message": "song not found"},404
        else :
            return {},204

        return 
    except Exception as e:
        return jsonify({"message": "Internal Server Errorsd", "error": str(e)}), 500          
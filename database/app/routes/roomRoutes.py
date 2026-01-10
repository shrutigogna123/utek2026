from flask import Blueprint, request
from app import db
from app.models.room import Room, formatRoom
from app.models.drone import Drone, formatDrone
from app.models.droneDistance import DroneDistance
from sqlalchemy.exc import IntegrityError


room_bp = Blueprint("room", __name__)


# Request:
# {
#   "locationX": 5,
#   "locationY": 10,
#   "battery": 100,
#   "currentJob": "delivery",
#   "distances": [
#     {"room_id": 101, "distance": 25.0},
#     {"room_id": 102, "distance": 40.5}
#   ]
# }
@room_bp.route("/", methods=["POST"])
def createRoom():
    data = request.json

    try:
        room = Room(
            name = data['name'],
            topLeftX = data['topLeftX'],
            topLeftY = data['topLeftY'],
            bottomRightX = data['bottomRightX'],
            bottomRightY = data['bottomRightY'],
            suppliesNeeded = data['suppliesNeeded'],
        )
        # figure out how to add the distances

        db.session.add(room)
        db.session.flush()
        
        # adding distances to the association table
        if 'distances' in data:
            for d in data['distances']:
                drone = Drone.query.get(d['drone_id'])
                if drone: # checking if the Room exists
                    distance_entry = DroneDistance(
                        drone_id = drone.id,
                        room_id = room.id,
                        distance = d['distance']
                    )
                    db.session.add(distance_entry), 201
        db.session.commit()
        return formatRoom(room), 201
    except IntegrityError:
        db.session.rollback()
        return {"error": "A room with this name already exists."}, 400


@room_bp.route("/", methods=["GET"])
def getRooms():
    rooms = Room.query.order_by(Room.name.asc()).order_by(Room.id.asc()).all()
    allRooms = []
    for room in rooms:
        allRooms.append(formatRoom(room))
    return {"rooms": allRooms}

# get single room
@room_bp.route ('/<id>', methods=['GET'])
def getRoom(id):
    room = Room.query.filter(Room.id == id).one()
    formattedRoom = formatRoom(room) 
    return {"room": formattedRoom}

# delete a room
@room_bp.route ('/<id>', methods=['DELETE'])
def deleteRoom(id):
    room = Room.query.filter(Room.id == id).one()
    db.session.delete(room)
    db.session.commit()
    return f"Room (id: {id}) deleted"

# edit a room
@room_bp.route ('/<id>', methods=['PUT'])
def updateRoom(id):
    room = Room.query.get_or_404(id) # returns 404 if not found
    data = request.json
    room.name = data.get('name', room.name)
    room.topLeftX = data.get('topLeftX', room.topLeftX)
    room.topLeftY = data.get('topLeftY', room.topLeftY)
    room.bottomRightX = data.get('bottomRightX', room.bottomRightX)
    room.bottomRightY = data.get('bottomRightY', room.bottomRightY)
    room.suppliesNeeded = data.get('suppliesNeeded', room.suppliesNeeded)
    
    db.session.flush()

    # updating distances to the association table by deleting all current rooms and updating the distances
    DroneDistance.query.filter_by(room_id=room.id).delete()

    if 'distances' in room:
        for d in data['distances']:
            drone = Drone.query.get(d['drone_id'])
            if room: # checking if the Room exists
                distance_entry = DroneDistance(
                    drone_id = drone.id,
                    room_id = room.id,
                    distance = d['distance']
                )
                db.session.add(distance_entry), 201

    db.session.commit()
    return {'room': formatRoom(room)}

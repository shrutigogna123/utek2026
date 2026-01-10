from flask import Blueprint, request
from app import db
from app.models.drone import Drone, formatDrone
from app.models.room import Room, formatRoom
from app.models.droneDistance import DroneDistance
from sqlalchemy.exc import IntegrityError


drone_bp = Blueprint("drone", __name__)


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
@drone_bp.route("/", methods=["POST"])
def createDrone():
    data = request.json

    try:
        drone = Drone(
            locationX = data['locationX'],
            locationY = data['locationY'],
            battery = data['battery'],
            currentJob = data['currentJob']
        )
        # figure out how to add the distances

        db.session.add(drone)
        db.session.flush()
        
        # adding distances to the association table
        if 'distances' in drone:
            for d in data['distances']:
                room = Room.query.get(d['room_id'])
                if room: # checking if the Room exists
                    distance_entry = DroneDistance(
                        drone_id = drone.id,
                        room_id = room.id,
                        distance = d['distance']
                    )
                    db.session.add(distance_entry), 201
        db.session.commit()
        return formatDrone(drone), 201
    except IntegrityError:
        db.session.rollback()
        return {"error": "A drone with this id already exists."}, 400


@drone_bp.route("/", methods=["GET"])
def getDrones():
    drones = Drone.query.order_by(Drone.name.asc()).order_by(Drone.id.asc()).all()
    allDrones = []
    for drone in drones:
        allDrones.append(formatDrone(drone))
    return {"drones": allDrones}

# get single drone
@drone_bp.route ('/<id>', methods=['GET'])
def getDrone(id):
    drone = Drone.query.filter(Drone.id == id).one()
    formattedDrone = formatDrone(drone) 
    return {"drone": formattedDrone}

# delete a drone
@drone_bp.route ('/<id>', methods=['DELETE'])
def deleteDrone(id):
    drone = Drone.query.filter(Drone.id == id).one()
    db.session.delete(drone)
    db.session.commit()
    return f"Drone (id: {id}) deleted"

# edit a drone
@drone_bp.route ('/<id>', methods=['PUT'])
def updateDrone(id):
    drone = Drone.query.get_or_404(id) # returns 404 if not found
    data = request.json
    drone.locationX = data.get('locationX', drone.locationX)
    drone.locationY = data.get('locationY', drone.locationY)
    
    drone.battery = data.get('battery', drone.battery)
    drone.currentJob = data.get('currentJob', drone.currentJob)
    
    db.session.flush()

    # updating distances to the association table by deleting all current drones and updating the distances
    DroneDistance.query.filter_by(drone_id=drone.id).delete()

    if 'distances' in drone:
        for d in data['distances']:
            room = Room.query.get(d['room_id'])
            if room: # checking if the Room exists
                distance_entry = DroneDistance(
                    drone_id = drone.id,
                    room_id = room.id,
                    distance = d['distance']
                )
                db.session.add(distance_entry), 201

    db.session.commit()
    return {'drone': formatDrone(drone)}

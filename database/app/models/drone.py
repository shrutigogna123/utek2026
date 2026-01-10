from app.extensions import db

class Drone (db.Model):
    __tablename__ = 'drones'
    id = db.Column(db.Integer, primary_key = True)
    locationX = db.Column (db.Float, nullable = False, default = 0)
    locationY = db.Column (db.Float, nullable = False, default = 0)
    battery = db.Column (db.Float, default = 100)
    currentJob = db.Column (db.Text)

    # parent-child relationship
    distances = db.relationship ('DroneDistance', back_populates='drone', cascade="all, delete-orphan") # Drone <=> Rooms (N:M relationship)

    def __repr__(self):
        return f"Drone: ({self.locationX}, {self.locationY})"
    
def formatDrone(drone):
    return {
        "id": drone.id,
        "locationX": drone.locationX,
        "locationY": drone.locationY,
        "battery": drone.battery,
        "currentJob": drone.currentJob,
        "distances": {item.room_id: item.distance for item in drone.distances}
    }
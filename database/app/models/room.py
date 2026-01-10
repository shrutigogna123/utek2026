from app.extensions import db

class Room (db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column (db.String, nullable = False, unique = True)
    topLeftX = db.Column (db.Float, nullable = False, default = 0)
    topLeftY = db.Column (db.Float, nullable = False, default = 0)
    bottomRightX = db.Column (db.Float, nullable = False, default = 0)
    bottomRightY = db.Column (db.Float, nullable = False, default = 0)
    suppliesNeeded = db.Column (db.Text)
    
    # parent-child relationship
    distances = db.relationship ('DroneDistance', back_populates='room', cascade="all, delete-orphan") # Drone <=> Rooms (N:M relationship)

    def __repr__(self):
        return f"Room: ({self.locationX}, {self.locationY})"
    
def formatRoom(room):
    return {
        "id": room.id,
        "name": room.name,
        "topLeftX": room.topLeftX,
        "topLeftY": room.topLeftY,
        "bottomRightX": room.bottomRightX,
        "bottomRightY": room.bottomRightY,
        "suppliesNeeded": room.suppliesNeeded,
        "distances": {drone.id: drone.distance for drone in room.distances}
    }
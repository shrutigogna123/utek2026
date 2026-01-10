from app.extensions import db  # <-- changed this line


class DroneDistance (db.Model):
    __tablename__ = "drone_distance"
    drone_id = db.Column(db.Integer, db.ForeignKey("drones.id"), primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), primary_key=True)
    distance = db.Column(db.Float, nullable=False)

    drone = db.relationship("Drone", back_populates="distances")
    room = db.relationship("Room", back_populates="distances")
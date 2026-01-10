from app.extensions import db
from app.models.request import Request, formatRequest
class Supply (db.Model):
    __tablename__ = 'supplies'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False, unique = True)
    description = db.Column (db.Text, nullable = False)
    weight = db.Column (db.Float)
    quantity = db.Column (db.Integer, nullable = False, default = 0)

    requests = db.relationship('Request', back_populates='supply', cascade="all, delete-orphan") # parent side: Supply -> Requests (1:N)
    def __repr__(self):
        return f"Supply: {self.description}"
    
def formatSupply(supply):
    return {
        "name": supply.name,
        "id": supply.id,
        "description": supply.description,
        "weight": supply.weight,
        "quantity": supply.quantity,

        "requests": [formatRequest(request) for request in supply.requests]
    }
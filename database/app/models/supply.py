from app.extensions import db

class Supply (db.Model):
    __table__ = 'supplies'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False, unique = True)
    description = db.Column (db.Text, nullable = False)
    weight = db.Column (db.Float)
    quantity = db.Column (db.Integer, nullable = False)

    def __repr__(self):
        return f"Supply: {self.description}"
    
def formatSupply(supply):
    return {
        "name": supply.name,
        "id": supply.id,
        "description": supply.description,
        "weight": supply.weight,
        "quantity": supply.quantity
    }
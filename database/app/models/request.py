from app.extensions import db
import enum
from sqlalchemy import Enum as PgEnum

class timeRequire(enum.Enum):
    LIFE_CRITICAL_0to4 = 1
    SEVERE_4to8 = 2
    HIGH_8to15 = 3
    MODERATE_15to30 = 4
    LOW_30to60 = 5

class ctasLevel(enum.Enum):
    LEVEL1 = 1
    LEVEL2 = 2
    LEVEL3 = 3
    LEVEL4 = 4
    LEVEL5 = 5

class Request (db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key = True)
    requester_id = db.Column (db.Integer, nullable = False)
    description = db.Column (db.Text, nullable = False)
    time_required = db.Column(PgEnum(timeRequire, name="time_required"), nullable=False, default = timeRequire.LOW_30to60)
    ctas_level = db.Column(PgEnum(ctasLevel, name="ctas_level"), nullable=False, default = ctasLevel.LEVEL5)
    quantity_of_supply = db.Column (db.Integer, nullable = False)
    supply_id = db.Column(db.Integer, db.ForeignKey('supplies.id')) # FK points to parent
    supply = db.relationship('Supply', back_populates = 'requests') # child side: request -> supply (1:N)

    def __repr__(self):
        return f"Request: {self.description}"
    
def formatRequest(request):
    return {
        "id": request.id,
        "requester_id": request.requester_id,
        "description": request.description,
        "time_required": request.time_required.name,
        "ctas_level": request.ctas_level.name,
        "quantity_of_supply": request.quantity_of_supply,
        "supply": {
            "id": request.supply.id,
            "name": request.supply.name
        } if request.supply else None
    }
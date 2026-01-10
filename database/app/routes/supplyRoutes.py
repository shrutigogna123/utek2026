from flask import Blueprint, request
from app import db
from app.models.supply import Supply, formatSupply
from app.models.request import Request as RequestModel, formatRequest
from sqlalchemy.exc import IntegrityError


supply_bp = Blueprint("supply", __name__)


@supply_bp.route("/", methods=["POST"])
def createSupply():
    data = request.json

    # # Get the supply by name
    # supply_name = data.get("supply_name")
    # if not supply_name:
    #     return {"error": "supply_name is required."}, 400

    # supply = Supply.query.filter_by(name=supply_name).first()
    # if not supply:
    #     return {"error": f"Supply with name '{supply_name}' not found."}, 404
    
    # getting the supplies
    requestID = data.get("requests", [])
    requestList = []
    for reqID in requestID:
        req = RequestModel.query.filter(RequestModel.id == reqID).first()
        if not req:
            return {"error": f"Request with id '{reqID}' not found."}, 404
        requestList.append(req)

    
    if Supply.query.filter_by(name=data['name']).first():
        return {"error": "Supply with that name already exists."}, 409
    
    
    try:
        supply = Supply(
            name = data['name'],
            description = data['description'],
            weight = data['weight'],
            quantity = data['quantity'],
            requests = requestList
        )
        db.session.add(supply)
        db.session.commit()
        return formatSupply(supply), 201
    except IntegrityError:
        db.session.rollback()
        return {"error": "A supply with this name already exists."}, 400


@supply_bp.route("/", methods=["GET"])
def getSupplies():
    supplies = Supply.query.order_by(Supply.name.asc()).order_by(Supply.id.asc()).all()
    allSupplies = []
    for supply in supplies:
        allSupplies.append(formatSupply(supply))
    return {"supplies": allSupplies}

# get single supply
@supply_bp.route ('/<id>', methods=['GET'])
def getSupply(id):
    supply = Supply.query.filter(Supply.id == id).one()
    formattedSupply = formatSupply(supply) 
    return {"supply": formattedSupply}

# delete a supply
@supply_bp.route ('/<id>', methods=['DELETE'])
def deleteSupply(id):
    supply = Supply.query.filter(Supply.id == id).one()
    db.session.delete(supply)
    db.session.commit()
    return f"Supply (id: {id}) deleted"

# edit a supply
@supply_bp.route ('/<id>', methods=['PUT'])
def updateSupply(id):
    supply = Supply.query.get_or_404(id) # returns 404 if not found
    data = request.json
    supply.name = data.get('name', supply.name)
    supply.description = data.get('description', supply.description)
    
    supply.weight = data.get('weight', supply.weight)
    supply.quantity = data.get('quantity', supply.quantity)
    
    # update requests
    if "requests" in data:
        updatedRequests = []
        for reqID in data["requests"]:
            request = Request.query.filter(Request.id == reqID).first()
            if not request:
                return {"error": f"Request '{reqID}' not found for this Supply."}, 404
            updatedRequests.append(request)
        supply.requests = updatedRequests
    db.session.commit()
    return {'supply': formatSupply(supply)}

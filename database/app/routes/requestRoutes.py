from flask import Blueprint, request
from app import db
from app.models.request import Request as RequestModel, formatRequest, timeRequire, ctasLevel
from app.models.supply import Supply, formatSupply
from sqlalchemy.exc import IntegrityError


request_bp = Blueprint("request", __name__)


@request_bp.route("/", methods=["POST"])
def createRequest():
    data = request.json

    # # Get the request by name
    # request_name = data.get("request_name")
    # if not request_name:
    #     return {"error": "request_name is required."}, 400

    # request = Request.query.filter_by(name=request_name).first()
    # if not request:
    #     return {"error": f"Request with name '{request_name}' not found."}, 404
    
    # Get the supply by id
    supply_id = data.get("supply")
    if not supply_id:
        return {"error": "supply_id is required."}, 400
    supply = Supply.query.get(supply_id)
    if not supply:
        return {"error": f"Supply with id '{supply_id}' not found."}, 404
    supply_id = supply.id
    

    # if RequestModel.query.filter_by(name=data['name']).first():
    #     return {"error": "Request with that name already exists."}, 409
    
    
    try:
        req = RequestModel(
            requester_id = data['requester_id'],
            description = data['description'],
            time_required = timeRequire[data['time_require']],
            ctas_level = ctasLevel[data['ctas_level']],
            quantity_of_supply = data['quantity_of_supply'],

            # parent-child
            supply = supply,
            supply_id = supply_id
            
        )
        db.session.add(req)
        db.session.commit()
        return formatRequest(req), 201
    except IntegrityError:
        db.session.rollback()
        return {"error": "A request with this id already exists."}, 400


@request_bp.route("/", methods=["GET"])
def getRequests():
    requests = RequestModel.query.order_by(RequestModel.time_required.asc()).order_by(RequestModel.ctas_level.asc()).all()
    allRequests = []
    for req in requests:
        allRequests.append(formatRequest(req))
    return {"requests": allRequests}

# get single request
@request_bp.route ('/<id>', methods=['GET'])
def getRequest(id):
    req = RequestModel.query.filter(RequestModel.id == id).one()
    formattedRequest = formatRequest(req) 
    return {"request": formattedRequest}

# delete a request
@request_bp.route ('/<id>', methods=['DELETE'])
def deleteRequest(id):
    req = RequestModel.query.filter(RequestModel.id == id).one()
    db.session.delete(req)
    db.session.commit()
    return f"Request (id: {id}) deleted"

# edit a request
@request_bp.route ('/<id>', methods=['PUT'])
def updateRequest(id):
    req = RequestModel.query.get_or_404(id) # returns 404 if not found
    data = req.json
    req.requester_id = data.get('requester_id', req.requester_id)
    req.description = data.get('description', req.description)
    
    time_requirestr = data.get('time_require', req.time_require.name)
    # safely find the enum member
    for member in timeRequire:
        if member.name == time_requirestr:
            req.time_require = member
            break
    else:
        return {"error": f"Invalid time_require: {time_requirestr}"}, 400

    ctas_str = data.get('ctas_level', req.ctas_level.name)
    # safely find the enum member
    for member in ctasLevel:
        if member.name == ctas_str:
            req.ctas_level = member
            break
    else:
        return {"error": f"Invalid ctas_level: {ctas_str}"}, 400

    req.quantity_of_supply = data.get('quantity_of_supply', req.quantity_of_supply)

    supplyID = data.get('supply', req.supply.id)
    supply = Supply.query.filter(supplyID == Supply.id).first_or_404()
    req.supply = supply
    req.supply_id = supply.id    
    
    db.session.commit()
    return {'request': formatRequest(req)}

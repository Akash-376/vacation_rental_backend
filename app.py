
from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from flask_cors import CORS # to handle CORS policy error

app = Flask(__name__)
CORS(app, resources={
    r"/*":{"origins":"*"}
})  # Enable CORS for all routes
client = MongoClient('mongodb+srv://akash:Akash_1997@cluster0.sssf80e.mongodb.net/?retryWrites=true&w=majority')
db = client['hotel_renting']






# Entity1: Host
#Register Host
@app.route('/hosts', methods=['POST'])
def create_host():
    data = request.json
    data['properties'] = [] # initially host's properties would we empty list
    email = data.get('email')
    # print(email)

    # Check if email already exists
    existing_host = db.hosts.find_one({'email': email})
    if existing_host:
        return jsonify({'error': 'This Email is already registered. Please try with another one'}), 400

    host_id = db.hosts.insert_one(data).inserted_id
    return jsonify({'host_id': str(host_id)}), 201

# get host by Id
@app.route('/hosts/<host_id>', methods=['GET'])
def get_host(host_id):
    host = db.hosts.find_one({'_id': ObjectId(host_id)})
    if host:
        host["_id"] = str(host["_id"])
        return jsonify(host), 200
    else:
        return jsonify({'error': 'Host not found'}), 404


# get host_id by email (host_id is needed in frontend to add property)
@app.route('/hostemail/<email>', methods=['GET'])
def get_hostId(email):
    host = db.hosts.find_one({'email': email})
    if host:
        host["_id"] = str(host["_id"])
        return jsonify({'host_id' :host["_id"]}), 200
    else:
        return jsonify({'error': 'Host not found'}), 404


# get host by email
@app.route('/hostnamebyemail/<email>', methods=['GET'])
def get_hostByEmail(email):
    host = db.hosts.find_one({'email': email})
    
    if host:
        host["_id"] = str(host["_id"])
        return jsonify(host['name']), 200
    else:
        return jsonify({'error': 'host not found'}), 404

# Implement routes for updating and deleting hosts






# Entity2: Property

# create new property
@app.route('/properties', methods=['POST'])
def create_property():
    data = request.json
    data['status'] = 'Available'  # Set the initial status to 'Available'
    host_id = data.get('host_id')

    # Check if the host_id is not provided or is empty
    if not host_id:
        return jsonify({'error': 'Host ID is required'}), 400

    # Check if the host exists
    host = db.hosts.find_one({'_id': ObjectId(host_id)})
    if not host:
        return jsonify({'error': 'Host not found'}), 404

    # Insert the property document
    property_id = db.properties.insert_one(data).inserted_id

    # Add the property ID to the host's properties field
    db.hosts.update_one({'_id': ObjectId(host_id)}, {'$push': {'properties': property_id}})

    return jsonify({'property_id': str(property_id)}), 201

# get all properties
@app.route('/properties', methods=['GET'])
def get_All_properties():
    propertyList = list(db.properties.find())
    if propertyList:
        for property in propertyList:
            property["_id"] = str(property["_id"])

        return jsonify(propertyList), 200
    else:
        return jsonify({'error': 'Property not found'}), 404

# get property by Id
@app.route('/properties/<property_id>', methods=['GET'])
def get_property(property_id):
    property = db.properties.find_one({'_id': ObjectId(property_id)})
    if property:
        property["_id"] = str(property["_id"])
        return jsonify(property), 200
    else:
        return jsonify({'error': 'Property not found'}), 404
    
@app.route('/property/update/<property_id>', methods=['PATCH'])
def update_property_price(property_id):
    query = {"_id": ObjectId(property_id)}
    property = db.properties.find_one(query)
    if property:
        new_price = request.args.get('updated_price')
        db.properties.update_one(query, {'$set': {'price':new_price}})
        return jsonify({'message': 'Price updated successfully'})
    return jsonify({'error': 'Property not found with this Id : '+ property_id})


# Implement routes for updating and deleting properties






# Entity3: Guest

# Register new guest
@app.route('/guests', methods=['POST'])
def create_guest():
    data = request.json
    guest_id = db.guests.insert_one(data).inserted_id
    return jsonify({'guest_id': str(guest_id)}), 201

@app.route('/guests', methods=['GET'])
def get_All_guests():
    guests = list(db.guests.find())
    if guests:
        for guest in guests:
            guest["_id"] = str(guest["_id"])

        return jsonify(guests), 201
    else:
        return jsonify({"message": "No any guest found"}), 404


# get guest by Id
@app.route('/guests/<guest_id>', methods=['GET'])
def get_guest(guest_id):
    guest = db.guests.find_one({'_id': ObjectId(guest_id)})
    if guest:
        guest["_id"] = str(guest["_id"])
        return jsonify(guest), 200
    else:
        return jsonify({'error': 'Guest not found'}), 404


# get guest_id by email (host_id is needed in frontend to add property)
@app.route('/guestemail/<email>', methods=['GET'])
def get_guestId(email):
    guest = db.guests.find_one({'email': email})
    if guest:
        guest["_id"] = str(guest["_id"])
        return jsonify({'guest_id' :guest["_id"]}), 200
    else:
        return jsonify({'error': 'guest not found'}), 404


# get guest by email
@app.route('/guestbyemail/<email>', methods=['GET'])
def get_guestByEmail(email):
    guest = db.guests.find_one({'email': email})
    if guest:
        guest["_id"] = str(guest["_id"])
        return jsonify(guest), 200
    else:
        return jsonify({'error': 'guest not found'}), 404


# Guest booking route
@app.route('/guests/bookings/<guest_id>/<property_id>', methods=['POST'])
def book_property(guest_id, property_id):
    # data = request.json
    # property_id = data.get('property_id')
    guest = db.guests.find_one({'_id': ObjectId(guest_id)})
    property = db.properties.find_one({'_id': ObjectId(property_id)})

    if guest and property and property['status'] == 'Available':
        
        # Create booking document
        booking_data = {
            'guest_id': guest_id,
            'property_id': property_id
        }
        booking_id = db.bookings.insert_one(booking_data).inserted_id

        # Update property status to 'Booked' and add guest_id
        db.properties.update_one(
            {'_id': ObjectId(property_id)},
            {'$set': {'status': 'Booked', 'guest_id': guest_id}}
        )

        return jsonify({'booking_id': str(booking_id)}), 201
    # if property is already booked
    elif guest and property and property['status'] == 'Booked':
        return jsonify({'error': 'This property is already booked. Please try another one...'}), 404
    else:
        return jsonify({'error': 'Guest or Property not found or Property is not available'}), 404


# Guest checkout route
@app.route('/guests/checkout/<booking_id>', methods=['DELETE'])
def checkout(booking_id):
    # guest = db.guests.find_one({'_id': ObjectId(guest_id)})
    booking = db.bookings.find_one({'_id': ObjectId(booking_id)})
    # print(guest_id)
    # print(booking_id)

    if booking:
        # Delete the booking document
        db.bookings.delete_one({'_id': ObjectId(booking_id)})

        property_id = booking['property_id']

        # Remove guest_id and update status to 'Available'
        db.properties.update_one(
            {'_id': ObjectId(property_id)},
            {'$unset': {'guest_id': 1}, '$set': {'status': 'Available'}}
        )

        return jsonify({'message': 'Checkout successful'}), 200
    else:
        return jsonify({'error': 'Booking details not found'}), 404


# Guest checkout route2
@app.route('/guests/checkout/<guest_id>/<property_id>', methods=['DELETE'])
def checkout2(guest_id, property_id):
    # guest = db.guests.find_one({'_id': ObjectId(guest_id)})
    guest = db.guests.find_one({'_id': ObjectId(guest_id)})
    property = db.properties.find_one({'_id': ObjectId(property_id)})
    # print(guest_id)
    # print(booking_id)

    if guest and property:
        # Delete the booking document
        db.bookings.delete_one({'guest_id': guest_id, 'property_id': property_id})

        # Remove guest_id and update status to 'Available'
        db.properties.update_one(
            {'_id': ObjectId(property_id)},
            {'$unset': {'guest_id': 1}, '$set': {'status': 'Available'}}
        )

        return jsonify({'message': 'Checkout successful'}), 200
    else:
        return jsonify({'error': 'Booking details not found'}), 404

# Implement routes for updating and deleting guests





            #BOOKING





# Entity4: Booking

# NO need to create Booking manually it will be created automatically when customer will book ant property


# Implement routes for updating and deleting bookings







# Endpoint for admin login
@app.route('/host/login', methods=['POST'])
def admin_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Validate admin credentials against the database
    host = db.hosts.find_one({'email': email, 'password': password})
    if host:
        return jsonify({'email': email, 'role': 'host'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401





# Endpoint for guest login
@app.route('/guest/login', methods=['POST'])
def guest_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Validate guest credentials against the database
    guest = db.guests.find_one({'email': email, 'password': password})
    if guest:
        return jsonify({'email': email, 'role': 'guest'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401




if __name__ == '__main__':
    app.run(debug=True)
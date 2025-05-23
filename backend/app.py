from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    pets = db.relationship('Pet', backref='owner', lazy=True)
    appointments = db.relationship('Appointment', backref='user', lazy=True)

class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String)
    breed = db.Column(db.String)
    size = db.Column(db.String)
    weight = db.Column(db.String)
    gender = db.Column(db.String)
    age = db.Column(db.String)
    appointments = db.relationship('Appointment', backref='pet', lazy=True)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    notes = db.Column(db.Text)

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    appointments = db.relationship('Appointment', backref='service', lazy=True)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'message': 'Missing name, email, or password'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email
        }
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    # For now, just a placeholder response as no server-side session exists yet
    return jsonify({'message': 'Logout successful'}), 200

# --- Pet Management Endpoints ---

@app.route('/api/pets', methods=['POST'])
def add_pet():
    data = request.get_json()
    user_id = data.get('user_id')
    name = data.get('name')
    
    if not user_id or not name:
        return jsonify({'message': 'Missing user_id or pet name'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_pet = Pet(
        user_id=user_id,
        name=name,
        type=data.get('type'),
        breed=data.get('breed'),
        size=data.get('size'),
        weight=data.get('weight'),
        gender=data.get('gender'),
        age=data.get('age')
    )
    db.session.add(new_pet)
    db.session.commit()
    
    return jsonify({
        'message': 'Pet added successfully',
        'pet': {
            'id': new_pet.id,
            'user_id': new_pet.user_id,
            'name': new_pet.name,
            'type': new_pet.type,
            'breed': new_pet.breed,
            'size': new_pet.size,
            'weight': new_pet.weight,
            'gender': new_pet.gender,
            'age': new_pet.age
        }
    }), 201

@app.route('/api/pets', methods=['GET'])
def get_user_pets():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': 'Missing user_id query parameter'}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'message': 'Invalid user_id format'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    pets = Pet.query.filter_by(user_id=user_id).all()
    pets_data = [{
        'id': pet.id,
        'user_id': pet.user_id,
        'name': pet.name,
        'type': pet.type,
        'breed': pet.breed,
        'size': pet.size,
        'weight': pet.weight,
        'gender': pet.gender,
        'age': pet.age
    } for pet in pets]
    
    return jsonify(pets_data), 200

@app.route('/api/pets/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'message': 'Missing user_id in request body'}), 400

    pet = Pet.query.get(pet_id)
    if not pet:
        return jsonify({'message': 'Pet not found'}), 404

    if pet.user_id != user_id:
        return jsonify({'message': 'Forbidden: Pet does not belong to this user'}), 403

    # Update attributes
    pet.name = data.get('name', pet.name)
    pet.type = data.get('type', pet.type)
    pet.breed = data.get('breed', pet.breed)
    pet.size = data.get('size', pet.size)
    pet.weight = data.get('weight', pet.weight)
    pet.gender = data.get('gender', pet.gender)
    pet.age = data.get('age', pet.age)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Pet updated successfully',
        'pet': {
            'id': pet.id,
            'user_id': pet.user_id,
            'name': pet.name,
            'type': pet.type,
            'breed': pet.breed,
            'size': pet.size,
            'weight': pet.weight,
            'gender': pet.gender,
            'age': pet.age
        }
    }), 200

@app.route('/api/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    # Assuming user_id might come in JSON body as per instruction, or could be a query param.
    # For consistency with PUT, let's try JSON body first.
    data = request.get_json()
    user_id = data.get('user_id') 

    if not user_id: # Fallback to query parameter if not in body
        user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'message': 'Missing user_id (must be in JSON body or query parameter)'}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'message': 'Invalid user_id format'}), 400

    pet = Pet.query.get(pet_id)
    if not pet:
        return jsonify({'message': 'Pet not found'}), 404

    if pet.user_id != user_id:
        return jsonify({'message': 'Forbidden: Pet does not belong to this user'}), 403
        
    db.session.delete(pet)
    db.session.commit()
    
    return jsonify({'message': 'Pet deleted successfully'}), 200

# --- Service and Appointment Management Endpoints ---

def populate_services():
    """Pre-populates the Service table if it's empty or specific services are missing."""
    default_services = [
        {'name': 'Basic Bath', 'description': 'Includes bath and blow-dry.', 'price': 30.0},
        {'name': 'Full Groom', 'description': 'Includes bath, haircut, nail trim, ear cleaning.', 'price': 50.0},
        {'name': 'Nail Trim', 'description': 'Just nail trimming.', 'price': 15.0}
    ]
    with app.app_context(): # Ensure app context for db operations
        for service_data in default_services:
            service = Service.query.filter_by(name=service_data['name']).first()
            if not service:
                new_service = Service(name=service_data['name'], description=service_data['description'], price=service_data['price'])
                db.session.add(new_service)
        db.session.commit()

@app.route('/api/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    services_data = [{
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'price': service.price
    } for service in services]
    return jsonify(services_data), 200

@app.route('/api/appointments', methods=['POST'])
def book_appointment():
    data = request.get_json()
    user_id = data.get('user_id')
    pet_id = data.get('pet_id')
    service_id = data.get('service_id')
    date = data.get('date')
    time = data.get('time')
    notes = data.get('notes')

    if not all([user_id, pet_id, service_id, date, time]):
        return jsonify({'message': 'Missing required fields (user_id, pet_id, service_id, date, time)'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        return jsonify({'message': 'Pet not found or does not belong to user'}), 404 # Or 403 if pet exists but wrong user

    service = Service.query.get(service_id)
    if not service:
        return jsonify({'message': 'Service not found'}), 404

    new_appointment = Appointment(
        user_id=user_id,
        pet_id=pet_id,
        service_id=service_id,
        date=date,
        time=time,
        notes=notes
    )
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({
        'message': 'Appointment booked successfully',
        'appointment': {
            'id': new_appointment.id,
            'user_id': new_appointment.user_id,
            'pet_id': new_appointment.pet_id,
            'service_id': new_appointment.service_id,
            'date': new_appointment.date,
            'time': new_appointment.time,
            'notes': new_appointment.notes,
            'pet_name': pet.name, # Include related data
            'service_name': service.name
        }
    }), 201

@app.route('/api/appointments', methods=['GET'])
def get_user_appointments():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'message': 'Missing user_id query parameter'}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'message': 'Invalid user_id format'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    # Eager load pet and service details to avoid N+1 queries if accessed in loop
    appointments = Appointment.query.filter_by(user_id=user_id)\
                                    .join(Pet, Appointment.pet_id == Pet.id)\
                                    .join(Service, Appointment.service_id == Service.id)\
                                    .add_columns(Pet.name.label("pet_name"), Service.name.label("service_name"))\
                                    .all()
    
    appointments_data = []
    for app_obj, pet_name, service_name in appointments: # Result is a tuple: (AppointmentObject, pet_name, service_name)
        appointments_data.append({
            'id': app_obj.id,
            'user_id': app_obj.user_id,
            'pet_id': app_obj.pet_id,
            'service_id': app_obj.service_id,
            'date': app_obj.date,
            'time': app_obj.time,
            'notes': app_obj.notes,
            'pet_name': pet_name,
            'service_name': service_name
        })
        
    return jsonify(appointments_data), 200

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    data = request.get_json()
    user_id = data.get('user_id') if data else None

    if not user_id: # Fallback to query parameter if not in body
        user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'message': 'Missing user_id (must be in JSON body or query parameter)'}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'message': 'Invalid user_id format'}), 400

    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({'message': 'Appointment not found'}), 404

    if appointment.user_id != user_id:
        return jsonify({'message': 'Forbidden: Appointment does not belong to this user'}), 403
        
    db.session.delete(appointment)
    db.session.commit()
    
    return jsonify({'message': 'Appointment canceled successfully'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        populate_services() # Call to pre-populate services
    app.run(debug=True)

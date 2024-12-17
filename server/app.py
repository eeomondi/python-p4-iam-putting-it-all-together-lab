#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource  # type: ignore
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        # Extract data from the request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Basic validation
        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 422
        
        try:
            # Use the User model's method to create the user
            user = User.create_user(username, password)
            return jsonify({'message': 'User created successfully', 'user_id': user.id}), 201
        except IntegrityError:
            db.session.rollback()  # Rollback in case of integrity error (e.g., duplicate username)
            return jsonify({'message': 'Username already exists'}), 422
        except ValueError as e:
            return jsonify({'message': str(e)}), 422

class CheckSession(Resource):
    def get(self):
        # Check if there is an active session
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized'}), 401
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'image_url': user.image_url,
            'bio': user.bio
        })

class Login(Resource):
    def post(self):
        # Extract data from the request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Basic validation
        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 422
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Store the user_id in session for login tracking
            session['user_id'] = user.id
            return jsonify({'message': 'Logged in successfully', 'user_id': user.id}), 200
        
        return jsonify({'message': 'Invalid username or password'}), 401

class Logout(Resource):
    def post(self):
        # Log out the user by clearing the session
        session.pop('user_id', None)
        return jsonify({'message': 'Logged out successfully'}), 200

class RecipeIndex(Resource):
    def get(self):
        # Check if the user is logged in
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized'}), 401
        
        user_id = session['user_id']
        recipes = Recipe.query.filter_by(user_id=user_id).all()
        
        return jsonify([recipe.serialize() for recipe in recipes]), 200

    def post(self):
        # Create a new recipe
        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')
        
        # Ensure user is logged in
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized'}), 401
        
        user_id = session['user_id']
        
        try:
            # Use the Recipe model's method to create a recipe
            recipe = Recipe.create_recipe(title, instructions, minutes_to_complete, user_id)
            return jsonify({'message': 'Recipe created successfully', 'recipe_id': recipe.id}), 201
        except ValueError as e:
            return jsonify({'message': str(e)}), 422

# Add the API resources
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_re

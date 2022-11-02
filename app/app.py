from flask import Flask

from flask_cors import CORS
from flask_restful import Api, Resource
from app.rest.portfoliocontroller import Controller

app = Flask("__name__")
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
api.add_resource(Controller, '/portfolio')

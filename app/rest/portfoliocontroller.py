from flask import jsonify, request

from app.service.portfolioservice import Service
from app.validation.portfoliovalidator import Validator
from flask_restful import Resource


class Controller(Resource):

    def get(self):
        investment_names = request.args.get('invs', default=None)
        priorize = float(request.args.get('priorize', default=0))
        years = float(request.args.get('years', default=1))

        Validator().validate(investment_names, priorize)

        investment_names = investment_names.split(",")

        response_body = Service().find_best_portfolio(investment_names, years, priorize)

        Validator().validate_return(response_body)
        return jsonify(response_body)

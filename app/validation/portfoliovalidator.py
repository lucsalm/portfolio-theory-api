from flask import abort


class Validator:

    def validate(self, investment_names, priorize):
        if type(investment_names) is None or len(investment_names.split(",")) not in range(3, 7):
            abort(400)
        if not (0 <= priorize <= 1):
            abort(400)

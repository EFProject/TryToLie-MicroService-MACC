from marshmallow import Schema, fields


class User(object):
    def __init__(self, name, email, email_verified, provider, matches_played, matches_won, country, signup_date):
        self.name = name
        self.email = email
        self.email_verified = email_verified
        self.provider = provider
        self.matches_played = matches_played
        self.matches_won = matches_won
        self.country = country
        self.signup_date = signup_date


class UserSchema(Schema):
    name = fields.String()
    email = fields.String()
    email_verified = fields.Boolean()
    provider = fields.String()
    matches_played = fields.Integer()
    matches_won = fields.Integer()
    country = fields.String()
    signup_date = fields.String()
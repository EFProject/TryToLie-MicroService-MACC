from marshmallow import Schema, fields


class User(object):
    def __init__(self, id, name, email, emailVerified, provider, matchesPlayed, matchesWon, signupDate):
        self.id = id
        self.name = name
        self.email = email
        self.emailVerified = emailVerified
        self.provider = provider
        self.matchesPlayed = matchesPlayed
        self.matchesWon = matchesWon
        self.signupDate = signupDate


class UserSchema(Schema):
    id = fields.String()
    name = fields.String()
    email = fields.String()
    emailVerified = fields.Boolean()
    provider = fields.String()
    matchesPlayed = fields.Integer()
    matchesWon = fields.Integer()
    signupDate = fields.String()
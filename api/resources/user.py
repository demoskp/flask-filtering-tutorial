import operator
from flask import request
from flask_restful import Resource

from api.schemas.user import UserSchema
from extensions import db
from models import User


def get_comparator(comparator):
    if comparator == ">=":
        return operator.ge
    if comparator == ">":
        return operator.gt
    if comparator == "<=":
        return operator.le
    if comparator == "<":
        return operator.lt
    if comparator == "=":
        return operator.eq


class UserList(Resource):
    def get(self):
        name_filter = request.args.get("name")
        age_filter = request.args.get("age")
        email_filter = request.args.get("email")

        users_query = User.query

        if name_filter:
            users_query = users_query.filter(User.name.ilike(f"%{name_filter}%"))
        if age_filter:
            users_query = users_query.filter(User.age == age_filter)
        if email_filter:
            users_query = users_query.filter(User.email.in_(email_filter.split(",")))

        users = users_query.all()
        schema = UserSchema(many=True)
        return {"results": schema.dump(users)}

    def post(self):
        schema = UserSchema()
        validated_data = schema.load(request.json)

        user = User(**validated_data)
        db.session.add(user)
        db.session.commit()

        return {"msg": "User created", "user": schema.dump(user)}


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        schema = UserSchema()

        return {"user": schema.dump(user)}

    def put(self, user_id):
        schema = UserSchema(partial=True)
        user = User.query.get_or_404(user_id)
        user = schema.load(request.json, instance=user)

        db.session.add(user)
        db.session.commit()

        return {"msg": "User updated", "user": schema.dump(user)}

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()

        return {"msg": "User deleted"}

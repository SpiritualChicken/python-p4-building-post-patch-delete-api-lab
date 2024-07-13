#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.filter_by(id=id).first()
    if not bakery:
        return make_response(jsonify({'error': 'Bakery not found'}), 404)

    data = request.form
    name = data.get('name')

    if name:
        bakery.name = name
        db.session.commit()

    bakery_serialized = bakery.to_dict()
    response = make_response(jsonify(bakery_serialized), 200)
    return response

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.filter_by(id=id).first()
    if not baked_good:
        return make_response(jsonify({'error': 'Baked good not found'}), 404)

    db.session.delete(baked_good)
    db.session.commit()

    response = make_response(jsonify({'message': 'Baked good successfully deleted'}), 200)
    return response


@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.form

    name = data.get('name')
    price = data.get('price')
    bakery_id = data.get('bakery_id')

    if not name or not price or not bakery_id:
        return make_response(jsonify({'error': 'Missing required fields'}), 400)

    try:
        new_baked_good = BakedGood(
            name=name,
            price=int(price),
            bakery_id=int(bakery_id)
        )

        db.session.add(new_baked_good)
        db.session.commit()

        response_body = new_baked_good.to_dict()

        response = make_response(jsonify(response_body), 201)

        return response
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

if __name__ == '__main__':
    app.run(port=5555, debug=True)
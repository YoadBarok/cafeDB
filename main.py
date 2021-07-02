from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice


app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


all_cafes = db.session.query(Cafe).all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def get_random_cafe():
    random_cafe = choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_all_cafes():
    # final = jsonify(cafes={cafe.name: cafe.to_dict() for cafe in all_cafes}) # alternatively
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route('/search')
def get_cafe_location():
    query_location = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=query_location.title()).all()
    if len(cafes) > 0:
        cafes_dict = [cafe.to_dict() for cafe in cafes]
        return jsonify(cafes=cafes_dict)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route('/add', methods=["POST"])
def add_cafe():
    cafe_to_add = Cafe(name=request.form.get("name"),
                       map_url=request.form.get("map_url"),
                       img_url=request.form.get("img_url"),
                       location=request.form.get("location"),
                       seats=request.form.get("seats"),
                       has_toilet=bool(request.form.get("has_toilet")),
                       has_wifi=bool(request.form.get("has_wifi")),
                       has_sockets=bool(request.form.get("has_sockets")),
                       can_take_calls=bool(request.form.get("can_take_calls")),
                       coffee_price=request.form.get("coffee_price"))
    db.session.add(cafe_to_add)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route('/update-price/<cafe_id>', methods=["PATCH"])
def update_price(cafe_id):
    try:
        id_to_update = Cafe.query.get(cafe_id)
        new_price = request.form.get("new_price")
        id_to_update.coffee_price = new_price
        print(cafe_id)
        db.session.commit()
        return jsonify({"Success": "Price updated"})
    except AttributeError:
        return jsonify({"Error": f"Sorry no cafe with ID: {cafe_id}"}), 404


@app.route("/delete/<cafe_id>", methods=["GET", "DELETE"])
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    api_key = request.form.get("api_key")
    if cafe_to_delete:
        if api_key == "TopSecretAPIKey":
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify({"Success": f"{cafe_to_delete.name} removed successfully"})
        else:
            return jsonify({"error": "Wrong api key"}), 403
    else:
        return jsonify({"error": f"No cafe with the id {cafe_id}"}), 404


if __name__ == '__main__':
    app.run(debug=True)

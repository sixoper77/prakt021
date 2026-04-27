from flask import Blueprint, abort, jsonify, request
from sqlalchemy import func

from extensions import db
from models import Category, Film

api = Blueprint('api', __name__, url_prefix='/api')


@api.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify({"data": [c.to_dict() for c in categories]})


@api.route("/categories/<int:id>", methods=["GET"])
def get_category(id):
    category = Category.query.get_or_404(id)
    return jsonify(category.to_dict())


@api.route("/films", methods=["GET"])
def get_films():
    query = Film.query
    category_id = request.args.get("category_id", type=int)
    if category_id:
        query = query.filter_by(category_id=category_id)
    search = request.args.get("search", "", type=str)
    if search:
        query = query.filter(Film.title.ilike(f"%{search}%"))
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        {
            "data": [f.to_dict() for f in pagination.items],
            "meta": {
                "page": pagination.page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        }
    )


@api.route("/films/<int:id>", methods=["GET"])
def get_film(id):
    film = Film.query.get_or_404(id)
    return jsonify(film.to_dict())


@api.route("/films", methods=["POST"])
def create_film():
    data = request.get_json()
    if not data or not all(
        k in data for k in ("title", "year", "rating", "category_id")
    ):
        abort(400, description="Не вистачає обов'язкових полів")

    film = Film(
        title=data["title"],
        year=data["year"],
        rating=data["rating"],
        category_id=data["category_id"],
    )
    db.session.add(film)
    db.session.commit()
    return jsonify(film.to_dict()), 201


@api.route("/films/<int:id>", methods=["PUT"])
def update_film(id):
    film = Film.query.get_or_404(id)
    data = request.get_json()

    if not data:
        abort(400, description="Тіло запиту має бути JSON")

    if "title" in data:
        film.title = data["title"]
    if "year" in data:
        film.year = data["year"]
    if "rating" in data:
        film.rating = data["rating"]
    if "category_id" in data:
        film.category_id = data["category_id"]

    db.session.commit()
    return jsonify(film.to_dict())


@api.route("/films/<int:id>", methods=["DELETE"])
def delete_film(id):
    film = Film.query.get_or_404(id)
    db.session.delete(film)
    db.session.commit()
    return "", 204


@api.route("/stats", methods=["GET"])
def get_stats():
    total_films = db.session.query(func.count(Film.id)).scalar()
    avg_rating = db.session.query(func.avg(Film.rating)).scalar()

    return jsonify(
        {
            "total_films": total_films,
            "average_rating": round(avg_rating, 2) if avg_rating else 0,
        }
    )


@api.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Ресурс не знайдено"}), 404


@api.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error.description)}), 400

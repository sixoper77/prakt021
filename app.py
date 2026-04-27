import os

from flask import Flask, render_template

from extensions import db
from models import Category, Film
from routers import api


def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "api.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(api)

    with app.app_context():
        db.create_all()
        
        if not Category.query.first():
            categories = [
                Category(name="Драма"),
                Category(name="Комедія"),
                Category(name="Фантастика"),
                Category(name="Бойовик"),
                Category(name="Трилер")
            ]
            db.session.add_all(categories)
            db.session.commit()
            
            films = [
                Film(title="Втеча з Шоушенка", year=1994, rating=9.3, category_id=1),
                Film(title="Зелена миля", year=1999, rating=8.6, category_id=1),
                Film(title="Матриця", year=1999, rating=8.7, category_id=3),
                Film(title="Початок", year=2010, rating=8.8, category_id=3),
                Film(title="Темний лицар", year=2008, rating=9.0, category_id=4)
            ]
            db.session.add_all(films)
            db.session.commit()

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

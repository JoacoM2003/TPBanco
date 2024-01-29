from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://#usuario:#contraseña@#direccion:#puerto/banco"

db.init_app(app)
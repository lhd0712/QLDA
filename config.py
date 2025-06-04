import os

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost:3307/todoweb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

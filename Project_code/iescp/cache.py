from flask_caching import Cache
from app import app

cache = Cache()
cache.init_app(app)

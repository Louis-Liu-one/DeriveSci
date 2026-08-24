'''
Copyright (c) 2026 Zatursure  All rights reserved.
'''

from .auth import auth_bp, register_auth_api
from .probs import probs_bp, register_probs_api
from .articles import articles_bp, register_articles_api
from .images import images_bp, register_images_api
from .social import social_bp, register_social_api
from .helps import helps_bp


def register_all(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(probs_bp)
    app.register_blueprint(articles_bp)
    app.register_blueprint(images_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(helps_bp)
    register_auth_api(app)
    register_probs_api(app)
    register_articles_api(app)
    register_images_api(app)
    register_social_api(app)
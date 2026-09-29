import os
from flask import Flask, render_template
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, Product, Founder, GalleryImage
from routes import main_bp, contact_bp, admin_bp

load_dotenv()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html',
                               page_title='Page Not Found | Leaf Letang Enterprises'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html',
                               page_title='Something Went Wrong | Leaf Letang Enterprises'), 500

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        # Lightweight CSP compatible with inline styles needed for design
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )
        if os.environ.get('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response


    return app



def ensure_schema():
    """Add missing columns on SQLite without full migration tool."""
    from sqlalchemy import text, inspect
    try:
        insp = inspect(db.engine)
        if 'founders' in insp.get_table_names():
            cols = [c['name'] for c in insp.get_columns('founders')]
            if 'image' not in cols:
                with db.engine.begin() as conn:
                    conn.execute(text('ALTER TABLE founders ADD COLUMN image VARCHAR(255)'))
    except Exception:
        pass


def seed_data():
    """Seed initial products and founders if empty."""
    if Product.query.count() == 0:
        products = [
            Product(
                name='Duna',
                slug='duna',
                description='Traditional leaf bowls made from naturally sourced betel-nut leaves. Suitable for food service and traditional occasions.',
                image='products/duna-placeholder.svg',
                is_active=True,
                sort_order=1,
            ),
            Product(
                name='Tapari',
                slug='tapari',
                description='Leaf plates designed for food service, traditional occasions, events and everyday use.',
                image='products/tapari-placeholder.svg',
                is_active=True,
                sort_order=2,
            ),
            Product(
                name='Bulk / Custom Orders',
                slug='bulk-orders',
                description='Talk to us about larger quantities and business requirements for leaf-based food-service products.',
                image='products/bulk-placeholder.svg',
                is_active=True,
                sort_order=3,
            ),
        ]
        db.session.add_all(products)

    if Founder.query.count() == 0:
        founders = [
            Founder(name='Lekhnath Timilsina', role='Director', sort_order=1),
            Founder(name='Jas Bahadur Rai', role='', sort_order=2),
            Founder(name='Yuvraj Khatiwada', role='', sort_order=3),
            Founder(name='Roshan Paudel', role='', sort_order=4),
            Founder(name='Bijay Devkota', role='', sort_order=5),
            Founder(name='Subas Rai', role='', sort_order=6),
            Founder(name='Aatish Subedi', role='', sort_order=7),
        ]
        db.session.add_all(founders)

    db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)




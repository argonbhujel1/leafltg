from flask import Blueprint, render_template, current_app, send_from_directory, abort
from models import Product, GalleryImage, Founder, SiteSetting
from datetime import datetime
import os

main_bp = Blueprint('main', __name__)


@main_bp.context_processor
def inject_globals():
    return {
        'current_year': datetime.utcnow().year,
        'company_name': current_app.config.get('COMPANY_NAME'),
        'company_tagline': current_app.config.get('COMPANY_TAGLINE'),
        'company_location': current_app.config.get('COMPANY_LOCATION'),
        'company_phone': current_app.config.get('COMPANY_PHONE'),
        'company_email': current_app.config.get('COMPANY_EMAIL'),
        'company_facebook': current_app.config.get('COMPANY_FACEBOOK'),
        'company_instagram': current_app.config.get('COMPANY_INSTAGRAM'),
        'company_youtube': current_app.config.get('COMPANY_YOUTUBE'),
        'company_tiktok': current_app.config.get('COMPANY_TIKTOK'),
    }


@main_bp.route('/')
def index():
    products = Product.query.filter_by(is_active=True).order_by(Product.sort_order).limit(3).all()
    hero_setting = SiteSetting.query.filter_by(key='hero_image').first()
    hero_image = hero_setting.value if hero_setting and hero_setting.value else None
    return render_template('index.html',
                           page_title='Leaf Letang Enterprises | Sustainable Leaf Products from Nepal',
                           page_description='Leaf Letang Enterprises is a sustainable manufacturing enterprise in Letang, Morang, Nepal, producing biodegradable duna and tapari from betel-nut leaves.',
                           products=products,
                           hero_image=hero_image)


@main_bp.route('/about')
def about():
    founders = Founder.query.order_by(Founder.sort_order).all()
    if not founders:
        # Fallback static list if DB empty
        founders = [
            {'name': 'Lekhnath Timilsina', 'role': 'Director'},
            {'name': 'Jas Bahadur Rai', 'role': ''},
            {'name': 'Yuvraj Khatiwada', 'role': ''},
            {'name': 'Roshan Paudel', 'role': ''},
            {'name': 'Bijay Devkota', 'role': ''},
            {'name': 'Subas Rai', 'role': ''},
            {'name': 'Aatish Subedi', 'role': ''},
        ]
    return render_template('about.html',
                           page_title='Our Story | Leaf Letang Enterprises',
                           page_description='Learn about Leaf Letang Enterprises — founded by local entrepreneurs in Letang, Morang, transforming fallen betel-nut leaves into sustainable products since November 2021.',
                           founders=founders)


@main_bp.route('/products')
def products():
    products = Product.query.filter_by(is_active=True).order_by(Product.sort_order).all()
    return render_template('products.html',
                           page_title='Products | Leaf Letang Enterprises',
                           page_description='Discover biodegradable duna, tapari and leaf-based food-service products made from betel-nut leaves by Leaf Letang Enterprises in Nepal.',
                           products=products)


@main_bp.route('/process')
def process():
    return render_template('process.html',
                           page_title='Our Process | Leaf Letang Enterprises',
                           page_description='From fallen leaf collection to finished duna and tapari — the production process at Leaf Letang Enterprises in Letang, Nepal.')


@main_bp.route('/sustainability')
def sustainability():
    return render_template('sustainability.html',
                           page_title='Sustainability | Leaf Letang Enterprises',
                           page_description='Turning an agricultural by-product into opportunity — how Leaf Letang Enterprises creates value from fallen betel-nut leaves.')


@main_bp.route('/community')
def community():
    return render_template('community.html',
                           page_title='Community | Leaf Letang Enterprises',
                           page_description='Growing with our community — farmers, employment and local entrepreneurship around Leaf Letang Enterprises in Letang Municipality.')


@main_bp.route('/gallery')
def gallery():
    category = None
    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    categories = ['All', 'Factory', 'Products', 'Farmers', 'Production', 'Community']
    return render_template('gallery.html',
                           page_title='Gallery | Leaf Letang Enterprises',
                           page_description='Visual stories from the factory, products, farmers and community of Leaf Letang Enterprises.',
                           images=images,
                           categories=categories,
                           active_category='All')


@main_bp.route('/robots.txt')
def robots():
    return send_from_directory(current_app.static_folder, 'robots.txt')


@main_bp.route('/sitemap.xml')
def sitemap():
    pages = [
        {'loc': '/', 'priority': '1.0'},
        {'loc': '/about', 'priority': '0.9'},
        {'loc': '/products', 'priority': '0.9'},
        {'loc': '/process', 'priority': '0.8'},
        {'loc': '/sustainability', 'priority': '0.8'},
        {'loc': '/community', 'priority': '0.8'},
        {'loc': '/gallery', 'priority': '0.7'},
        {'loc': '/contact', 'priority': '0.9'},
    ]
    return render_template('sitemap.xml', pages=pages), 200, {'Content-Type': 'application/xml'}

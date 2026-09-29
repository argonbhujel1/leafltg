"""
Admin blueprint — private management only.
Never linked from public templates.
"""
from functools import wraps
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, session, current_app)
from werkzeug.security import check_password_hash
from models import db, ContactMessage, Product, GalleryImage, Founder, SiteSetting
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from werkzeug.utils import secure_filename
import os
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def _save_upload(file_storage, folder_key, prefix='file'):
    """Save uploaded image; returns filename or None."""
    if not file_storage or not getattr(file_storage, 'filename', None):
        return None
    original = secure_filename(file_storage.filename or '')
    if not original:
        return None
    ext = original.rsplit('.', 1)[-1].lower() if '.' in original else 'jpg'
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'})
    if ext not in allowed:
        return None
    upload_dir = current_app.config.get(folder_key)
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{prefix}-{uuid.uuid4().hex[:12]}.{ext}"
    file_storage.save(os.path.join(upload_dir, filename))
    return filename


def _delete_upload(filename, folder_key):
    if not filename:
        return
    upload_dir = current_app.config.get(folder_key)
    if not upload_dir:
        return
    path = os.path.join(upload_dir, filename)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass




def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please sign in to continue.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    slug = StringField('Slug', validators=[DataRequired(), Length(max=140)])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField(
        'Product image (PC or phone)',
        validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'gif'], 'Images only')],
    )
    is_active = BooleanField('Active', default=True)
    sort_order = StringField('Sort Order', default='0')
    submit = SubmitField('Save Product')


class GalleryForm(FlaskForm):
    title = StringField('Title', validators=[Optional(), Length(max=200)])
    image = FileField(
        'Select image (PC or phone)',
        validators=[
            FileRequired(message='Please select an image'),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'gif'], 'Images only (jpg, png, webp, gif)'),
        ],
    )
    category = SelectField('Category', choices=[
        ('Factory', 'Factory'),
        ('Products', 'Products'),
        ('Farmers', 'Farmers'),
        ('Production', 'Production'),
        ('Community', 'Community'),
    ])
    submit = SubmitField('Upload Image')


class FounderForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    role = StringField('Role', validators=[Optional(), Length(max=120)])
    image = FileField(
        'Photo (PC or phone)',
        validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'gif'], 'Images only')],
    )
    sort_order = StringField('Sort Order', default='0')
    submit = SubmitField('Save Founder')


class HeroForm(FlaskForm):
    image = FileField(
        'Hero image (PC or phone)',
        validators=[
            FileRequired(message='Please select an image'),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'gif'], 'Images only'),
        ],
    )
    submit = SubmitField('Upload Hero Image')


class SettingForm(FlaskForm):
    key = StringField('Key', validators=[DataRequired(), Length(max=100)])
    value = TextAreaField('Value', validators=[Optional()])
    submit = SubmitField('Save Setting')


@admin_bp.route('/')
def admin_root():
    """Unauthenticated → login; authenticated → dashboard."""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        expected_user = current_app.config.get('ADMIN_USERNAME') or 'admin'
        password_hash = current_app.config.get('ADMIN_PASSWORD_HASH')

        if not password_hash:
            if username == expected_user and password == 'change-me-on-first-login':
                session['admin_logged_in'] = True
                session.permanent = True
                flash('Signed in with temporary password. Set ADMIN_PASSWORD_HASH in production.', 'warning')
                return redirect(url_for('admin.dashboard'))
            flash('Invalid credentials. Configure ADMIN_PASSWORD_HASH.', 'error')
            return render_template('admin/login.html', form=form)

        if username == expected_user and check_password_hash(password_hash, password):
            session['admin_logged_in'] = True
            session.permanent = True
            flash('Welcome back.', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been signed out.', 'success')
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    total_messages = ContactMessage.query.count()
    unread = ContactMessage.query.filter_by(is_read=False).count()
    products_count = Product.query.count()
    gallery_count = GalleryImage.query.count()
    recent = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           total_messages=total_messages,
                           unread=unread,
                           products_count=products_count,
                           gallery_count=gallery_count,
                           recent=recent)


@admin_bp.route('/messages')
@login_required
def messages():
    msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=msgs)


@admin_bp.route('/messages/<int:msg_id>/read', methods=['POST'])
@login_required
def mark_read(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    flash('Message marked as read.', 'success')
    return redirect(url_for('admin.messages'))


@admin_bp.route('/messages/<int:msg_id>/delete', methods=['POST'])
@login_required
def delete_message(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'success')
    return redirect(url_for('admin.messages'))


@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    form = ProductForm()
    if form.validate_on_submit():
        slug = form.slug.data.strip()
        existing = Product.query.filter_by(slug=slug).first()
        if existing:
            flash('A product with this slug already exists.', 'error')
        else:
            filename = _save_upload(form.image.data, 'PRODUCTS_UPLOAD_FOLDER', 'product')
            # Store path relative to static/images/ for public templates
            image_path = f'products/{filename}' if filename else ''
            p = Product(
                name=form.name.data.strip(),
                slug=slug,
                description=form.description.data or '',
                image=image_path,
                is_active=form.is_active.data,
                sort_order=int(form.sort_order.data or 0),
            )
            db.session.add(p)
            db.session.commit()
            flash('Product added.', 'success')
            return redirect(url_for('admin.products'))
    products_list = Product.query.order_by(Product.sort_order).all()
    return render_template('admin/products.html', form=form, products=products_list, edit_product=None)


@admin_bp.route('/products/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(pid):
    p = Product.query.get_or_404(pid)
    form = ProductForm(obj=p)
    form.sort_order.data = str(p.sort_order)
    if request.method == 'GET':
        form.is_active.data = p.is_active
    if form.validate_on_submit():
        slug = form.slug.data.strip()
        clash = Product.query.filter(Product.slug == slug, Product.id != p.id).first()
        if clash:
            flash('Another product already uses this slug.', 'error')
        else:
            p.name = form.name.data.strip()
            p.slug = slug
            p.description = form.description.data or ''
            p.is_active = form.is_active.data
            p.sort_order = int(form.sort_order.data or 0)
            filename = _save_upload(form.image.data, 'PRODUCTS_UPLOAD_FOLDER', 'product')
            if filename:
                # delete old file if it was under products/
                if p.image and p.image.startswith('products/'):
                    _delete_upload(p.image.replace('products/', '', 1), 'PRODUCTS_UPLOAD_FOLDER')
                p.image = f'products/{filename}'
            db.session.commit()
            flash('Product updated.', 'success')
            return redirect(url_for('admin.products'))
    products_list = Product.query.order_by(Product.sort_order).all()
    return render_template('admin/products.html', form=form, products=products_list, edit_product=p)


@admin_bp.route('/products/<int:pid>/toggle', methods=['POST'])
@login_required
def toggle_product(pid):
    p = Product.query.get_or_404(pid)
    p.is_active = not p.is_active
    db.session.commit()
    flash(f'Product {"activated" if p.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/<int:pid>/delete', methods=['POST'])
@login_required
def delete_product(pid):
    p = Product.query.get_or_404(pid)
    if p.image and p.image.startswith('products/'):
        _delete_upload(p.image.replace('products/', '', 1), 'PRODUCTS_UPLOAD_FOLDER')
    db.session.delete(p)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/gallery', methods=['GET', 'POST'])
@login_required
def gallery():
    form = GalleryForm()
    if form.validate_on_submit():
        f = form.image.data
        original = secure_filename(f.filename or 'image')
        ext = original.rsplit('.', 1)[-1].lower() if '.' in original else 'jpg'
        if ext not in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'}):
            flash('File type not allowed.', 'error')
            return redirect(url_for('admin.gallery'))
        filename = f"{uuid.uuid4().hex[:12]}.{ext}"
        upload_dir = current_app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_dir, exist_ok=True)
        f.save(os.path.join(upload_dir, filename))
        g = GalleryImage(
            title=(form.title.data or '').strip(),
            image=filename,
            category=form.category.data,
        )
        db.session.add(g)
        db.session.commit()
        flash('Image uploaded successfully.', 'success')
        return redirect(url_for('admin.gallery'))
    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return render_template('admin/gallery.html', form=form, images=images)


@admin_bp.route('/gallery/<int:gid>/delete', methods=['POST'])
@login_required
def delete_gallery(gid):
    g = GalleryImage.query.get_or_404(gid)
    upload_dir = current_app.config.get('UPLOAD_FOLDER')
    if g.image and upload_dir:
        path = os.path.join(upload_dir, g.image)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
    db.session.delete(g)
    db.session.commit()
    flash('Image removed from gallery.', 'success')
    return redirect(url_for('admin.gallery'))


@admin_bp.route('/founders', methods=['GET', 'POST'])
@login_required
def founders():
    form = FounderForm()
    if form.validate_on_submit():
        filename = _save_upload(form.image.data, 'FOUNDERS_UPLOAD_FOLDER', 'founder')
        f = Founder(
            name=form.name.data.strip(),
            role=(form.role.data or '').strip(),
            image=filename,
            sort_order=int(form.sort_order.data or 0),
        )
        db.session.add(f)
        db.session.commit()
        flash('Founder added.', 'success')
        return redirect(url_for('admin.founders'))
    founders_list = Founder.query.order_by(Founder.sort_order).all()
    return render_template('admin/founders.html', form=form, founders=founders_list, edit_founder=None)


@admin_bp.route('/founders/<int:fid>/edit', methods=['GET', 'POST'])
@login_required
def edit_founder(fid):
    f = Founder.query.get_or_404(fid)
    form = FounderForm(obj=f)
    form.sort_order.data = str(f.sort_order)
    if form.validate_on_submit():
        f.name = form.name.data.strip()
        f.role = (form.role.data or '').strip()
        f.sort_order = int(form.sort_order.data or 0)
        filename = _save_upload(form.image.data, 'FOUNDERS_UPLOAD_FOLDER', 'founder')
        if filename:
            _delete_upload(f.image, 'FOUNDERS_UPLOAD_FOLDER')
            f.image = filename
        db.session.commit()
        flash('Founder updated.', 'success')
        return redirect(url_for('admin.founders'))
    founders_list = Founder.query.order_by(Founder.sort_order).all()
    return render_template('admin/founders.html', form=form, founders=founders_list, edit_founder=f)


@admin_bp.route('/founders/<int:fid>/delete', methods=['POST'])
@login_required
def delete_founder(fid):
    f = Founder.query.get_or_404(fid)
    _delete_upload(f.image, 'FOUNDERS_UPLOAD_FOLDER')
    db.session.delete(f)
    db.session.commit()
    flash('Founder removed.', 'success')
    return redirect(url_for('admin.founders'))




@admin_bp.route('/homepage', methods=['GET', 'POST'])
@login_required
def homepage():
    """Upload/replace the public homepage hero image."""
    form = HeroForm()
    setting = SiteSetting.query.filter_by(key='hero_image').first()
    current_hero = setting.value if setting else None

    if form.validate_on_submit():
        f = form.image.data
        original = secure_filename(f.filename or 'hero')
        ext = original.rsplit('.', 1)[-1].lower() if '.' in original else 'jpg'
        allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'})
        if ext not in allowed:
            flash('File type not allowed.', 'error')
            return redirect(url_for('admin.homepage'))

        upload_dir = current_app.config.get('HERO_UPLOAD_FOLDER')
        os.makedirs(upload_dir, exist_ok=True)

        # Remove old file if present
        if current_hero:
            old_path = os.path.join(upload_dir, current_hero)
            if os.path.isfile(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        filename = f"hero-{uuid.uuid4().hex[:10]}.{ext}"
        f.save(os.path.join(upload_dir, filename))

        if setting:
            setting.value = filename
        else:
            db.session.add(SiteSetting(key='hero_image', value=filename))
        db.session.commit()
        flash('Hero image updated. It now appears on the public homepage.', 'success')
        return redirect(url_for('admin.homepage'))

    return render_template('admin/homepage.html', form=form, current_hero=current_hero)


@admin_bp.route('/homepage/remove', methods=['POST'])
@login_required
def homepage_remove_hero():
    setting = SiteSetting.query.filter_by(key='hero_image').first()
    if setting and setting.value:
        upload_dir = current_app.config.get('HERO_UPLOAD_FOLDER')
        path = os.path.join(upload_dir, setting.value)
        if os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
        db.session.delete(setting)
        db.session.commit()
        flash('Hero image removed. Placeholder will show again.', 'success')
    return redirect(url_for('admin.homepage'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        key = form.key.data.strip()
        existing = SiteSetting.query.filter_by(key=key).first()
        if existing:
            existing.value = form.value.data or ''
            flash('Setting updated.', 'success')
        else:
            db.session.add(SiteSetting(key=key, value=form.value.data or ''))
            flash('Setting added.', 'success')
        db.session.commit()
        return redirect(url_for('admin.settings'))
    settings_list = SiteSetting.query.order_by(SiteSetting.key).all()
    return render_template('admin/settings.html', form=form, settings=settings_list)


@admin_bp.route('/settings/<int:sid>/delete', methods=['POST'])
@login_required
def delete_setting(sid):
    s = SiteSetting.query.get_or_404(sid)
    db.session.delete(s)
    db.session.commit()
    flash('Setting deleted.', 'success')
    return redirect(url_for('admin.settings'))

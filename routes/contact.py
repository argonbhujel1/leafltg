from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional
from models import db, ContactMessage

contact_bp = Blueprint('contact', __name__)


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=40)])
    inquiry_type = SelectField('Inquiry Type', choices=[
        ('Product Inquiry', 'Product Inquiry'),
        ('Bulk Order', 'Bulk Order'),
        ('Business Partnership', 'Business Partnership'),
        ('Distribution', 'Distribution'),
        ('Export Inquiry', 'Export Inquiry'),
        ('General Inquiry', 'General Inquiry'),
    ], validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=5000)])
    submit = SubmitField('Send Message')


@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=(form.phone.data or '').strip() or None,
            inquiry_type=form.inquiry_type.data,
            message=form.message.data.strip(),
        )
        db.session.add(msg)
        db.session.commit()
        flash('Thank you. Your message has been sent successfully. We will get back to you soon.', 'success')
        return redirect(url_for('contact.contact'))
    return render_template('contact.html',
                           page_title="Let's Work Together | Leaf Letang Enterprises",
                           page_description='Contact Leaf Letang Enterprises for product inquiries, bulk orders, partnerships and distribution of biodegradable leaf products.',
                           form=form)

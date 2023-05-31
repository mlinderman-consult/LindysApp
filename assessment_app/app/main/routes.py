from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, login_required, current_user, logout_user
from . import main
from .. import db
from ..models import Admin, Assessment
from .forms import LoginForm, UploadForm
import pandas as pd
import uuid
import logging
from airtable import Airtable

AIRTABLE_API_KEY = 'your_airtable_api_key'
AIRTABLE_BASE_KEY = 'your_airtable_base_key'
AIRTABLE_TABLE_NAME = 'your_airtable_table_name'

logger = logging.getLogger(__name__)

@main.errorhandler(404)
def page_not_found(e):
    # Render a custom 404 error page
    return render_template('404.html'), 404

def process_file(file):
    try:
        data = pd.read_csv(file)  # if it's a CSV file
        # data = pd.read_excel(file)  # if it's an Excel file
        return data.to_dict()
    except Exception as e:
        logger.exception("Error occurred while processing the file")
        # Send email notification to developers about the error
        # ...
        raise

def generate_assessment(questions, url, pin):
    airtable = Airtable(AIRTABLE_BASE_KEY, AIRTABLE_TABLE_NAME, api_key=AIRTABLE_API_KEY)
    for question in questions:
        airtable.insert(question)
    new_assessment = Assessment(url=url, pin=pin)
    db.session.add(new_assessment)
    db.session.commit()

def generate_unique_url():
    return str(uuid.uuid4())

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        questions = process_file(file)
        if not questions:
            # Render an error page if the list of questions is empty
            return render_template('error.html', message='The file does not contain any questions.')
        pin = form.pin.data
        url = generate_unique_url()
        generate_assessment(questions, url, pin)
        flash('Assessment created successfully! The URL is: ' + url)
        return redirect(url_for('main.dashboard'))
    return render_template('dashboard.html', form=form)

@main.route('/assessment/<string:url>', methods=['GET', 'POST'])
def assessment(url):
    assessment = Assessment.query.filter_by(url=url).first()
    if not assessment:
        # Render a custom 404 error page if the requested assessment does not exist
        return render_template('404.html'), 404
    if request.method == 'POST':
        entered_pin = request.form.get('pin')
        if entered_pin != assessment.pin:
            # Render an error page if the entered PIN is incorrect
            return render_template('error.html', message='Incorrect PIN. Please try again.')
        # Process the assessment
        # ...
    return render_template('assessment.html', url=url)

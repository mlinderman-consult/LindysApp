from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

class UploadForm(FlaskForm):
    file = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['csv', 'xlsx'], 'CSV/XLSX files only!')
    ])
    submit = SubmitField('Upload')

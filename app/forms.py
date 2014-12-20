from flask_wtf import Form
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired
from wtforms import widgets

class MonkeyForm(Form):
    name = StringField('name', default=None)
    age = IntegerField('age', default=0)
    email = StringField('email', default=' ')

class SelectOneMonkeyForm(Form):
    example = SelectField()

class SelectManyMonkeyForm(Form):
    example = SelectMultipleField(
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False))

from decimal import Decimal
from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, IntegerField, DecimalField, HiddenField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from wtforms import Form

from flask_wtf.file import FileField, FileRequired

from flask_pagedown.fields import PageDownField
from ..models import Role, User


class FileUploadForm(FlaskForm):
    purch_file = FileField('Select the Comic Collector Purchase Export File to Upload', validators=[FileRequired()])
    default_disc_rate = StringField('Default Discount Percentage')
    tax_rate = StringField('Sales Tax Rate')
    pmt_meth = StringField('Payment Method')
    submit = SubmitField('Upload File')


class InvoiceLineForm(Form):
    line_id = HiddenField('line_id', default=0)
    file_id = HiddenField('file_id', default=0)
    seq = HiddenField('seq', default=0)
    ser_id = HiddenField('ser_id', default=0)
    publisher = HiddenField('publisher', default="publisher")
    series = HiddenField('series', default="series")
    issue = HiddenField('issue', default="issue")
    iss_full = HiddenField('iss_full', default="issue-full")
    iss_num = HiddenField('iss_num', default=0)
    iss_ext = HiddenField('iss_ext', default="issue-extension")
    edition = HiddenField('edition', default="eddition")
    cvr_dt = HiddenField('cvr_dt', default="cover-date")
    cvr_dt_year = HiddenField('cvr_dt_year', default=0)
    cvr_dt_month = HiddenField('cvr_dt_month', default=0)
    cvr_dt_day = HiddenField('cvr_dt_day', default=0)
    cover_price = HiddenField('cover_price', default=Decimal('0.00'))
    owner = HiddenField('owner', default="owner")
    purch_dt = HiddenField('purch_dt', default=date(9999,1,1))
    store = HiddenField('store', default="store")
    trans_num = HiddenField('trans_num', default="transaciton-number")
    release_dt = HiddenField('release_dt', default=date(9999,1,1))
    crossover = HiddenField('crossover', default="crossover")
    story_arc = HiddenField('story_arc', default="story-arc")
    title = HiddenField('title', default="title")
    sub_title = HiddenField('sub_title', default="sub-title")
    desc = StringField('Item Description', default='item-description')                              # read only
    str_seq = IntegerField('Sales Receipt Sequence', default='0')
    str_cvr_price = DecimalField('Store Cover Price', places=2, default=Decimal('0.00'))
    str_item_disc = DecimalField('Store Item Discount Amount', places=2, default=Decimal('0.00'))
    str_disc_price = DecimalField('Store Discount Item Price', places=2, default=Decimal('0.00'))   # read only
    taxable_ind = StringField('Taxable (Y/N)', default='N')
    str_item_tax = DecimalField('Item Tax Amount', places=2, default=Decimal('0.00'))               # read only
    str_tax_adj = DecimalField('Item Tax Adjustment', places=2, default=Decimal('0.00'))
    str_tax_paid = DecimalField('Item Tax Paid', places=2, default=Decimal('0.00'))                 # read only
    purch_price = DecimalField('Item Purchase Price', places=2, default=Decimal('0.00'))            # read only


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    body = StringField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')

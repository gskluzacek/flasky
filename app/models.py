from datetime import date, datetime
from decimal import Decimal
# import os.path
import csv
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager

from jinja2 import FileSystemLoader, Environment


DEFAULT_DISCOUNT = Decimal('0.20')
DEC_PERC = Decimal('1.00')


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class File(db.Model):
    __tablename__ = 'files'

    file_id            = db.Column(db.Integer,       primary_key=True)
    crt_dt             = db.Column(db.TIMESTAMP,     nullable=False, default=db.func.now(), onupdate=db.func.now())
    status             = db.Column(db.String(  25),  nullable=False, default='UPLOADED')
    file_path          = db.Column(db.String(  500), nullable=False)
    orig_file          = db.Column(db.String(  100), nullable=False)
    purch_dt           = db.Column(db.Date)
    store              = db.Column(db.String(  100))
    trans_num          = db.Column(db.String(   40))
    # TODO: remove default discount once we have the Web GUI collecting it
    default_discount   = db.Column(db.Numeric(3, 2), nullable=False, default=DEFAULT_DISCOUNT)
    tax_rate           = db.Column(db.Numeric(6, 5))
    pmt_meth           = db.Column(db.String(   50))
    trans_total        = db.Column(db.Numeric(5, 2))
    sub_total          = db.Column(db.Numeric(5, 2))
    tax_total          = db.Column(db.Numeric(5, 2))
    discount_total     = db.Column(db.Numeric(5, 2))
    nei_trans_total    = db.Column(db.Numeric(5, 2))
    nei_sub_total      = db.Column(db.Numeric(5, 2))
    nei_tax_total      = db.Column(db.Numeric(5, 2))
    nei_discount_total = db.Column(db.Numeric(5, 2))
    notes              = db.Column(db.Text)
    lines              = db.relationship("Line", backref='file', order_by='Line.seq')

    @staticmethod
    def load_file(file_path, orig_file, default_discount_rate=0, tax_rate=0, pmt_meth=None):
        dbfo = File(file_path=file_path, orig_file=orig_file, tax_rate=tax_rate, pmt_meth=pmt_meth)

        fh = open(file_path)
        dialect = csv.Sniffer().sniff(fh.read(1024))
        fh.seek(0)
        reader = csv.DictReader(fh, dialect=dialect)

        # TODO: add logic to read purch_dt from the web-form and then figure out how to default the db col
        # TODO: add logic to read store from the web-form and then figure out how to default the db col
        # TODO: add logic to read trans_num from the web-form and then figure out how to default the db col
        # yes I know I'm setting the cover date to the publication date - due to an issue with labels in CC
        # yes I know I'm setting the release date to the cover date - due to an issue with labels in CC

        for cnt, row in enumerate(reader, start=1):
            dblo = Line(
                default_discount_rate,
                seq=cnt,
                publisher=row['Publisher'],
                series=row['Series'],
                iss_full=row['Issue'],
                iss_num=row['Issue No.'],
                iss_ext=row['Issue Ext'],
                edition=row['Edition'],
                cvr_dt=row['Publication Date'],
                cover_price=row['Cover Price'],
                owner=row['Owner'],
                purch_dt=row['Purchase Date'],
                store=row['Store'],
                trans_num=row['Purchase Batch Id'],
                release_dt=row['Cover Date'],
                crossover=row['Crossover'],
                story_arc=row['Story Arc'],
                title=row['Title'],
                sub_title=row['Sub Title']
            )
            dbfo.lines.append(dblo)

        fh.close()

        if len(dbfo.lines) != 0:
            ln1 = dbfo.lines[0]

            dbfo.purch_dt = ln1.purch_dt
            dbfo.store = ln1.store
            dbfo.trans_num = ln1.trans_num

            db.session.add(dbfo)
            db.session.commit()

            return dbfo
        else:
            # TODO: add logic to handle the use case where the input file is empty
            return None

    def generate_invoice(self):
        print("=" * 125)
        print("Purchase Date: {0:25s} Trans #: {1:44s} Store: {2:s}".format(
            str(self.purch_dt or ''),
            self.trans_num or '',
            self.store or ''
        ))
        print("=" * 125)
        print("")
        print("")

        print("{0:50s} {1:4s} {2:20s} {3:20s} {4:3s} {5:11s} {6:11s}".format(
            'Title',
            'Year',
            'Notes',
            'Cover Date',
            'Num',
            'Cover Price',
            'Purch Price'
        ))
        print("{0:50s} {1:4s} {2:20s} {3:20s} {4:3s} {5:11s} {6:11s}".format(
            '-' * 50,
            '-' * 4,
            '-' * 20,
            '-' * 20,
            '-' * 3,
            '-' * 11,
            '-' * 11
        ))

        tot_cvr_price = Decimal('0')
        tot_purch_price = Decimal('0')
        for line in self.lines:
            tot_cvr_price += line.cover_price
            tot_purch_price += line.purch_price

            print("{0:50s} {1:4s} {2:20s} {3:20s} {4:>3s} {5:>11s} {6:>11s}".format(
                line.series or '',
                '',  # year
                line.notes or '',
                str(line.cvr_dt_month).rjust(2, '0') + '/' + str(line.cvr_dt_year),
                str(line.iss_num or ''),
                str(line.cover_price or ''),
                str(line.purch_price or '')
            ))

        print("")
        print("{0:101s} {1:11s} {2:11s}".format('', '-' * 11, '-' * 11))
        print("Payment Method: {0:50s} {1:>34s} {2:>11s} {3:>11s}".format(
            self.pmt_meth or '',
            "TOTAL",
            str(tot_cvr_price),
            str(tot_purch_price)
        ))

    def get_invoice_data(self):
        cols = [
            'Title',
            'Year',
            'Notes',
            'Cover Date',
            'Num',
            'Cover Price',
            'Purch Price'
        ]

        hdr_data = {
            'purch_dt': str(self.purch_dt.strftime('%d-%b-%Y').upper() or ''),
            'trans_num': self.trans_num or '',
            'store': self.store or '',
            'pmt_meth': self.pmt_meth or '',
            'trans_total': self.trans_total or '',
            'nei_trans_total': self.nei_trans_total or '',
        }

        tot_cvr_price = Decimal('0')
        tot_purch_price = Decimal('0')
        dtl_data = []
        for line in self.lines:
            tot_cvr_price += line.cover_price
            tot_purch_price += line.purch_price

            dtl_data.append({
                'series': line.series or '',
                'year': '',  # year
                'notes': line.notes or '',
                'cover_dt': date(line.cvr_dt_year or 9999, line.cvr_dt_month or 1, 1).strftime('%b-%Y').upper(),
                'issue': str(line.iss_num or ''),
                'cover_price': str(line.cover_price or ''),
                'purch_price': str(line.purch_price or '')
            })

        hdr_data['tot_cover_price'] = tot_cvr_price
        hdr_data['tot_purch_price'] = tot_purch_price

        return {'hdr': hdr_data, 'cols': cols, 'dtl': dtl_data}


    def generate_html_invoice(self):
        loader = FileSystemLoader('')
        env = Environment(loader=loader)
        inv_template = env.get_template('invoice_template.html')

        inv_template.stream(self.get_invoice_data()).dump(
            'output/INV_{0}_{1}.html'.format(self.store, self.purch_dt)
        )

    def __repr__(self):
        return '<File file_id: {file_id!r} crt_dt: {crt_dt!r} file_path: {file_path!r}>'.format(
            file_id=self.file_id, crt_dt=self.crt_dt, file_path=self.file_path
        )


class Line(db.Model):
    __tablename__ = 'lines'

    line_id           = db.Column(db.Integer,       primary_key=True)
    file_id           = db.Column(db.Integer,       db.ForeignKey('files.file_id'))
    seq               = db.Column(db.Integer,       nullable=False)
    ser_id            = db.Column(db.Integer)
    publisher         = db.Column(db.String(  150), nullable=False)
    series            = db.Column(db.String(  150), nullable=False)
    issue             = db.Column(db.String(   20))
    iss_full          = db.Column(db.String(   20), nullable=False)
    iss_num           = db.Column(db.Integer,       nullable=False)
    iss_ext           = db.Column(db.String(   10))
    edition           = db.Column(db.String(  150))
    cvr_dt            = db.Column(db.String(   20))
    cvr_dt_year       = db.Column(db.Integer)
    cvr_dt_month      = db.Column(db.Integer)
    cvr_dt_day        = db.Column(db.Integer)
    cover_price       = db.Column(db.Numeric(5, 2))
    purch_price       = db.Column(db.Numeric(5, 2))
    owner             = db.Column(db.String(  100))
    purch_dt          = db.Column(db.Date)
    store             = db.Column(db.String(  100))
    trans_num         = db.Column(db.String(   40))
    release_dt        = db.Column(db.Date)
    crossover         = db.Column(db.String(  100))
    story_arc         = db.Column(db.String(  100))
    title             = db.Column(db.String(  100))
    sub_title         = db.Column(db.String(  100))
    str_seq           = db.Column(db.Integer)
    str_cvr_price     = db.Column(db.Numeric(5, 2))
    str_item_disc     = db.Column(db.Numeric(5, 2))
    str_disc_price    = db.Column(db.Numeric(5, 2))
    taxable_ind       = db.Column(db.String(    1))
    str_item_tax      = db.Column(db.Numeric(4, 2))
    str_tax_adj       = db.Column(db.Numeric(3, 2))
    str_tax_paid      = db.Column(db.Numeric(4, 2))
    notes             = db.Column(db.Text)

    # wrapper function to specifically parse the the comic collector cover date
    # into year, month and day components
    # returns None for all values if input is the empty string
    @staticmethod
    def cc_cover_date_parse(cc_cvr_date_str):
        if cc_cvr_date_str:
            return Line.cc_twofmt_date_parse(cc_cvr_date_str)
        else:
            return None, None, None

    # this function will return a date object or None if input is the empty string
    # it takes a comic collector date string as input
    #   a comic collector date string can be in 1 of 2 formats
    #     format 1: Month day, Year              e.g.: July 4, 1776
    #     format 2: Month Year (no day value)    e.g.: September 2001
    # if the input is in format 2, then the day of the returned date object will be set to 1
    @staticmethod
    def cc_date_parse(cc_date_str):
        if cc_date_str:
            yr, mon, day = Line.cc_twofmt_date_parse(cc_date_str)
            return date(yr, mon, day or 1)
        else:
            return None

    # this function will return integer values for the year, month, day
    # it takes a comic collector date string as input
    #   a comic collector date string can be in 1 of 2 formats
    #     format 1: Month day, Year              e.g.: July 4, 1776
    #     format 2: Month Year (no day value)    e.g.: September 2001
    # if the input is in format 2, then the day will be set to 1
    @staticmethod
    def cc_twofmt_date_parse(date_str):
        day = 0
        sub_fld_cnt = len(date_str.split())
        if sub_fld_cnt == 2:
            dt = datetime.strptime(date_str, '%B %Y').date()
        elif sub_fld_cnt == 3:
            dt = datetime.strptime(date_str, '%B %d, %Y').date()
            day = int(dt.strftime('%d'))
        else:
            # TODO: if the input is not in format 1 or 2 (e.g., the empty string or None, etc.) this function should thrown an exception
            # unsupported format of the input date from comic collector
            return None, None, None
        mon = int(dt.strftime('%m'))
        yr = int(dt.strftime('%Y'))

        return yr, mon, day

    # this function will return a Decimal Object or None if the input is the empty string (or just a '$')
    @staticmethod
    def cc_price_parse(cc_price_string):
        cover_price = cc_price_string.lstrip('$')
        return Decimal(cover_price) if cover_price else None

    # this function will return a Decimal Object of None if the cover_price is None
    @staticmethod
    def discounted_purch_price(cover_price, discount_rate):
        if cover_price:
            return (cover_price - (discount_rate * cover_price)).quantize(DEC_PERC)
        else:
            return None

    def __init__(self, default_disc_rate, **kwargs):

        cover_price = Line.cc_price_parse(kwargs.get('cover_price'))
        cvr_dt_year, cvr_dt_month, cvr_dt_day = Line.cc_cover_date_parse(kwargs.get('cvr_dt'))

        super(Line, self).__init__(
            seq=kwargs.get('seq', 0),
            ser_id=kwargs.get('ser_id'),
            publisher=kwargs.get('publisher') or None,
            series=kwargs.get('series') or None,
            issue=kwargs.get('issue'),
            iss_full=kwargs.get('iss_full') or None,
            iss_num=kwargs.get('iss_num') or None,
            iss_ext=kwargs.get('iss_ext') or None,
            edition=kwargs.get('edition') or None,
            cvr_dt=kwargs.get('cvr_dt') or None,
            cvr_dt_year=cvr_dt_year,
            cvr_dt_month=cvr_dt_month,
            cvr_dt_day=cvr_dt_day,
            cover_price=cover_price,
            purch_price=Line.discounted_purch_price(cover_price, default_disc_rate),
            owner=kwargs.get('owner') or None,
            purch_dt=Line.cc_date_parse(kwargs.get('purch_dt')),
            store=kwargs.get('store') or None,
            trans_num=kwargs.get('trans_num') or None,
            release_dt=Line.cc_date_parse(kwargs.get('release_dt')),
            crossover=kwargs.get('crossover')[:100] or None,
            story_arc=kwargs.get('story_arc')[:100] or None,
            title=kwargs.get('title')[:100] or None,
            sub_title=kwargs.get('sub_title')[:100] or None,
            str_seq=kwargs.get('str_seq'),
            str_cvr_price=kwargs.get('str_cvr_price'),
            str_item_disc=kwargs.get('str_item_disc'),
            str_disc_price=kwargs.get('str_disc_price'),
            taxable_ind=kwargs.get('taxable_ind'),
            str_item_tax=kwargs.get('str_item_tax'),
            str_tax_adj=kwargs.get('str_tax_adj'),
            str_tax_paid=kwargs.get('str_tax_paid'),
            notes=kwargs.get('notes')
        )

    def __repr__(self):
        return ('<Line line_id: {line_id!r} file_id: {file_id!r} seq: {seq!r} publisher: {publisher!r} '
                'series: {series!r} iss_full: {iss_full!r}>'.format(
            line_id=self.line_id,
            file_id=self.file_id,
            seq=self.seq,
            publisher=self.publisher,
            series=self.series,
            iss_full=self.iss_full
        ))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)

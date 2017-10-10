from decimal import Decimal
from os import path
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import main
from .forms import FileUploadForm, EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm, InvoiceLineForm
from .. import db
from ..models import Permission, Role, User, File, Post, Comment
from ..decorators import admin_required, permission_required

from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        uploaded_file_obj = form.purch_file.data
        uploaed_filename = secure_filename(uploaded_file_obj.filename)
        save_location = path.join(path.dirname(current_app.root_path), 'uploads', uploaed_filename)
        uploaded_file_obj.save(save_location)
        dm_file = File.load_file(save_location, uploaded_file_obj.filename, Decimal(form.default_disc_rate.data), Decimal(form.tax_rate.data), form.pmt_meth.data)
        flash('The file (id: {0}) has been received!'.format(dm_file.file_id))
        return redirect(url_for('.upload'))
    return render_template('file_upload.html', form=form)


@main.route('/invoice1/<file_id>', methods=['GET', 'POST'])
def view_invoice1(file_id):
    # logic for displaying the form
    if request.method == 'GET':
        file = File.query.get_or_404(file_id)
        line_cnt = len(file.lines)
        # Dynamical create a Form Class with the correct number of entries set to the number of lines in the file
        class InvoiceForm(FlaskForm):
            pass
        # add a FieldList field to the Dynamic Form Class setting the min/max entries of the
        # InvoiceLineForm subform to the count of the number of lines in the file
        InvoiceForm.lines =  FieldList(
            FormField(
                InvoiceLineForm,label='Invoice Line'
            ),
            label='Invoice Lines', min_entries=line_cnt, max_entries=line_cnt
        )
        InvoiceForm.total_str_cvr_price = StringField('Total Store Cover Price', default=0)
        InvoiceForm.total_str_item_disc = StringField('Total Store Item Discount', default=0)
        InvoiceForm.total_str_disc_price = StringField('Total Store Dicounted Item Price', default=0)
        InvoiceForm.total_str_item_tax = StringField('Total Store Item Tax', default=0)
        InvoiceForm.total_str_tax_adj = StringField('Total Tax Adjustment', default=0)
        InvoiceForm.total_str_tax_paid = StringField('Total Store Adjusted Tax', default=0)
        InvoiceForm.total_purch_price = StringField('Total Purchase Price', default=0)
        form = InvoiceForm()

        # populate the values for each SubForm on the dynamic form class
        for subform in form.lines:
            for subfield in subform:
                # don't set the value if the field type is CSRFTokenField
                if subfield.type != 'CSRFTokenField':
                    # by splitting the name of the subfield, we can get the index and subform field name
                    # the contariner field name (1st item) is discarded
                    unused_lines_field_name, line_index, field_name = subfield.name.split('-')
                    val = getattr(file.lines[int(line_index)], field_name, None) or subfield.data
                    subfield.data = val
            subform.desc.data = (
                '[{0}] {1} #{2} {3} ${4}'.format(
                subform.seq.data,
                subform.series.data,
                subform.iss_full.data,
                subform.cvr_dt.data,
                subform.cover_price.data
            ))
        return render_template('invoice1.html', form=form, file_dbm=file)
    # logic for processing the form data
    else:
        pass

@main.route('/invoice/<file_id>')
def view_invoice(file_id):
    file = File.query.get_or_404(file_id)
    # {'hdr': hdr_data, 'cols': cols, 'dtl': dtl_data}
    return render_template('view_invoice.html', **file.get_invoice_data())


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

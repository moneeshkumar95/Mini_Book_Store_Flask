from . import *
from .models import *
from .forms import *
from flask import redirect, url_for, render_template, flash, request
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        create_user = User(username=form.username.data,
                           email=form.email.data,
                           password=form.password1.data)
        db.session.add(create_user)
        db.session.commit()
        login_user(create_user)
        flash(f'Account created successfully, Logged in as {create_user.username}', category='success')
        return redirect(url_for('market'))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Successful logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('Successful Logged out!', category='info')
    return redirect(url_for('home_page'))

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market')
@login_required
def market():
    items = Item.query.filter_by(owner=None)
    owned_items = Item.query.filter_by(owner=current_user.id)
    return render_template('market.html', items=items, owned_items=owned_items)

@app.route('/item-details/<int:id>')
def details_page(id):
    items = Item.query.filter_by(id=id)
    return render_template('details.html', items=items)

@app.route('/purchase/<int:id>', methods=['GET', 'POST'])
def purchase_page(id):
    items = Item.query.filter_by(id=id)
    purchase_form = PurchaseItemForm()

    if request.method == "POST":
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
                return redirect(url_for('market'))
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')

    return render_template('purchase.html', items=items, purchase_form=purchase_form)

@app.route('/sell/<int:id>', methods=['GET', 'POST'])
def sell_page(id):
    items = Item.query.filter_by(id=id)
    selling_form = SellItemForm()
    owned_items = Item.query.filter_by(owner=current_user.id, id=id)
    if request.method == "POST":
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
                return redirect(url_for('market'))
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')
    else:
        return render_template('sell.html', items=items, selling_form=selling_form, owned_items=owned_items)
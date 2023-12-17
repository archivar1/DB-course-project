from app import app
from flask import request, render_template, redirect, flash, url_for
import psycopg, os
from forms import RegistrationForm, EditUserForm, AddObjectForm, LoginForm, EditObjectForm, Search, CloseDeal
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import current_user, login_user, logout_user, login_required
from user import User
import datetime


def get_db_connection():
    try:
        con = psycopg.connect(user=app.config['DB_USER'],
                              host=app.config['DB_SERVER'],
                              port=app.config['DB_PORT'],
                              password=app.config['DB_PASSWORD'],
                              dbname=app.config['DB_NAME'])
        return con
    except:
        print(ConnectionError)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


@app.route('/', methods=['GET', 'POST'])
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM object')
    objects = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('main.html', objects=objects)


@app.route('/object/<int:object_id>', methods=['GET', 'POST'])
def object(object_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT * FROM type_of_object INNER JOIN object ON type_of_object.id=object.id_type_of_object INNER JOIN adress ON adress.id=object.id_adress INNER JOIN type_of_deal ON type_of_deal.id=object.id_type_of_deal WHERE object.id=%s',
        (object_id,))
    object_info = cur.fetchall()
    cur.execute(
        'SELECT first_name, second_name, phone_num FROM "user" INNER JOIN deal ON "user".id=deal.id_first_user INNER JOIN object ON object.id=deal.id_object WHERE id_object = %s',
        (object_id,))
    user_info = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('object_details.html', object_info=object_info, user_info=user_info)


@app.route('/account')
def account():
    if not current_user.is_authenticated:
        return redirect('/')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "user" WHERE id = %s', (current_user.id,))
    user = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('account.html', user=user)


@app.route('/add_ad', methods=['GET', 'POST'])
def add_ad():
    if current_user.role != 'realtor':
        return redirect('/')
    add_ad_form = AddObjectForm()
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT id, name FROM type_of_object")
        options1 = cur.fetchall()
        cur.execute("SELECT id, name FROM type_of_deal")
        options2 = cur.fetchall()
    if add_ad_form.validate_on_submit() and request.method == "POST":
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            options3 = request.form['type_of_object']
            options4 = request.form['type_of_deal']
            adress = request.form['adress']
            cur.execute('INSERT INTO adress (name) VALUES (%s)', [adress])
            cur.execute(
                'INSERT INTO object (id_type_of_object, id_type_of_deal, id_adress, room_num, square, price, floar_num, date_build, material_type, distance_to_subway, district, description, date_of_sale, image) VALUES (%s, %s, (SELECT id FROM adress WHERE name  = %s LIMIT 1 ) , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                [options3, options4, adress, request.form['room_num'], request.form['square'], request.form['price'],
                 request.form['floar_num'],
                 request.form['date_build'], request.form['material_type'], request.form['distance_to_subway'],
                 request.form['district'], request.form['description'], datetime.datetime.now(),
                 filename])
            cur.execute("SELECT lastval()")
            ad_id = cur.fetchone()[0]
            cur.execute("SELECT id FROM object")
            cur.execute('INSERT INTO deal (id_object, id_first_user, id_type_of_deal) VALUES (%s, %s, %s)',
                        [ad_id, current_user.id, options4])
            conn.commit()
            cur.close()
            conn.close()
            return redirect('/')
    return render_template('add_ad.html', title='Новое объявление', form=add_ad_form, options1=options1,
                           options2=options2)


@app.route('/edit_object/<int:object_id>', methods=['GET', 'POST'])
@login_required
def edit_object(object_id):
    conn = get_db_connection()
    cur = conn.cursor()
    adress, room_num, square, price, floar_num, date_build, material_type, distance_to_subway, district, description = cur.execute(
        'SELECT name, room_num, square, price, floar_num, date_build, material_type, distance_to_subway, district, description FROM object INNER JOIN adress ON object.id_adress=adress.id WHERE object.id = %s',
        (object_id,)).fetchone()
    form = EditObjectForm(adress=adress, room_num=room_num, square=square, floar_num=floar_num, price=price,
                          date_build=date_build,
                          material_type=material_type, distance_to_subway=distance_to_subway, district=district,
                          description=description)
    if request.method == "GET":
        cur.execute("SELECT id, name FROM type_of_object")
        options1 = cur.fetchall()
        cur.execute("SELECT id, name FROM type_of_deal")
        options2 = cur.fetchall()

    if form.validate_on_submit() and request.method == "POST":
        img = request.files['image']
        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            options1 = request.form['type_of_object']
            options2 = request.form['type_of_deal']
            adress = request.form['adress']
            cur.execute("SELECT id_adress FROM object WHERE id=%s", (object_id,))
            options3 = cur.fetchall()[0][0]
            cur.execute('UPDATE adress SET name=%s WHERE id =%s', [adress, options3])
            cur.execute(
                'UPDATE object SET id_type_of_object=%s, id_type_of_deal=%s, room_num=%s, square=%s, price=%s, floar_num=%s, date_build=%s, material_type=%s, distance_to_subway=%s, district=%s, description=%s, date_of_sale=%s, image=%s WHERE id =%s',
                [options1, options2, request.form['room_num'], request.form['square'], request.form['price'],
                 request.form['floar_num'],
                 request.form['date_build'], request.form['material_type'], request.form['distance_to_subway'],
                 request.form['district'], request.form['description'], datetime.datetime.now(),
                 filename, object_id])
            cur.execute('UPDATE deal SET id_type_of_deal=%s WHERE id_object=%s',
                        [options1, object_id])
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('my_object', form=form))
    return render_template('edit_object.html', form=form, options1=options1,
                           options2=options2)


@app.route('/my_object', methods=['GET', 'POST'])
@login_required
def my_object():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST' and 'delete_btn' in request.form:
        obj_id_to_delete = request.form['delete_btn']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id_adress FROM object WHERE id = %s", (obj_id_to_delete,))
        obj_adress = cur.fetchall()[0][0]
        cur.execute("DELETE FROM deal WHERE id_object = %s ", (obj_id_to_delete,))
        cur.execute("DELETE FROM object WHERE id = %s", (obj_id_to_delete,))
        cur.execute("DELETE FROM adress WHERE id =%s", (obj_adress,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/my_object')
    cur.execute(
        "SELECT room_num, square, price, floar_num, date_of_sale, image, id_object FROM object JOIN deal ON object.id=deal.id_object WHERE id_first_user = %s",
        (current_user.id,))
    user_object = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('my_object.html', user_object=user_object)


@app.route('/my_deal')
@login_required
def my_deal():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT room_num, square, price, floar_num, date_of_sale, image, id_object FROM object JOIN deal ON object.id=deal.id_object WHERE id_first_user = %s",
        (current_user.id,))
    user_object = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('my_deal.html', user_object=user_object)


@app.route('/deal_details/<int:object_id>', methods=['GET', 'POST'])
@login_required
def deal_details(object_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT * FROM deal INNER JOIN "user" ON deal.id_first_user="user".id INNER JOIN type_of_deal ON deal.id_type_of_deal=type_of_deal.id  WHERE id_object=%s',
        (object_id,))
    deal_info = cur.fetchall()
    cur.execute('SELECT id_second_user FROM deal WHERE id_object=%s', (object_id,))
    id_second_user = cur.fetchall()[0][0]
    cur.execute('SELECT first_name, second_name FROM "user" WHERE id=%s', (id_second_user,))
    second_user = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('deal_details.html', deal_info=deal_info, second_user=second_user)


@app.route('/close_deal/<int:object_id>', methods=['GET', 'POST'])
@login_required
def close_deal(object_id):
    form = CloseDeal()
    if form.validate_on_submit() and request.method == "POST":
        conn = get_db_connection()
        cur = conn.cursor()
        user_second_login = request.form['user_second_login']
        cur.execute('SELECT id FROM "user" WHERE login =%s', (user_second_login,))
        id_second_user = cur.fetchall()[0][0]
        cur.execute(
            'UPDATE deal SET id_second_user =%s, price_of_deal= %s, date_of_deal = %s WHERE id_object =%s',
            [id_second_user, request.form['price'], datetime.datetime.now(), object_id])
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('my_deal', form=form))
    return render_template('close_deal.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = Search()
    if request.method == 'POST':
        price_min = request.form['price_min']
        price_max = request.form['price_max']
        square_min = request.form['square_min']
        square_max = request.form['square_max']
        room_num = request.form['room_num']

        conn = get_db_connection()
        cur = conn.cursor()
        query = "SELECT * FROM object WHERE 1=1"

        if price_min:
            query += f" AND price >= {price_min}"
        if price_max:
            query += f" AND price <= {price_max}"
        if square_min:
            query += f" AND square >= {square_min}"
        if square_max:
            query += f" AND square <= {square_max}"
        if room_num:
            query += f" AND room_num = {room_num}"

        cur.execute(query)
        results = cur.fetchall()
        cur.execute('SELECT * FROM object')
        objects = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('search.html', results=results, form=form, objects=objects)
    else:
        return render_template('search.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    message = ''
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        conn = get_db_connection()
        cur = conn.cursor()
        is_realtor = request.form.get('realtor') == 'true'
        if is_realtor:
            role = 'realtor'
        else:
            role = 'user'
        cur.execute('SELECT * FROM "user" WHERE login = %s', (request.form['login'],))
        if cur.fetchone():
            message = 'Login already exist'
        cur.execute('SELECT * FROM "user" WHERE email = %s', (request.form['email'],))
        if cur.fetchone():
            message = 'Email already exist'
        cur.execute('SELECT * FROM "user" WHERE phone_num = %s', (request.form['phone_num'],))
        if cur.fetchone():
            message = 'Phone already exist'
        cur.execute('SELECT * FROM "user" WHERE pass_num = %s', (request.form['pass_num'],))
        if cur.fetchone():
            message = 'Pass already exist'
        if message == '':
            password_hash = generate_password_hash(request.form['password'])
            cur.execute(
                'INSERT INTO "user" (first_name, second_name, login, email, password, phone_num, pass_num, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                [request.form['first_name'], request.form['second_name'], request.form['login'],
                 request.form['email'], password_hash, request.form['phone_num'],
                 request.form['pass_num'], role])
            conn.commit()
            cur.close()
            conn.close()
            return redirect('login')

    return render_template('register.html', title='Регистрация', form=reg_form, message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    login_form = LoginForm()
    if login_form.validate_on_submit():
        conn = get_db_connection()
        cur = conn.cursor()
        res = cur.execute('SELECT id, login, password, role '
                          'FROM "user" '
                          'WHERE login = %s', (request.form['login'],)).fetchone()
        if res is None or not check_password_hash(res[2], request.form['password']):
            message = 'Неверный логин или пароль'
            flash(message, 'danger')
            return redirect('login')
        id, login, password, role = res
        user = User(id, login, password, role)
        login_user(user, remember=login_form.remember_me.data)
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/')
    return render_template('login.html', title='Вход', form=login_form, message=message)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/edituser', methods=['GET', 'POST'])
@login_required
def edit_user():
    conn = get_db_connection()
    cur = conn.cursor()

    first_name, second_name, login, email, password, phone_num, pass_num = cur.execute(
        'SELECT first_name, second_name, login, email, password, phone_num, pass_num '
        'FROM "user" '
        'WHERE id = %s',
        (current_user.id,)).fetchone()
    user_id = cur.fetchall()
    editmessage = ''
    form = EditUserForm(first_name=first_name, second_name=second_name, login=login, email=email, password=password,
                        phone_num=phone_num, pass_num=pass_num)
    if form.validate_on_submit():
        cur.execute('SELECT * FROM "user" WHERE login = %s', (request.form['login'],))
        if cur.fetchone():
            editmessage = 'Login already exist'
        cur.execute('SELECT * FROM "user" WHERE email = %s', (request.form['email'],))
        if cur.fetchone():
            editmessage = 'Email already exist'
        cur.execute('SELECT * FROM "user" WHERE phone_num = %s', (request.form['phone_num'],))
        if cur.fetchone():
            editmessage = 'Phone already exist'
        cur.execute('SELECT * FROM "user" WHERE pass_num = %s', (request.form['pass_num'],))
        if cur.fetchone():
            editmessage = 'Pass already exist'
        if editmessage == '':
            password_hash = generate_password_hash(request.form['password'])
            cur.execute(
                'UPDATE  "user" SET first_name = %s, second_name = %s, login = %s, email = %s, password = %s,  phone_num = %s, pass_num = %s WHERE id =%s ',
                [request.form['first_name'], request.form['second_name'], request.form['login'],
                 request.form['email'], password_hash, request.form['phone_num'],
                 request.form['pass_num'], current_user.id])
        editmessage = 'Неверный логин или пароль'
        flash(editmessage, 'submit')
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('account', form=form, user_id=user_id))
    return render_template('edit_user.html', form=form, user_id=user_id)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(401)
def page_not_found(error):
    return render_template('401.html'), 401


@app.errorhandler(500)
def page_not_found(error):
    return render_template('500.html'), 500

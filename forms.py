from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, DateField, IntegerField, PasswordField, FloatField, FileField, \
    validators, ValidationError, SubmitField

def my_length_check(form, field):
    if len(field.data) != 11:
        raise ValidationError('Телефон и паспорт должны быть равны 11')
class RegistrationForm(FlaskForm):
    first_name = StringField('Имя пользователя', [validators.InputRequired(), validators.Length(min=1, max=25)])
    second_name = StringField('Фамилия', [validators.InputRequired(), validators.Length(min=1, max=25)])
    login = StringField('Логин', [validators.InputRequired(), validators.Length(min=4, max=25)])
    email = StringField('E-mail', [validators.InputRequired(), validators.Length(min=6, max=100)])
    password = PasswordField('Пароль', [validators.InputRequired(),
                                        validators.Length(min=6, max=100),
                                        validators.EqualTo('confirm', message='Пароли должны совпадать')])
    confirm = PasswordField('Повторите пароль')
    phone_num = StringField('Телефон', [validators.InputRequired(), my_length_check])
    pass_num = StringField('Паспорт', [validators.InputRequired(),my_length_check])


class EditUserForm(FlaskForm):
    first_name = StringField('Имя пользователя', [validators.Length(min=1, max=25)])
    second_name = StringField('Фамилия', [validators.Length(min=1, max=25)])
    login = StringField('Логин', [validators.Length(min=4, max=25)])
    email = StringField('E-mail', [validators.Length(min=6, max=100)])
    password = PasswordField('Пароль', [
        validators.Length(min=6, max=100),
        validators.EqualTo('confirm', message='Пароли должны совпадать')])
    confirm = PasswordField('Повторите пароль')
    phone_num = StringField('Телефон', [my_length_check])
    pass_num = StringField('Паспорт', [my_length_check])


class LoginForm(FlaskForm):
    login = StringField('Логин', [validators.InputRequired()])
    password = PasswordField('Пароль', [validators.InputRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AddObjectForm(FlaskForm):
    adress = StringField('Адрес', [validators.InputRequired()])
    room_num = IntegerField('Количество комнат', [validators.InputRequired()])
    square = IntegerField('Площадь в м2', [validators.InputRequired()])
    floar_num = IntegerField('Номер этажа', [validators.InputRequired()])
    date_build = IntegerField('Год постройки', [validators.InputRequired()])
    material_type = StringField('Тип материала', [validators.InputRequired()])
    distance_to_subway = IntegerField('Расстояние до метро в м')
    district = StringField('Район', [validators.InputRequired()])
    description = StringField('Описание')
    date_of_sale = DateField('Дата выставления на продажу', format='%Y-%m-%d')
    price = IntegerField('Цена', [validators.InputRequired()])
    image = FileField('Фото', [validators.DataRequired()])
    submit = SubmitField('Создать объявление')


class EditObjectForm(FlaskForm):
    adress = StringField('Адрес')
    room_num = IntegerField('Количество комнат')
    square = IntegerField('Площадь в м2')
    floar_num = IntegerField('Номер этажа')
    date_build = IntegerField('Год постройки')
    material_type = StringField('Тип материала')
    distance_to_subway = IntegerField('Расстояние до метро в м')
    district = StringField('Район')
    description = StringField('Описание')
    date_of_sale = DateField('Дата выставления на продажу', format='%Y-%m-%d')
    price = IntegerField('Цена')
    image = FileField('Фото')
    submit = SubmitField('Редактировать объявление')


class Search(FlaskForm):
    price_min = IntegerField('Минимальная цена')
    price_max = IntegerField('Максимальная цена')
    square_min = IntegerField('Минимальная площадь в м2')
    square_max = IntegerField('Максимальная площадь в м2')
    room_num = IntegerField('Количество комнат')

class CloseDeal(FlaskForm):
    user_second_login = StringField('Логин покупателя', [validators.InputRequired()])
    price = IntegerField('Итоговая цена', [validators.InputRequired()])
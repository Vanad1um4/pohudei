from django.db import connection
from datetime import date, datetime
from .log import *

logger = get_logger()  # pyright: ignore


def dict_fetchall(cursor):
    """Returns all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


##### WEIGHT FUNCTIONS ########################################################

def db_get_one_weight(user_id, date_iso):
    try:
        if date_iso == None:
            today = datetime.today()
            date_iso = today.strftime('%Y-%m-%d')
        with connection.cursor() as c:
            sql = 'select id, date, weight from weights where users_id=%s and date=%s;'
            values = (user_id, date_iso)
            c.execute(sql, values)
            res = c.fetchall()
            if res:
                return ('success', res)
            else:
                return ('no_data', [])

    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_update_weight_from_diary(user_id, date, weight):
    try:
        with connection.cursor() as c:
            sql = 'select id from weights where users_id=%s and date=%s;'
            values = (user_id, date)
            c.execute(sql, values)
            id = c.fetchone()
            print(id)
            if id:
                sql = 'update weights set weight=%s where id=%s and users_id=%s;'
                values = (weight, id[0], user_id)
                c.execute(sql, values)
            elif not id:
                sql = 'insert into weights (users_id, date, weight) values (%s, %s, %s);'
                values = (user_id, date, weight)
                c.execute(sql, values)
            return ('success', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


##### DIARY FUNCTIONS #########################################################

def db_get_food_from_diary(user_id, date_iso):
    try:
        if date_iso == None:
            today = datetime.today()
            date_iso = today.strftime('%Y-%m-%d')
        with connection.cursor() as c:
            sql = '''
                select d.id, c.name, d.food_weight, cast(round(d.food_weight / 100.0 * c.kcals) as integer) as eaten_kcals
                from diary d join catalogue c on d.catalogue_id=c.id
                where d.date=%s and d.users_id=%s
                order by d.id;'''
            values = (date_iso, user_id)
            c.execute(sql, values)
            res = c.fetchall()
        return res
    except Exception as exc:
        logger.exception(exc)
        return []


def db_add_new_diary_entry(user_id, date, food_id, weight):
    try:
        with connection.cursor() as c:
            sql = 'insert into diary (users_id, date, catalogue_id, food_weight) values (%s, %s, %s, %s);'
            values = (user_id, date, food_id, weight)
            c.execute(sql, values)
            return 'success'
    except Exception as exc:
        logger.exception(exc)
        return 'failure'


def db_update_diary_entry(user_id, diary_id, new_food_weight):
    try:
        with connection.cursor() as c:
            sql = 'update diary set food_weight=%s where id=%s and users_id=%s;'
            values = (new_food_weight, diary_id, user_id)
            c.execute(sql, values)
            return 'success'
    except Exception as exc:
        logger.exception(exc)
        return 'failure'


def db_del_diary_entry(user_id, diary_id):
    try:
        with connection.cursor() as c:
            sql = 'delete from diary where id=%s and users_id=%s;'
            values = (diary_id, user_id)
            c.execute(sql, values)
            return 'success'
    except Exception as exc:
        logger.exception(exc)
        return 'failure'


##### CATALOGUE FUNCTIONS #####################################################

def db_get_all_food_names(user_id):
    try:
        with connection.cursor() as c:
            sql = 'select id, name from catalogue where users_id=0 or users_id=%s order by name;'
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
        return res
    except Exception as exc:
        logger.exception(exc)
        return []


def db_get_users_food_names(user_id, admin=False):
    try:
        with connection.cursor() as c:
            if admin:
                c.execute('select id, name, kcals from catalogue order by name;')
                foods = c.fetchall()
            else:
                sql = 'select id, name, kcals from catalogue where users_id=%s order by name;'
                values = (user_id,)
                c.execute(sql, values)
                foods = c.fetchall()
        return ('success', foods)
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_add_new_food_to_catalogue(user_id, food_name, food_kcals, admin=False):
    try:
        with connection.cursor() as c:
            sql = 'select id from catalogue where name=%s;'
            values = (food_name,)
            c.execute(sql, values)
            id = c.fetchall()
            if id:
                return ('duplication', [])
            elif admin:
                sql = 'insert into catalogue (name, kcals, users_id) values (%s, %s, 0);'
                values = (food_name, food_kcals)
                c.execute(sql, values)
                return ('success', [])
            elif not admin:
                sql = 'insert into catalogue (name, kcals, users_id) values (%s, %s, %s);'
                values = (food_name, food_kcals, user_id)
                c.execute(sql, values)
                return ('success', [])
            else:
                return ('failure', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_update_food_in_catalogue(user_id, food_id, food_name, food_kcals, admin=False):
    try:
        with connection.cursor() as c:
            sql = 'select id from catalogue where id!=%s and name=%s;'
            values = (food_id, food_name)
            c.execute(sql, values)
            id = c.fetchall()
            if id:
                return ('duplication', [])
            elif admin:
                sql = 'update catalogue set name=%s, kcals=%s where id=%s;'
                values = (food_name, food_kcals, food_id)
                c.execute(sql, values)
                return ('success', [])
            elif not admin:
                sql = 'update catalogue set name=%s, kcals=%s where id=%s and users_id=%s;'
                values = (food_name, food_kcals, food_id, user_id)
                c.execute(sql, values)
                return ('success', [])
            else:
                return ('failure', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_delete_food_from_catalogue(food_id):
    try:
        with connection.cursor() as c:
            sql = 'select id from diary where catalogue_id=%s;'
            values = (food_id,)
            c.execute(sql, values)
            id = c.fetchone()
            print(id)
            if id:
                return ('in use', [])
            elif not id:
                sql = 'delete from catalogue where id=%s;'
                values = (food_id,)
                c.execute(sql, values)
                return ('success', [])
            else:
                return ('failure', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


##### STATS FUNCTIONS #########################################################


def db_get_users_weights_all(user_id):
    try:
        with connection.cursor() as c:
            sql = 'select date, weight from weights where users_id=%s order by date;'
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
        return ('success', res)
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_get_everyday_sum_kcals_from_diary(user_id):
    try:
        with connection.cursor() as c:
            sql = '''
                select d.date, sum(round(d.food_weight / 100.0 * c.kcals)) as eaten
                from diary d join catalogue c on d.catalogue_id=c.id
                where d.users_id=%s
                group by d.date
                order by d.date;'''
            values = (user_id,)
            c.execute(sql, values)
            res = c.fetchall()
        return res
    except Exception as exc:
        logger.exception(exc)
        return []


##### BACKUP FUNCTIONS ########################################################


def db_backup(date_iso):
    try:
        with connection.cursor() as c:
            sql = '''
                select d.id as diary_id, *, round(d.food_weight / 100.0 * c.kcals) as calc_kcals
                from diary d join catalogue c on d.catalogue_id=c.id
                where d.date=%s
                order by d.date asc, d.id asc;'''
            values = (date_iso,)
            c.execute(sql, values)
            food = dict_fetchall(c)

            sql = 'select * from weights where date=%s;'
            values = (date_iso,)
            c.execute(sql, values)
            weights = dict_fetchall(c)
        return ('success', (food, weights))
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [{}, {}])

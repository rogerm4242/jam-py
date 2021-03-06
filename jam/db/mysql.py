import MySQLdb
from werkzeug._compat import iteritems

DATABASE = 'MYSQL'
NEED_DATABASE_NAME = True
NEED_LOGIN = True
NEED_PASSWORD = True
NEED_ENCODING = True
NEED_HOST = True
NEED_PORT = True
CAN_CHANGE_TYPE = False
CAN_CHANGE_SIZE = False
DDL_ROLLBACK = False
NEED_GENERATOR = False

FROM = '"%s" AS %s'
LEFT_OUTER_JOIN = 'LEFT OUTER JOIN "%s" AS %s'
FIELD_AS = 'AS'
LIKE = 'LIKE'

JAM_TYPES = TEXT, INTEGER, FLOAT, CURRENCY, DATE, DATETIME, BOOLEAN, BLOB, KEYS = range(1, 10)
FIELD_TYPES = {
    INTEGER: 'INT',
    TEXT: 'VARCHAR',
    FLOAT: 'DOUBLE',
    CURRENCY: 'DOUBLE',
    DATE: 'DATE',
    DATETIME: 'DATETIME',
    BOOLEAN: 'INT',
    BLOB: 'BLOB',
    KEYS: 'BLOB'
}

def connect(database, user, password, host, port, encoding):
    charset = None
    use_unicode = None
    if encoding:
        charset = encoding
        use_unicode = True
    if port:
        connection = MySQLdb.connect(db=database, user=user, passwd=password, host=host,
            port=int(port), charset=charset, use_unicode=use_unicode)
    else:
        connection = MySQLdb.connect(db=database, user=user, passwd=password, host=host,
            charset=charset, use_unicode=use_unicode)
    connection.autocommit(False)
    cursor = connection.cursor()
    cursor.execute("SET SESSION SQL_MODE=ANSI_QUOTES")
    return connection

def get_lastrowid(cursor):
    return cursor.lastrowid

def get_select(query, start, end, fields):
    offset = query['__offset']
    limit = query['__limit']
    result = 'SELECT %s FROM %s' % (start, end)
    if limit:
        result += ' LIMIT %d, %d' % (offset, limit)
    return result

def process_sql_params(params, cursor):
    result = []
    for p in params:
        if type(p) == tuple:
            value, data_type = p
        else:
            value = p
        result.append(value)
    return result

def process_sql_result(rows):
    result = []
    for row in rows:
        result.append(list(row))
    return result

def cast_date(date_str):
    return "'" + date_str + "'"

def cast_datetime(datetime_str):
    return "'" + datetime_str + "'"

def value_literal(index):
    return '%s'

def upper_function():
    pass

def create_table_sql(table_name, fields, gen_name=None, foreign_fields=None):
    result = []
    primary_key = ''
    sql = 'CREATE TABLE "%s"\n(\n' % table_name
    lines = []
    for field in fields:
        line = '"%s" %s' % (field['field_name'], FIELD_TYPES[field['data_type']])
        if field['size'] != 0 and field['data_type'] == TEXT:
            line += '(%d)' % field['size']
        if field['default_value'] and not field['primary_key']:
            if field['data_type'] == TEXT:
                line += " DEFAULT '%s'" % field['default_value']
            else:
                line += ' DEFAULT %s' % field['default_value']
        if field['primary_key']:
            line += ' NOT NULL AUTO_INCREMENT'
            primary_key = field['field_name']
        lines.append(line)
    if primary_key:
        lines.append('PRIMARY KEY("%s")' % primary_key)
    sql += ',\n'.join(lines)
    sql += ')\n'
    result.append(sql)
    return result


def delete_table_sql(table_name, gen_name):
    result = []
    result.append('DROP TABLE "%s"' % table_name)
    return result

def create_index_sql(index_name, table_name, unique, fields, desc):
    return 'CREATE %s INDEX "%s" ON "%s" (%s)' % (unique, index_name, table_name, fields)

def create_foreign_index_sql(table_name, index_name, key, ref, primary_key):
    return 'ALTER TABLE "%s" ADD CONSTRAINT "%s" FOREIGN KEY ("%s") REFERENCES "%s"("%s")' % \
        (table_name, index_name, key, ref, primary_key)

def delete_index(table_name, index_name):
    return 'DROP INDEX "%s" ON "%s"' % (index_name, table_name)

def delete_foreign_index(table_name, index_name):
    return 'ALTER TABLE "%s" DROP FOREIGN KEY "%s"' % (table_name, index_name)

def add_field_sql(table_name, field):
    result = 'ALTER TABLE "%s" ADD "%s" %s' % \
        (table_name, field['field_name'], FIELD_TYPES[field['data_type']])
    if field['size']:
        result += '(%d)' % field['size']
    if field['default_value']:
        if field['data_type'] == TEXT:
            result += " DEFAULT '%s'" % field['default_value']
        else:
            result += ' DEFAULT %s' % field['default_value']
    return result

def del_field_sql(table_name, field):
    return 'ALTER TABLE "%s" DROP "%s"' % (table_name, field['field_name'])

def change_field_sql(table_name, old_field, new_field):
    result = []
    if old_field['field_name'] != new_field['field_name']:
        sql = 'ALTER TABLE "%s" CHANGE  "%s" "%s" %s' % (table_name, old_field['field_name'],
            new_field['field_name'], FIELD_TYPES[new_field['data_type']])
        if old_field['size']:
            sql += '(%d)' % old_field['size']
        #~ if old_field['data_type'] != new_field['data_type'] or \
            #~ old_field['size'] != new_field['size']:
            #~ sql += ' %s' % FIELD_TYPES[field['data_type']]
            #~ if new_field['size'] and old_field['size'] != new_field['size']:
                #~ sql += '(%d)' % new_field['size']
        result.append(sql)
    if old_field['default_value'] != new_field['default_value']:
        if new_field['default_value']:
            if new_field['data_type'] == TEXT:
                sql = 'ALTER TABLE "%s" ALTER "%s" SET DEFAULT' % \
                    (table_name, new_field['field_name'])
                sql +=  " '%s'" % new_field['default_value']
            else:
                sql = 'ALTER TABLE "%s" ALTER "%s" SET DEFAULT %s' % \
                    (table_name, new_field['field_name'], new_field['default_value'])
        else:
            sql = 'ALTER TABLE "%s" ALTER "%s" DROP DEFAULT' % \
                (table_name, new_field['field_name'])
        result.append(sql)
    return result

def param_literal():
    return '%s'

def quotes():
    return '`'

def get_sequence_name(table_name):
    return None

def next_sequence_value_sql(table_name):
    return None

def restart_sequence_sql(table_name, value):
    pass

def set_literal_case(name):
    return name.lower()

def get_table_names(connection):
    cursor = connection.cursor()
    cursor.execute('show tables')
    result = cursor.fetchall()
    return [r[0] for r in result]

def get_table_info(connection, table_name, db_name):
    cursor = connection.cursor()
    sql = 'SHOW COLUMNS FROM "%s" FROM %s' % (table_name, db_name)
    cursor.execute(sql)
    result = cursor.fetchall()
    fields = []
    for (field_name, type_size, null, key, default_value, autoinc) in result:
        try:
            pk = False
            if autoinc and key == 'PRI':
                pk = True
            data_type = type_size.split('(')[0].upper()
            size = type_size.split('(')[1].split(')')[0]
            if not data_type in ['VARCHAR', 'CHAR']:
                size = 0
        except:
            data_type = type_size
            size = 0
        fields.append({
            'field_name': field_name,
            'data_type': data_type,
            'size': size,
            'default_value': default_value,
            'pk': pk
        })
    sql = 'SHOW INDEXES FROM %s FROM %s' % (table_name, db_name)
    cursor.execute(sql)
    result = cursor.fetchall()
    indexes = {}
    for r in result:
        index_name = r[2]
        unique = False
        if r[1] == 0:
            unique = True
        if index_name != 'PRIMARY':
            index = indexes.get(index_name)
            if not index:
                index = {
                    'index_name': index_name,
                    'unique': unique,
                    'fields': []
                }
                indexes[index_name] = index
            index['fields'].append([r[4], False])
    ind = []
    indexes.values()
    for key, value in iteritems(indexes):
        ind.append(value)
    return {'fields': fields, 'indexes': ind}


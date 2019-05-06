import MySQLdb
from config import HOST, PORT, PASSWD, DB, USER
from MySQLdb import cursors


class __MySql():
    def __init__(self):
        self.parameters = {
            'host': HOST,
            'port': PORT,
            'user': USER,
            'passwd': PASSWD,
            'db': DB,
            'charset': 'utf8',
            'cursorclass': cursors.DictCursor
        }
        self.db = MySQLdb.connect(**self.parameters)

    def __del__(self):
        self.db.close()

    def query(self, sql):
        c = self.db.cursor()
        try:
            c.execute(sql)
            r = c.fetchall()
            c.close()
            return r
        except:
            return None

    def run(self, sql):
        c = self.db.cursor()
        try:
            c.execute(sql)
            self.db.commit()
            c.close()
            return True
        except:
            self.db.rollback()
            return False


class SQL():
    def __init__(self):
        self.sql = ''

    def clear(self):
        self.sql = ''
        return self

    def __ts(self, input):
        if isinstance(input, str):
            return "'%s'" % input
        return str(input)

    def __ts_cols(self, **columns):
        s = []
        for (k, v) in columns.items():
            s.append('%s=%s' % (k, self.__ts(v)))
        return ','.join(s)

    def __ts_odb_cols(self, **columns):
        s = []
        for (k, v) in columns.items():
            if (str(v) != '0') and (str(v).upper() != 'FALSE') and (str(v).upper() != 'DESC'):
                v = 'ASC'
            else:
                v = 'DESC'
            s.append('%s %s' % (k, v))
        return ','.join(s)

    def __ts_val_cols(self, **columns):
        ks = []
        vs = []
        for (k, v) in columns.items():
            ks.append(k)
            vs.append(self.__ts(v))
        return '( %s ) Values ( %s )' % (','.join(ks), ','.join(vs))

    def Update(self, tabel):
        self.sql = self.sql + ('UPDATE %s ' % (tabel))
        return self

    def Delete(self, tabel):
        self.sql = self.sql + ('DELETE FROM %s ' % (tabel))
        return self

    def Insert(self, tabel):
        self.sql = self.sql + ('INSERT INTO %s ' % (tabel))
        return self

    def Select(self, tabel, columns=None):
        if columns is None:
            cols = '*'
        else:
            cols = ','.join(columns)
        self.sql = self.sql + ('SELECT %s FROM %s ' % (cols, tabel))
        return self

    def Set(self, **columns):
        cols = self.__ts_cols(**columns)
        self.sql = self.sql + ('SET %s ' % (cols))
        return self

    def Where(self, **columns):
        cols = self.__ts_cols(**columns)
        self.sql = self.sql+('WHERE %s ' % (cols))
        return self

    def Values(self, **columns):
        cols = self.__ts_val_cols(**columns)
        self.sql = self.sql+('%s ' % (cols))
        return self

    def OrderBy(self, **columns):
        cols = self.__ts_odb_cols(**columns)
        self.sql = self.sql+('ORDER BY %s ' % (cols))
        return self

    def Limit(self, lines, offset=0):
        self.sql = self.sql+('LIMIT {},{}'.format(offset, lines))
        return self

    def Page(self, size=10, index=0):
        return self.Limit(size, size*index)


mysql = __MySql()

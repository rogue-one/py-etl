import pyodbc
from datetime import date
from datetime import time
from datetime import datetime
import decimal

__author__ = 'chlr'


class DataComparator():

    default_values = {
        str : '',
        bool : '',
        date : '',
        time : '',
        datetime : '',
        long : 0,
        float : 0.0,
        decimal : 0.0,
        int: 0
    }

    def __init__(self,lhs_dsn,rhs_dsn):
        self.lhs_dsn = lhs_dsn
        self.rhs_dsn = rhs_dsn
        self.lhs_query = None
        self.rhs_query = None
        self.key_columns = None

    def set_query_metadata(self,lhs_query,rhs_query,key_columns):
        self.lhs_query = lhs_query
        self.rhs_query = rhs_query
        self.key_columns = key_columns

    @staticmethod
    def execute_query(dsn,query,keylist):
        conn = pyodbc.connect(**dsn)
        cursor = conn.cursor()
        result = cursor.execute(query).fetchall()
        dict_result =  {tuple([row[k] for k in keylist]):tuple(row[k] for k in range(len(cursor.description)) if k not in keylist) for row in result}
        data_types = tuple([[DataComparator.default_values[k[1]] for k in cursor.description][i] for i in keylist])
        cursor.close()
        return dict_result,data_types

    def compare(self):
        lhs_result,lhs_default_values = self.execute_query(self.lhs_dsn,self.lhs_query,self.key_columns)
        rhs_result,rhs_data_types = self.execute_query(self.rhs_dsn,self.rhs_query,self.key_columns)
        final_result =  { k:(zip(lhs_result.get(k,lhs_default_values),rhs_result.get(k,rhs_data_types))) for k in (set(lhs_result) | set(rhs_result)) }
        for key in final_result:
            print('%s: %s\n' % (key,final_result[key]))


if __name__ == '__main__':
    dsn_1 = {'DSN':'test_server'}
    dsn_2 = {'DSN':'test_server'}
    query_1 = "select name,val1,val2 from table1"
    query_2 = "select name,val1,val2 from table2"
    key_columns = [0]
    comp = DataComparator(dsn_1,dsn_2)
    comp.set_query_metadata(query_1,query_2,key_columns)
    comp.compare()





























from datetime import datetime
from datetime import timedelta
import argparse,re

__author__ = 'chlr'


class HiveFilter():

    def __init__(self,metadata):
        self.partition = [metadata['date'][0],metadata['hour'][0]]
        self.start_date =  metadata['date'][1][0]
        self.start_hour = metadata['hour'][1][0]
        self.end_date = metadata['date'][1][1]
        self.end_hour = metadata['hour'][1][1]

    def generate_filter(self):
        if self.start_date == self.end_date:
            return "( %s = '%s' AND %s >= %s AND %s <= %s )" % (self.partition[0], self.start_date, self.partition[1], self.start_hour, self.partition[1],self.end_hour)
        else:
             start_date = datetime.strptime(self.start_date,'%Y-%m-%d')
             end_date = datetime.strptime(self.end_date,'%Y-%m-%d')
             filter_range = (end_date-start_date).days + 1
             f = lambda x,y:  "( %s = '%s' AND %s %s )" % (self.partition[0],(start_date+timedelta(days=x)).strftime('%Y-%m-%d'),self.partition[1],' >= '+self.start_hour if x == 0 else ' <= ' +self.end_hour) if ( x == 0 or x == y-1 ) else ("( %s = '%s' )" % (self.partition[0],(start_date+timedelta(days=x)).strftime('%Y-%m-%d')))
             return '('+' OR '.join([ f(i,filter_range) for i in range(0,filter_range) ]) + ')'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hive Where clause generator')
    opts = parser.parse_known_args()[1]
    assert len(opts) == 4 , "Incorrect number of partitions"
    conf = dict(zip([k.strip('--') for k in opts[::2]],opts[1::2]))
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2},\d{4}-\d{2}-\d{2}$')
    hour_pattern = re.compile(r'^\d{1,2},\d{1,2}$')
    settings = {}
    for k,v in conf.items():
        if re.search(date_pattern,v):
            settings['date'] = (k,v.split(','))
            continue
        elif re.search(hour_pattern,v):
            settings['hour'] = (k,v.split(','))
            continue
        raise AssertionError('parameters failed regex compliance')
    where = HiveFilter(settings)
    result = where.generate_filter()
    print('{ "date_filter" : "%s" }' % result)



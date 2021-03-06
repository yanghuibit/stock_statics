from dbbase import Dbbase
from math import sqrt
from map_code import code_list, market_index_list

sh = 'b000001'
START_DATE = '2001-01-01'


def get_market_date(last_days=1):
    operation = Dbbase()
    operation.execute('select date from {} order by date desc limit {}'.format(sh, last_days))
    result = operation.cursor.fetchall()
    if not result:
        return False
    return result[-1][0]


class Dbstatistic(Dbbase):
    def __init__(self):
        super(Dbstatistic, self).__init__()
        self.code = None
        self.is_suspension = False
        self.market_last_trading_day = None
        self.code_last_trading_day = None

    def initialize(self, code):
        self.code = code
        if not code.startswith('b'):
            self.code = "`{}`".format(code)
        self.is_suspension = self._check_suspension(code=self.code)
        self.market_last_trading_day = self._get_latest_date(code=sh, last_days=1)
        self.code_last_trading_day = self._get_latest_date(code=self.code, last_days=1)

    def _check_suspension(self, code):
        self.execute('select date from {} order by date desc limit 1'.format(code))
        code_latest = self.cursor.fetchall()
        self.execute('select date from {} order by date desc limit 1'.format(sh))
        market_latest = self.cursor.fetchall()
        if code_latest == market_latest:
            return False
        else:
            return True

    def _get_latest_date(self, code, last_days):
        self.execute('select date from {} order by date desc limit {}'.format(code, last_days))
        result = self.cursor.fetchall()
        if result:
            return result[-1][0]

    def cal_fluc(self, start, end):
        self.execute("select fluctuation from {} where date >= '{}' and date <= '{}'".format(self.code, start, end))
        output = self.cursor.fetchall()
        if not output:
            return 'null'
        result = [item[0] for item in output]
        return sqrt(sum(fluc**2 for fluc in result)/len(result))

    def check_isReach_highest_price(self, day):
        self.execute('select max(high) from {}'.format(self.code))
        highest_price = self.cursor.fetchall()[0][0]
        self.execute("select date,high from {} where date = '{}'".format(self.code, day))
        result = self.cursor.fetchall()
        if not result:
            return False
        selected_price = result[0][1]
        if selected_price > highest_price*0.95:
            return True

    def change_rate_byweekday(self):
        pass

    def change_rate_byweek(self):
        pass

    def change_rate_bymonth(self):
        pass




#    def change_rate_by_weekday(self, start, end):
#        for i in range(2,7):
#            self.execute("select sum(rate),count(*) from {} where date > '{}' and date < '{}' and dayofweek(date) = {})




    def rate_st_weekday(self):
        for i in range(2, 7):
            self.execute('select sum(rate),count(*) from {} where date > date(\'{}\') and date < date(\'{}\') and dayofweek(date) = {} and rate >0'
                         .format(self.table, self.start, self.end, i))
            sum_inc, counter_inc = self.cursor.fetchall()[0]
            self.execute('select sum(rate),count(*) from {} where date > date(\'{}\') and date < date(\'{}\') and dayofweek(date) = {} and rate <0'
                         .format(self.table, self.start, self.end, i))
            sum_dec, counter_dec = self.cursor.fetchall()[0]
            print '{:8.4f}'.format(counter_inc /float(counter_inc+counter_dec)), '{:8.4f}'.format((sum_inc+sum_dec)/(counter_dec+counter_inc))

    def rate_st_month(self):
        for i in range(1, 13):
            self.execute('select sum(rate), count(*) from sh  where date > date(\'{}\') and date < date(\'{}\') and month(date) = {}'
                         .format(self.start, self.end, i))
            sum_rate, count = self.cursor.fetchall()[0]
            print '{:8.4f}'.format(sum_rate/count)



if __name__ == '__main__':
    db = Dbstatistic()
    lastday = db._get_latest_date(sh, 1)
    print lastday
    for code in market_index_list + code_list.keys():
        db.initialize(code)
        if db.check_isReach_highest_price(lastday):
            print code








    #print db.cal_fluc(start='2001-08-10', end='2015-08-20')
    #print db.issuspension
    #print db.get_latest_date(10)

    #print db.fluctuation_in_recent_days(5)

    #flu_dict = {}
    ##for code in code_list.keys() + market_index_list:
    ##    db.initialize(code)
    ##    if db.check_isReach_highest_price(day=db.market_last_trading_day):
    ##        print db.code
        #code_flu = db.fluctuation_in_one_days(db.get_start_date(1))
        #flu_dict[code] = code_flu

    #print sorted(flu_dict.items(), key=lambda d: float(d[1]))[-10:]
    #print flu_dict


    #sh.rate_st_weekday()
    #sh.rate_st_month()
    #print sh.get_start_date






    #for i in range(2, 7):
#    cur.execute('select count(*) from sh where dayofweek(date) = {} and rate >0'.format(i))
#    counter_inc = cur.fetchall()[0][0]
#    cur.execute('select count(*) from sh where dayofweek(date) = {} and rate <0'.format(i))
#    counter_dec = cur.fetchall()[0][0]
#    print counter_inc /float(counter_inc+counter_dec)


#for i in range(2, 7):
#    cur.execute('select count(rate),sum(rate) from sh where dayofweek(date) = {} and rate >0'.format(i))
#    res = cur.fetchall()[0]
#    print res[1] / res[0]
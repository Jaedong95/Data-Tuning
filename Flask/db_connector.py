import pymysql
import csv

class DSMDB():
    def __init__(self, args):
        self.args = args 

    def connect(self):
        self.conn = pymysql.connect(host=self.args.host, user=self.args.user, \
            password=self.args.password, db=self.args.db, charset='utf8')
        self.curs = self.conn.cursor()

    def execute_sql(self, sql):
        self.curs.execute(sql)
        return self.curs.fetchall() 

    def update_sql(self, sql):
        self.curs.execute(sql)
        self.curs.fetchall() 

    def update_db(self, dsm_idx):
        sql = f'UPDATE dsm_table SET annot = 9999 WHERE idx = {dsm_idx};'
        self.execute_sql(sql)
        self.conn.commit()

    def get_dsm_data(self):
        sql = 'SELECT * FROM dsm_table;'
        self.dsm_data = self.execute_sql(sql)
    
    def get_mapping_idx(self, criteria, question_no):
        sql = f'SELECT idx FROM map_criteria WHERE criteria = {criteria} and criteria_idx = {question_no};'
        dsm_idx = self.execute_sql(sql)[0][0]
        return dsm_idx 

    def get_txt(self, dsm_idx):
        sql = f'SELECT text FROM dsm_table WHERE idx = {dsm_idx};'
        txt = self.execute_sql(sql)[0][0] 
        return txt
    
    def get_len(self, criteria):
        sql = f'SELECT COUNT(*) FROM dsm_table WHERE label = {criteria};'
        data_len = self.execute_sql(sql)[0][0] 
        return data_len 
    
    def get_annot(self, dsm_idx):
        sql = f'SELECT annot FROM dsm_table WHERE idx = {dsm_idx};'
        annot = self.execute_sql(sql)[0][0]
        return annot

    def save_criteria(self, criteria):
        sql = f'UPDATE dsm_criteria SET criteria_idx={criteria};'
        self.execute_sql(sql)
        self.conn.commit()

    def get_not_tagged(self, criteria):
        sql = f'SELECT criteria_idx FROM map_criteria WHERE idx in \
            (SELECT idx FROM dsm_table WHERE label = {criteria} and annot = 9999);'
        not_tagged_list = self.execute_sql(sql)
        return not_tagged_list

    def get_dsm_criteria(self):
        sql = f'SELECT criteria_idx FROM dsm_criteria;'
        self.dsm_criteria = self.execute_sql(sql)[0][0]
 
    def save_annot(self, dsm_idx, annot):
        sql = f'UPDATE dsm_table SET annot={annot} WHERE idx = {dsm_idx};'
        self.execute_sql(sql)
        self.conn.commit()

class UPLOADDB():
    def __init__(self, args):
        self.args = args 

    def connect(self):
        self.conn = pymysql.connect(host=self.args.host, user=self.args.user, \
            password=self.args.password, db=self.args.db, charset='utf8')
        self.curs = self.conn.cursor()

    def execute_sql(self, sql):
        self.curs.execute(sql)
        return self.curs.fetchall() 

    def update_sql(self):
        self.curs.fetchall()
        self.conn.commit()

    def save_file_info(self, filename):
        sql = f'UPDATE check_upload SET filename = {filename} WHERE idx = 0;' 
        self.execute_sql(sql)
        self.update_sql()

    def save_data(self, filename):
        sql = "TRUNCATE upload_data"
        self.execute_sql(sql)
        sql = "ALTER TABLE upload_data convert to charset utf8;"  
        self.execute_sql(sql)

        file = open(filename,'r', encoding='UTF8')
        fReader = csv.reader(file)
        idx_list = []
        for idx, line in enumerate(fReader):
            if idx == 0: 
                continue 
            try:    # ' -> 제거하지 않으면 오류 발생 
                sql = "INSERT INTO upload_data VALUES('{0}', '{1}', '{2}', '{3}')"\
                .format(line[0], line[1].replace("'", ''), line[2], line[3])
                self.execute_sql(sql)
            except:
                idx_list.append(idx)
                print(f'err: {idx}')
                continue    
        self.update_sql()

    def update_db(self, data_idx):
        sql = f'UPDATE upload_data SET annot = 9999 WHERE idx = {data_idx};'
        self.execute_sql(sql)
        self.update_sql()

    def get_data(self):
        sql = 'SELECT * FROM upload_data;'
        self.dsm_data = self.execute_sql(sql)
    
    def get_filename(self):
        sql = 'SELECT file_name FROM check_upload;'
        filename = self.execute_sql(sql)[0][0]
        return filename

    def get_txt(self, data_idx):
        sql = f'SELECT text FROM upload_data WHERE idx = {data_idx};'
        txt = self.execute_sql(sql)[0][0] 
        return txt
    
    def get_len(self):
        sql = f'SELECT COUNT(*) FROM upload_data;'
        data_len = self.execute_sql(sql)[0][0] 
        return data_len 
    
    def get_annot(self, data_idx):
        sql = f'SELECT annot FROM upload_data WHERE idx = {data_idx};'
        annot = self.execute_sql(sql)[0][0]
        return annot

    def get_not_tagged(self):
        sql = f'SELECT idx FROM upload_data WHERE annot = 9999'
        not_tagged_list = self.execute_sql(sql)
        return not_tagged_list
 
    def save_annot(self, data_idx, annot):
        sql = f'UPDATE upload_data SET annot={annot} WHERE idx = {data_idx};'
        self.execute_sql(sql)
        self.conn.commit()

    def close_session(self):
        self.curs.close()
        self.conn.close()
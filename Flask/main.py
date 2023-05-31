import os 
import argparse
import json
import pandas as pd 
from db_connector import DSMDB, UPLOADDB
from attrdict import AttrDict
from flask import Flask, render_template, request

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload_data', methods=['GET', 'POST'])
def upload_data():
    '''
    Data Tuning 할 데이터세트를 내 PC에서 Upload 
    '''
    global updb 
    updb = UPLOADDB(args1)
    updb.connect()
    annot_check = 9999 
    not_tagged = None 
    
    if request.method == 'POST':
        file = request.files['upload']   
        if file:
            filename = file.filename
            new_filename = "'" + filename + "'"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f'upload: {new_filename}')
            
            updb.save_file_info(new_filename)
            updb.save_data(os.path.join(upload_folder_dir, filename))
            # updb.close_session()
            return render_template("upload_data.html", annot_check=annot_check, not_tagged=not_tagged, task_flag=task_flag)
    return render_template("upload_data.html", annot_check=annot_check, not_tagged=not_tagged,)

@app.route('/upload_data/<int:question_no>', methods=['GET', 'POST'])
def upload_index(question_no):
    data_len = updb.get_len()
    txt = updb.get_txt(question_no - 1)
    annot = int(updb.get_annot(question_no - 1))
    data_idx = question_no - 1
    # print(annot)
    if request.method=='POST':
        try:
            request.form['translate']
        except:
            try:
                request.form['update']
                updb.update_db(question_no - 1)
                annot = int(dsmdb.get_annot(data_idx))
            except:
                annot_val = request.form['radioOpt']
                # print(annot_val)
                updb.save_annot(question_no - 1, annot_val)
                annot = int(updb.get_annot(data_idx))
    if question_no == 1:
        return render_template('task1_s.html', txt=txt, question_no=question_no, data_len=data_len, annot=annot)
    elif question_no == data_len:
        return render_template('task1_e.html', txt=txt, question_no=question_no, data_len=data_len, annot=annot)
    else:
        return render_template('task1_m.html', txt=txt, question_no=question_no, data_len=data_len, annot=annot)


@app.route('/dsm_data', methods=['GET', 'POST'])
def select_criteria():
    '''
    9가지 Criteria 중 Tuning 할 데이터세트 선택 
    '''
    global task_flag 
    task_flag = 10 
    global dsmdb
    dsmdb = DSMDB(args1)
    dsmdb.connect()    # MySQL 연동 
    
    criteria = 9999    
    annot_check = 9999 
    not_tagged = None 

    if request.method == 'POST':
        try:
            idx = request.form['form_test']
            criteria = int(idx) 
            dsmdb.save_criteria(criteria)
        except:
            request.form['check_annot']
            dsmdb.get_dsm_criteria()
            criteria = dsmdb.dsm_criteria
            annot_check = 0 
            not_tagged_list = dsmdb.get_not_tagged(criteria)
            not_tagged = [nt[0] for nt in not_tagged_list]
            # print(not_tagged)
    return render_template('dsm_data.html',criteria=criteria, annot_check=annot_check, not_tagged=not_tagged, task_flag=task_flag)

@app.route('/dsm_data/<int:question_no>', methods=['GET', 'POST'])
def index(question_no):
    dsmdb.get_dsm_criteria()
    criteria = dsmdb.dsm_criteria
    label = dsm_label[criteria]
    mapping_idx = dsmdb.get_mapping_idx(criteria, question_no-1)
    # print(mapping_idx)
    data_len = dsmdb.get_len(criteria)
    txt = dsmdb.get_txt(mapping_idx)
    annot = int(dsmdb.get_annot(mapping_idx))
    # print(annot)
    if request.method=='POST':
        try:
            request.form['translate']
        except:
            try:
                request.form['update']
                dsmdb.update_db(mapping_idx)
                annot = int(dsmdb.get_annot(mapping_idx))
            except:
                annot_val = request.form['radioOpt']
                # print(annot_val)
                dsmdb.save_annot(mapping_idx, annot_val)
                annot = int(dsmdb.get_annot(mapping_idx))
    if question_no == 1:
        return render_template('task1_s.html', criteria=criteria, label=label, txt=txt, \
                               question_no=question_no, data_len=data_len, annot=annot)
    elif question_no == data_len:
        return render_template('task1_e.html', criteria=criteria, label=label, txt=txt, \
                               question_no=question_no, data_len=data_len, annot=annot)
    else:
        return render_template('task1_m.html', criteria=criteria, label=label, txt=txt, \
                               question_no=question_no, data_len=data_len, annot=annot)

@app.route('/', methods=['GET', 'POST'])
def main_page():
    '''
    Data Tuning 작업 Task 선택 
    '''
    global args1
    global args2 

    with open(os.path.join(cli_argse.config_path, cli_argse.task1_db)) as f:
        args1 = AttrDict(json.load(f))

    with open(os.path.join(cli_argse.config_path, cli_argse.task2_db)) as f:
        args2 = AttrDict(json.load(f))
    
    # sumdb = SUMDB(args2)
    return render_template('main.html')

def main():
    app.run(debug=True, port=9507)
    # app.run(host="192.168.123.120", debug=True, port=9509)
    
if __name__ == '__main__':
    global cli_argse 
    global upload_folder_dir
    global dsm_label 
    default_path = os.getcwd()
    upload_folder_dir = os.path.join(default_path, 'uploads')
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--config_path", type=str, default='config')
    cli_parser.add_argument("--task1_db", type=str, default='task1_db.json')
    cli_parser.add_argument("--task2_db", type=str, default='task2_db.json')
    cli_argse = cli_parser.parse_args()

    dsm_label = dict()
    dsm_label[0] = 'depressed'
    dsm_label[1] = 'loss of interest'
    dsm_label[2] = 'appetite/weight problem'
    dsm_label[3] = 'sleep disorder'
    dsm_label[4] = 'emotional instability'
    dsm_label[5] = 'fatigue'
    dsm_label[6] = 'excessive guilt/worthlessness'
    dsm_label[7] = 'cognitive problems'
    dsm_label[8] = 'suicidal thoughts'
    dsm_label[9] = 'daily'
    main()
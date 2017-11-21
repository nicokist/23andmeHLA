#!/usr/bin/env python3
import sys
from flask import Flask, request, redirect, url_for, send_from_directory,flash, render_template, abort
from werkzeug.utils import secure_filename
import os
import uuid
from celery import Celery
from subprocess import call
import csv
app = Flask(__name__)

### Make Celery work (so we can run the HLA imputation pipeline in the background).
def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app.config.update(
    CELERY_BROKER_URL='redis://some-redis:6379',
    CELERY_RESULT_BACKEND='redis://some-redis:6379',
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024 
)
celery = make_celery(app)



### The HLA imputation pipeline
@celery.task(name='HLA_pipeline')
def getHLAs(uploadpath, filename, ethnicity):
    ### Continue here. Sanity check the file and then fire of R script, collect the output.
    ### and put into databse.
    ### While this is going on the user should see a 'waiting' page
    ### When it's done the user should be shown the output
    ### For bonus points, same an md5sum of the file and link it to the uuid.
    ### Maybe use the md5sum instead of the uuid
    os.chdir(uploadpath)
    call(["plink1.9", "--23file", filename])
    call(["Rscript", "/app/HIBAG.R",ethnicity])
    os.chdir('/app/')

UPLOAD_FOLDER = '/app/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ['flask_secret_key']

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        upload_id = str(uuid.uuid4())
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No file selected.')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            if filename == '':
                filename='sanitized_uploaded.txt'
            uploadpath=os.path.join(app.config['UPLOAD_FOLDER'],upload_id)
            os.mkdir(uploadpath)
            os.chdir(uploadpath)
            file.save(filename)
            try:
                handle=open(filename,'r')
                if 'This data file generated by 23andMe at' not in next(handle):
                    flash('Error: Improperly formatted file')
                    print('Junky')
                    return redirect(request.url)
                if any(['reference human assembly build 36' in next(handle) for x in range(50)]):
                    flash('Please use a more recent 23andMe raw data file. Reference assembly 36 is not supported')               
                    return redirect(request.url)
            except:
                flash('Error: Improperly formatted file')               
                return redirect(request.url)

            if(request.values['ethnicity']=='European'):
                getHLAs.delay(uploadpath, filename, 'European')
            if(request.values['ethnicity']=='Asian'):
                getHLAs.delay(uploadpath, filename, 'Asian')
            if(request.values['ethnicity']=='Hispanic'):
                getHLAs.delay(uploadpath, filename, 'Hispanic')
            if(request.values['ethnicity']=='African'):
                getHLAs.delay(uploadpath, filename, 'African')                
            return redirect(url_for('results',
                                    upload_id=upload_id))
    return render_template('frontpage.html')

@app.route('/results/<upload_id>')
def results(upload_id):
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'],upload_id)):
        abort(404)
    try:
        HIBAG_output=os.path.join(app.config['UPLOAD_FOLDER'],upload_id,'HIBAG_output.csv')
        results=next(csv.DictReader(open(HIBAG_output,'r'),quoting=csv.QUOTE_NONNUMERIC))
    except:
        return render_template('waiting.html')
    ## Yes, this probably should use SQL instead of CSV files.
    ## But this is quicker for now.    
    results['A_prob']=round(results['A_prob'],2)
    results['B_prob']=round(results['B_prob'],2)
    results['C_prob']=round(results['C_prob'],2)
    # results['DRB1_prob']=round(results['DRB1_prob'],2)
    # results['DQA1_prob']=round(results['DQA1_prob'],2)
    # results['DQB1_prob']=round(results['DQB1_prob'],2)
    # results['DPB1_prob']=round(results['DPB1_prob'],2)

    return render_template('results.html', results=results)


@app.route('/test')
def test_something():
    result = add_together.delay(23, 42)
    a=result.wait()
    return(str(a))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
from flask import Flask, g, redirect, render_template, request, send_from_directory, url_for
from pyee import EventEmitter
from werkzeug import secure_filename

import csv
import os
import requests
import shutil
import util
import zipfile

ee = EventEmitter()

app = Flask(__name__)

uploadFolder = "uploads"
if not os.path.exists(uploadFolder):
    os.makedirs(uploadFolder)
app.config['UPLOAD_FOLDER'] = uploadFolder

downloadFolder = "downloads"
if not os.path.exists(downloadFolder):
    os.makedirs(downloadFolder)
app.config['DOWNLOAD_FOLDER'] = downloadFolder

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')
		
@app.route('/tool-selection')
def tool_selection():
    return render_template('tool-selection.html')

@app.route('/data-converter')
def data_converter():
    return render_template('data-converter.html')

@app.route('/csv-to-tsv')
def csv_to_tsv():
    return render_template('csv-to-tsv.html')

@app.route('/tsv-to-csv')
def tsv_to_csv():
    return render_template('tsv-to-csv.html')

@app.route('/upload-csv-for-tsv', methods=['POST'])
def upload_csv_for_tsv():
  
    if request.files['input-file'].filename == '':
        return render_template('csv-to-tsv.html', Message = "Please select a file")

    inputFile = request.files['input-file']
    inputFileName = secure_filename(inputFile.filename)   
    fName, fExtension = os.path.splitext(inputFileName)
    
    if fExtension == '.csv':
        inputFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputFileName))      
        outputFileName = fName+'.tsv'
        
        with open(os.path.join(app.config['UPLOAD_FOLDER'], inputFileName)) as fileHandle:
            util.convert_to_tsv(fileHandle, outputFileName)
        
        if os.path.isfile(os.path.join(app.config['DOWNLOAD_FOLDER'], outputFileName)):
            os.remove(outputFileName)
        else:
            shutil.move(outputFileName, app.config['DOWNLOAD_FOLDER'])
        
        return redirect(url_for('newFile', filename = outputFileName))

@app.route('/upload-tsv-for-csv', methods=['POST'])
def upload_tsv_for_csv():
  
    if request.files['input-file'].filename == '':
        return render_template('tsv-to-csv.html', Message = "Please select a file")

    inputFile = request.files['input-file']
    inputFileName = secure_filename(inputFile.filename)   
    fName, fExtension = os.path.splitext(inputFileName)
    
    if fExtension == '.tsv':
        inputFile.save(os.path.join(app.config['UPLOAD_FOLDER'], inputFileName))      
        outputFileName = fName+'.csv'
        
        with open(os.path.join(app.config['UPLOAD_FOLDER'], inputFileName)) as fileHandle:
            util.convert_to_csv(fileHandle, outputFileName)
        
        if os.path.isfile(os.path.join(app.config['DOWNLOAD_FOLDER'], outputFileName)):
            os.remove(outputFileName)
        else:
            shutil.move(outputFileName, app.config['DOWNLOAD_FOLDER'])
        
        return redirect(url_for('newFile', filename = outputFileName))


@app.route('/view-uploads/<filename>')
def newFile(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename )

@app.route('/data-visualizer')
def data_visualizer():
    return render_template('get-label.html')

@app.route('/get-labels', methods=['POST'])
def get_labels():
  
    if request.files['csv-file'].filename == '':
        return render_template('get-label.html', inputErrorMessage = "Please select a file")
  
    csvFile = request.files['csv-file']
    csvFileName = secure_filename(csvFile.filename)   
    fName, fExtension = os.path.splitext(csvFileName)

    if fExtension == '.csv':
        csvFile.save(os.path.join(app.config['UPLOAD_FOLDER'], csvFileName))
        fileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], csvFileName), 'r') 
        data = fileHandle.readline()
        labels = data.split(',')
        firstLabel = labels[0]
        return render_template('select-label.html', labels = labels, firstLabel = firstLabel, csvFileName = csvFileName, msg = "Select 2 labels (One label should be "+firstLabel+"):")

    else:
	    return render_template('get-label.html', typeErrorMessage = "Please upload a .csv file")

@app.route('/select-labels', methods=['POST'])
def select_labels():
  
    csvFileName = request.form['file-name']
    fileHandle = open(os.path.join(app.config['UPLOAD_FOLDER'], csvFileName), 'r') 
    data = fileHandle.readline()
    labels = data.split(',')
    firstLabel = labels[0]
    
    values = request.form.getlist('check')
    
    length = len(values)
    if length == 0 or length == 1:
	    return render_template('select-label.html', lessLabelError = "Please select 2 labels", labels = labels, firstLabel = firstLabel, csvFileName = csvFileName)
    
    if length > 2:
	    return render_template('select-label.html', moreLabelError = "You can not select more than 2 labels", labels = labels, firstLabel = firstLabel, csvFileName = csvFileName)

    if length == 2 and firstLabel not in values:
	    return render_template('select-label.html', noFirstLabelError = "Please select  "+firstLabel, labels = labels, firstLabel = firstLabel, csvFileName = csvFileName)
    
    if length == 2 and firstLabel in values:
        fName, fExtension = os.path.splitext(csvFileName)
        outputFileName = fName+'.tsv'
        with open(os.path.join(app.config['UPLOAD_FOLDER'], csvFileName)) as fileHandle:
            util.convert_to_tsv(fileHandle, outputFileName)
            if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], outputFileName)):
                os.remove(outputFileName)
            else:
	            shutil.move(outputFileName, app.config['UPLOAD_FOLDER'])
        return render_template('bar-chart.html', filename = outputFileName, xLabel = values[0], yLabel = values[1], labels = labels, firstLabel = firstLabel, csvFileName = csvFileName, msg = "Select 2 labels (One label should be "+firstLabel+"):")
	
@app.route('/tsv/get/<filename>', methods=['GET'])
def get_tsv(filename):
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)     

if __name__=='__main__':
    app.run(debug = True)

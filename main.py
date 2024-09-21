from flask import Flask, render_template, request, redirect,url_for, redirect,abort
import os
import pandas as pd
from werkzeug.utils import secure_filename
from static.python.convert import Creator
from static.python.utils import setup_logging

app = Flask(__name__)
ruta_usuario = os.getenv('USERPROFILE')
if ruta_usuario == None:
    ruta_usuario = '/home/<NombreDeUsuario>/Downloads'
else:
    ruta_descarga = os.path.join(ruta_usuario,'Downloads')

setup_logging()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf','docx']

def validate_num_pages(page_number):
    try:
        num = int(page_number)
        if num > 0:
            return num
        else:
            abort(400,description='Numero de paginas invalido')
    except ValueError:
        abort(400,description='Numero de paginas invalido')
         
@app.route('/')
def index():
    return render_template('base.html')

@app.route('/upload',methods=['GET','POST'])
def upload_file():
    
    path_file = os.getenv('UPLOAD_FOLDER')
    
    if 'file_w' not in request.files or not request.files['file_w'].filename:
        return render_template('nofile.html')
    
    file_w = request.files['file_w']
    
    if file_w and allowed_file(file_w.filename):
        filename = secure_filename(file_w.filename)
        ext = filename.rsplit('.',1)[-1]
        name_doc = 'document.'+ ext
        file_w.save(os.path.join(path_file,name_doc))  
        
        selected_num = request.form.get('pages')
        if selected_num:
            num_pages = validate_num_pages(selected_num)
            with open(os.path.join(path_file, 'selected_num.txt'), 'w') as file:
                file.write(selected_num)
            
        if 'file_e' in request.files and request.files['file_e']:
            file_e = request.files['file_e']
            filename = secure_filename(file_e.filename)
            ext = filename.rsplit('.',1)[-1]
            name_doc = 'bd.'+ ext
            file_e.save(os.path.join(path_file,name_doc))
            path_doc = os.path.join(path_file,'bd.xlsx')
            
            try:
                excel = pd.ExcelFile(path_doc)
                hojas = excel.sheet_names                                    
                return render_template('load.html',hojas_columns=hojas)
            except Exception as e:
                return str(e)
            
        return render_template('process.html')
            
    return render_template('nofile.html')

@app.route('/load_data',methods=['GET','POST'])
def selector_columns():
    selected_hoja = request.form.get('hojas')
    path_doc = os.path.join(os.getenv('UPLOAD_FOLDER'),'bd.xlsx')
    
    try:
        data = pd.read_excel(path_doc,sheet_name=selected_hoja)
        if isinstance(data, pd.DataFrame):
                columns = data.columns
                return render_template('load.html',name_columns = columns)
        
    except Exception as e:
        return str(e)

@app.route('/generator_files',methods=['GET','POST'])
def generator_file():
    path_file = os.getenv('UPLOAD_FOLDER')
    selected_num_path = os.path.join(path_file, 'selected_num.txt')
    selected_column_path = os.path.join(path_file, 'selected_column.txt')
    columns_name = None
    
    try:
        with open(selected_num_path, 'r') as file:
                num_pages = int(file.read().strip())
                
    except Exception as e:
        return str(e)
    
    try:            
        with open(selected_column_path, 'r') as file:
                name_column = file.read().strip()
        columns_name = pd.read_excel(os.path.join(path_file,'bd.xlsx'))[name_column]
    except:
        pass
    
    creator = Creator
    route_download = ruta_descarga
    path_doc = os.path.join(path_file,'document.docx')
    
    creator.docx_to_pdf(path_doc,path_file)
    creator.dividir_pdf(os.path.join(path_file,'document.pdf'),route_download,num_page=num_pages, columns_name=columns_name)
    
    for file in os.listdir(path_file):
        os.remove(os.path.join(path_file, file))
    
    return render_template('success.html')

@app.route('/file_process',methods=['GET','POST'])
def page_process():
    selected_column = request.form.get('columns')
    path_file = os.getenv('UPLOAD_FOLDER')
    
    if selected_column:
            with open(os.path.join(path_file, 'selected_column.txt'), 'w') as file:
                file.write(selected_column)
                
    return render_template('process.html')

@app.route('/generator_images',methods=['GET','POST'])
def generator_image():
    path_file = os.getenv('UPLOAD_FOLDER')
    selected_num_path = os.path.join(path_file, 'selected_num.txt')
    selected_column_path = os.path.join(path_file, 'selected_column.txt')
    columns_name = None
    
    try:
        with open(selected_num_path, 'r') as file:
                num_pages = int(file.read().strip())

        with open(selected_column_path, 'r') as file:
                name_column = file.read().strip()
        columns_name = pd.read_excel(os.path.join(path_file,'bd.xlsx'))[name_column]
    except Exception as e:
        return str(e)
   
    creator = Creator
    route_download = ruta_descarga
    path_doc = os.path.join(path_file,'document.docx')
    
    creator.docx_to_pdf(path_doc,path_file)
    list_img = creator.pdf_to_images(os.path.join(path_file,'document.pdf'),route_download)
    Creator.combine_images(list_img,route_download,num_pages,columns_name)
    
    for file in os.listdir(path_file):
        os.remove(os.path.join(path_file, file))
    
    return render_template('success.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

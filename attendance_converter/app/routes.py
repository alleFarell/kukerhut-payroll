import os
from flask import current_app as app, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from app.converter.data_processing import clean_filter_data, merge_datasets
from app.converter.report_generator import generate_report
# from app.converter.config import year_filter, month_filter

UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'reports'
ALLOWED_EXTENSIONS = {'dat'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key'  # Needed for flash messages

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(REPORT_FOLDER):
    os.makedirs(REPORT_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        year = request.form.get('year')
        month = request.form.get('month')
        
        if not year or not month:
            flash('Please provide both year and month.')
            return redirect(request.url)
        
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            flash('Invalid year or month format.')
            return redirect(request.url)

        files = request.files.getlist('file')
        if not files or len(files) != 2:
            flash('Please upload exactly two .dat files.')
            return redirect(request.url)
        
        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_paths.append(file_path)
            else:
                flash('Invalid file type. Please upload .dat files only.')
                return redirect(request.url)
        
        if len(file_paths) != 2:
            flash('Please upload exactly two valid .dat files.')
            return redirect(request.url)
        
        df_clean_1 = clean_filter_data(file_paths[0], year, month)
        df_clean_2 = clean_filter_data(file_paths[1], year, month)
        df_complete = merge_datasets(df_clean_1, df_clean_2)

        try:
            df_pivot_table = generate_report(df_complete, 'https://raw.githubusercontent.com/alleFarell/kukerhut-payroll/main/master_gaji.csv')
        except ValueError as e:
            flash(f'Error generating report: {e}')
            return redirect(request.url)

        excel_file_path = os.path.join(app.config['REPORT_FOLDER'], f'attendance_report_{year}_{month:02d}.xlsx')
        df_pivot_table.to_excel(excel_file_path)

        if os.path.exists(excel_file_path):
            flash('Report generated successfully.')
            return redirect(url_for('download_page', filename=os.path.basename(excel_file_path)))
        else:
            flash('Error generating report. File not found.')
            return redirect(request.url)
    return render_template('upload.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['REPORT_FOLDER'], filename)
    absolute_file_path = os.path.abspath(file_path)
    print(f"Attempting to download file from path: {absolute_file_path}")  # Debug statement
    if os.path.exists(absolute_file_path):
        return send_file(absolute_file_path, as_attachment=True)
    else:
        flash('File not found.')
        return redirect(url_for('index'))

@app.route('/download_page/<filename>')
def download_page(filename):
    return render_template('download.html', filename=filename)
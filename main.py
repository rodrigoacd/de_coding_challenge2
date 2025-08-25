from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
import pandas as pd
import psycopg2
import pytest
from main import app

app = Flask(__name__)

#connection to the database postgresql
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qARzCDHuNXgdgBuahnzqXpJFSsSLQxyL@interchange.proxy.rlwy.net:44382/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Endpoint de healthcheck (verifica conexión con la DB)
@app.route('/db_health', methods=['GET'])
def health_check():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # consulta simple
        return jsonify({"status": "ok", "message": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/data/insert', methods=['POST'])
def insert_data():
    """Insert data from CSV files in upload/ directory"""
    
    table_columns = {
        'hired_employees': ['id', 'name', 'date', 'department_id', 'job_id'],
        'departments': ['id', 'department_name'],
        'jobs': ['id', 'job_name']
    }
    
    upload_path = 'upload/'
    results = {}
    
    try:
        for table_name, columns in table_columns.items():
            # print(f"Processing Table: {table_name}, Columns: {columns}")
            
            file_path = upload_path + table_name + '.csv'
            
            try:
                # Read CSV file
                df = pd.read_csv(file_path, header=None, names=columns)
                
                # Handle datetime conversion for employees
                if table_name == 'hired_employees' and 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                
                # Insert using pandas to_sql (simple approach)
                df.to_sql(table_name, db.engine, if_exists='append', index=False)
                
                results[table_name] = {
                    'status': 'success',
                    'rows_inserted': len(df)
                }
                
                print(f"Successfully inserted {len(df)} rows into {table_name}")
                
            except FileNotFoundError:
                results[table_name] = {
                    'status': 'skipped',
                    'reason': f'File {file_path} not found'
                }
                print(f"File not found: {file_path}")
                
            except Exception as e:
                results[table_name] = {
                    'status': 'error',
                    'reason': str(e)
                }
                print(f"Error processing {table_name}: {str(e)}")
        
        return jsonify({
            "message": "Bulk insert completed",
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/employees-by-quarter', methods=['GET'])
def employees_by_quarter():
    """Number of employees hired for each job and department in 2021 divided by quarter"""
    try:
        query = """
        SELECT 
            d.department_name,
            j.job_name,
            COUNT(CASE WHEN EXTRACT(QUARTER FROM e.date) = 1 THEN 1 END) as Q1,
            COUNT(CASE WHEN EXTRACT(QUARTER FROM e.date) = 2 THEN 1 END) as Q2,
            COUNT(CASE WHEN EXTRACT(QUARTER FROM e.date) = 3 THEN 1 END) as Q3,
            COUNT(CASE WHEN EXTRACT(QUARTER FROM e.date) = 4 THEN 1 END) as Q4
        FROM hired_employees e
        JOIN departments d ON e.department_id = d.id
        JOIN jobs j ON e.job_id = j.id
        WHERE EXTRACT(YEAR FROM e.date) = 2021
        GROUP BY d.department_name, j.job_name
        ORDER BY d.department_name ASC
        """
        
        result = db.session.execute(db.text(query))
        data = []
        
        for row in result:
            data.append({
                'department': row[0],
                'job': row[1],
                'Q1': row[2],
                'Q2': row[3],
                'Q3': row[4],
                'Q4': row[5]
            })
        
        return jsonify({'data': data})
         # count data retrieved
        print(f"Retrieved {len(data)} records")
    
    except Exception as e:
        return jsonify({'error': 'Query failed', 'details': str(e)}), 500

@app.route('/departments-above-mean', methods=['GET'])
def departments_above_mean():
    """Number of employees hired for each job and department in 2021 divided by quarter"""
    try:
        query = """
        WITH hired_by_department AS (
            SELECT 
                d.id, 
                d.department_name, 
                count(*) AS count
            FROM hired_employees h 
            INNER JOIN departments d 
            ON h.department_id = d.id 
            WHERE EXTRACT(YEAR FROM h.date) = 2021
            GROUP BY d.id, d.department_name ),
        mean_of_hired_by_department AS (
            SELECT 
                AVG(count) AS mean
            FROM hired_by_department
        )
        SELECT
            hbd.id,
            hbd.department_name,
            hbd.count
        FROM hired_by_department hbd
        WHERE hbd.count > (SELECT mean FROM mean_of_hired_by_department)
        ORDER BY hbd.count DESC;
        """
        
        result = db.session.execute(db.text(query))
        data = []
        
        for row in result:
            data.append({
                    "department_id": row[0],
                    "department_name": row[1],
                    "count": row[2]
            })
        
        # count data retrieved
        print(f"Retrieved {len(data)} departments above mean")

        return jsonify({'data': data})
    
    except Exception as e:
        return jsonify({'error': 'Query failed', 'details': str(e)}), 500

#############################
# automated tests to the API
#############################
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/db_health')
    assert response.status_code == 200 or response.status_code == 500

def test_employees_by_quarter(client):
    response = client.get('/employees-by-quarter')
    assert response.status_code == 200

def test_departments_above_mean(client):
    response = client.get('/departments-above-mean')
    assert response.status_code == 200



if __name__ == "__main__":
    app.run(debug=True)

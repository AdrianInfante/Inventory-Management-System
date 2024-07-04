from flask import Flask, render_template, request, redirect, jsonify, url_for,request, session
import sqlite3
import json
import time
import pandas as pd
import schedule
from datetime import datetime

app = Flask(__name__)

@app.route('/upload_excel', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        # Check if a file was uploaded
        if file.filename == '':
            return "No selected file"

        if file:
            # Read the uploaded Excel file into a pandas DataFrame
            try:
                df = pd.read_excel(file)

                # Check if the DataFrame columns match the table structure
                expected_columns = ['part_number', 'description', 'Bin']
                if set(df.columns) != set(expected_columns):
                    return "The uploaded Excel file columns do not match the table structure."

                # Connect to the SQLite database
                conn = sqlite3.connect('./products.db')
                cursor = conn.cursor()

                # Iterate over the DataFrame and insert or update records
                for index, row in df.iterrows():
                    part_number = row['part_number']
                    description = row['description']
                    bin_value = row['Bin']

                    # Check if the part number already exists in the table
                    cursor.execute("SELECT * FROM parts WHERE part_number = ?", (part_number,))
                    existing_record = cursor.fetchone()

                    if existing_record:
                        # Update the existing record
                        cursor.execute("UPDATE parts SET description = ?, Bin = ? WHERE part_number = ?", (description, bin_value, part_number))
                    else:
                        # Insert a new record
                        cursor.execute("INSERT INTO parts (part_number, description, Bin) VALUES (?, ?, ?)", (part_number, description, bin_value))

                # Commit the changes and close the database connection
                conn.commit()
                conn.close()

                
                time.sleep(3)
    
                # Redirect to the /scan page
                return "File uploaded and data updated successfully."

            except Exception as e:
                return f"An error occurred: {str(e)}"

    return render_template('upload_excel.html')


users_emails = {
    'user1': 'user1@domain.com',
    'user2': 'user2@domain.com',
    'user3': 'user3@domain.com',
}


@app.route('/return_item', methods=['POST'])
def return_item():
    row_id = request.form.get('row_id')

    # Get the current datetime
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Update the "Date Returned" column for the specified row
    connection = sqlite3.connect(r'./products.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE borrow SET date_returned = ? WHERE id = ?', (current_datetime, row_id))
    connection.commit()
    connection.close()

    return jsonify({'status': 'success'})


@app.route('/borrow_list')
def borrow_list():

    connection = sqlite3.connect(r'./products.db')
    cursor = connection.cursor()
    

    cursor.execute('SELECT * FROM borrow ORDER BY id DESC')
    data = cursor.fetchall()
    

    connection.close()


    
    return render_template('borrow_list.html', data=data)

@app.route('/get_outstanding_borrowers2', methods=['GET'])
def get_outstanding_borrowers_route():
    try:
        # Implementing get_outstanding_borrowers() function logic 
        outstanding_data = get_outstanding_borrowers2()


        for row in outstanding_data:
            name = row[5]  # the name is located in the index 5. example: (1, '', 'Item1', 'A01', 'test', 'Adrian', '04-07-2024 15:19:33', None)
            if name in users_emails:  
                send_email(users_emails[name])

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error"})

def get_outstanding_borrowers2():
   
    connection = sqlite3.connect(r'./products.db')
    cursor = connection.cursor()
    
   
    cursor.execute('SELECT * FROM borrow WHERE "date_returned" IS NULL OR "date_returned" = ""')
    outstanding_data = cursor.fetchall()
    
    
    connection.close()

    # Debugging: Print the raw data fetched from the database
    print("Raw data fetched for outstanding items:")
    for row in outstanding_data:
        print(row)
        if len(row) > 0:
            name = row[5]  
            item = row[2]
            date_borrowed = row[6]
            # print(f"Name: {name}")
            for key in users_emails.keys():
                if name.capitalize() == key.capitalize():  
                    print(f"Found matching email: {users_emails[key]}")
                    send_email(users_emails[key],name,item)
                    # break
    
    return outstanding_data


def get_outstanding_borrowers():

    connection = sqlite3.connect(r'./products.db')
    cursor = connection.cursor()
    

    cursor.execute('SELECT * FROM borrow WHERE "date_returned" IS NULL OR "date_returned" = ""')
    outstanding_data = cursor.fetchall()
    

    connection.close()

    # Debugging: Print the raw data fetched from the database
    print("Raw data fetched for outstanding items:")
    for row in outstanding_data:
        print(row)
        if len(row) > 0:
            name = row[5]  
            item = row[2]
            date_borrowed_str = row[6]  
            
            # Convert date_borrowed from string to datetime object
            date_borrowed = datetime.strptime(date_borrowed_str, '%d-%m-%Y %H:%M:%S')  
            
            # Calculate the difference in days
            days_difference = (datetime.now() - date_borrowed).days
            
            # Check if the difference is exactly 3 days
            if days_difference == 3:
                # Find the corresponding email for the borrower
                for key in users_emails.keys():
                    if name.capitalize() == key.capitalize():  
                        print(f"Found matching email: {users_emails[key]}")
                        send_email(users_emails[key], name, item)
                        break  
    
    return outstanding_data

def scheduled_job():
    get_outstanding_borrowers()

# Schedule the job
schedule.every().day.at("23:59").do(scheduled_job)


def send_email(recipient_email, name,item):
    import smtplib
    from email.message import EmailMessage
    from string import Template
    from pathlib import Path 

    
    html_template = Path(r'C:\Users\Barcode PC\Desktop\SCAN\templates\reminderBorrowed.html').read_text()

    
    html_message = Template(html_template).substitute({'name': name, 'item':item})

   
    email = EmailMessage()
    email['from'] = 'UK Warehouse Center'
    email['to'] = recipient_email
    email['subject'] = 'Borrowed items reminder'
    email.set_content(html_message, 'html')

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login('ainfantevicon@gmail.com', 'fwgg wqdp etvc jvdf')
        smtp.send_message(email)
    print('Email sent')

@app.route('/returns')
def display_data_returns():
   
    connection = sqlite3.connect(r'./products.db')
    cursor = connection.cursor()
    
  
    cursor.execute('SELECT * FROM return_authorization ORDER BY id DESC')

    data = cursor.fetchall()
    

    connection.close()
    
    return render_template('returns.html', data=data)

@app.route('/borrow')
def borrow_form():
    return render_template('borrow.html')



@app.route('/submit', methods=['POST'])
def submit_form():

    name = request.form.get('dropdown')
    reason = request.form.get('reason')
    product_description = request.form.get('product-description')
    product_code = request.form.get('hidden-product-code')
    bin = request.form.get('bin')


    current_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    
    connection = sqlite3.connect(r'./products.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO borrow (part_number, description, bin, reason, name, date_borrowed) VALUES (?, ?, ?, ?, ?, ?)',
                   (product_code, product_description, bin, reason, name, current_datetime))
    connection.commit()
    connection.close()



    return redirect('/borrow')

def check_product_exists(product_code):
    connection = sqlite3.connect(r'./products.db')
    cursor = connection.cursor()


    cursor.execute('SELECT COUNT(*) FROM parts WHERE part_number = ?', (product_code,))
    count = cursor.fetchone()[0]


    cursor.execute('SELECT description, bin FROM parts WHERE part_number = ?', (product_code,))
    row = cursor.fetchone()
    description, bin_value = row if count > 0 else (None, None)

    connection.close()

    return count > 0, description, bin_value


@app.route('/check_product', methods=['POST'])
def check_product():
    data = json.loads(request.data)
    product_code = data.get('product_code')
    print(data)

    exists, description, bin_value = check_product_exists(product_code)
    

    return jsonify({'exists': exists, 'description': description, 'bin': bin_value})



@app.route('/check_description', methods=['POST'])
def check_description():
    data = json.loads(request.data)
    product_description = data.get('description')


    exists, product_code, bin_value, description = check_description_exists(product_description)

    return jsonify({'exists': exists, 'product_code': product_code, 'bin': bin_value, 'description': description})

def check_description_exists(product_description):
    connection = sqlite3.connect(r'./products.db')
    cursor = connection.cursor()


    cursor.execute('SELECT COUNT(*) FROM parts WHERE description LIKE ?', ('%' + product_description + '%',))
    count = cursor.fetchone()[0]

    if count > 0:

        cursor.execute('SELECT part_number, bin, description FROM parts WHERE description LIKE ? LIMIT 1', ('%' + product_description + '%',))
        row = cursor.fetchone()
        product_code, bin_value, description = row
    else:
        product_code, bin_value, description = None, None, None

    connection.close()

    return count > 0, product_code, bin_value, description 

@app.route('/get_matching_products', methods=['POST'])
def get_matching_products():
    data = json.loads(request.data)
    product_description = data.get('description')


    matching_products = fetch_matching_products(product_description)

    return jsonify({'products': matching_products})


def fetch_matching_products(product_description):
    connection = sqlite3.connect(r'./products.db')
    cursor = connection.cursor()


    cursor.execute('SELECT part_number, bin, description FROM parts WHERE description LIKE ?', ('%' + product_description + '%',))
    matching_products = [{'product_code': row[0], 'bin': row[1], 'description': row[2]} for row in cursor.fetchall()]

    connection.close()

    return matching_products


if __name__ == '__main__':
    
    app.run(host='10.253.0.95', port=5000, debug=True)







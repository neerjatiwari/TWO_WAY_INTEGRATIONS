import stripe
import flask
from flask import render_template, request, jsonify, session
from flask_session import Session
from datetime import datetime
import requests, json
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = flask.Flask(__name__, template_folder='Templates')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#code for connection
app.config['MYSQL_HOST'] = 'localhost'#hostname
app.config['MYSQL_USER'] = 'root'#username
app.config['MYSQL_PASSWORD'] = 'Prabhneer@123'#password
#in my case password is null so i am keeping empty
app.config['MYSQL_DB'] = 'customer_notify'#database name


mysql = MySQL(app)

@app.route('/')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))

#User Login   
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))
    if flask.request.method == 'POST':
        msg=''
        if request.method == 'POST':
            userid    = request.form['userid']
            password = request.form['password']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user_details WHERE userid = % s and password = %s', (userid, password,))
            result = cursor.fetchone()        
            
        if result:
            msg = "1"
        else:
           msg = "0"
    return msg

@app.route('/businesspage', methods=['GET', 'POST'])
def businesspage():
    if flask.request.method == 'GET':
        return(flask.render_template('business.html'))
        
@app.route('/addcustomer', methods=['GET', 'POST'])
def addcustomer():
    if flask.request.method == 'POST':

        #passing HTML form data into python variable
        namedata        = request.form['namedata']
        emaildata       = request.form['emaildata']
        phonedata       = request.form['phonedata']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        #store in db
        cursor.execute("INSERT INTO customer_detail VALUES (NULL, NULL, %s, %s, %s,  NULL)", (namedata, emaildata, phonedata))
        refid = cursor.lastrowid
        stripe.api_key = "sk_test_51NoSwASH8IAXzcwhSZwdrjUwGrpEiqaRk7ZBp3bfvkX3vI97jIGJQYGUeD65cb9UYTBzZy4Jbo8w82g5MYTojTdp00HRe4z6lD"
        #add customer in stripe too
        new_cust_data = stripe.Customer.create(
          name=namedata,
          email=emaildata,
          stripe_account='acct_1NoSwASH8IAXzcwh',
        )
        cursor.execute("UPDATE customer_detail SET stripe_cust_id = %s WHERE customer_id = %s", (new_cust_data['id'], refid,))
        mysql.connection.commit()
        
        if new_cust_data["id"] != "": 
            return "1"
        else:
            return"0"

@app.route('/addinvoice', methods=['GET', 'POST'])
def addinvoice():
    if flask.request.method == 'POST':
        
        #passing HTML form data into python variable
        subtotal       = request.form['subtotal']
        discount       = request.form['discount']
        total          = request.form['total']
        customerid     = request.form['customerid']
        
        #add invoice_mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO invoice_detail VALUES (NULL, NULL, %s, %s, %s, %s,  NULL)", (customerid, subtotal, discount, total))
        refid = cursor.lastrowid
        
        #add invoice in stripe too
        stripe.api_key = "sk_test_51NoSwASH8IAXzcwhSZwdrjUwGrpEiqaRk7ZBp3bfvkX3vI97jIGJQYGUeD65cb9UYTBzZy4Jbo8w82g5MYTojTdp00HRe4z6lD"
        new_invoice_data = stripe.Invoice.create(
          customer     = customerid,
          stripe_account='acct_1NoSwASH8IAXzcwh'
        )
        cursor.execute("UPDATE invoice_detail SET stripe_invoiceid = %s WHERE invoice_id = %s", (new_invoice_data['id'], refid,))
        mysql.connection.commit()
        
        if new_invoice_data["id"] != '':
            return "1"
        else:
            return "0"
        

 
@app.route('/editcustomer', methods=['GET', 'POST'])
def editcustomer():
    if flask.request.method == 'POST':

        #passing HTML form data into python variable
        namedata        = request.form['namedata']
        emaildata       = request.form['emaildata']
        phonedata       = request.form['phonedata']
        stripeid        = request.form['stripeid']
        custid          = request.form['custid']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        #store in db
        cursor.execute("UPDATE customer_detail SET name = %s, email = %s, phone = %s WHERE customer_id =%s",  (namedata, emaildata, phonedata, custid,))
        refid = cursor.lastrowid
        stripe.api_key = "sk_test_51NoSwASH8IAXzcwhSZwdrjUwGrpEiqaRk7ZBp3bfvkX3vI97jIGJQYGUeD65cb9UYTBzZy4Jbo8w82g5MYTojTdp00HRe4z6lD"
        #add customer in stripe too
        upd_cust_data = stripe.Customer.update(
          
        )
        print(upd_cust_data)
        mysql.connection.commit()
        
        
    return "1"

#User Login   
@app.route('/deletecustomer', methods=['GET', 'POST'])
def deletecustomer():
    if flask.request.method == 'POST':
        #passing HTML form data into python variable
        stripeid   = request.form['stripeid']
        custid   = request.form['custid']
        url = "https://api.stripe.com/v1/customers/"+stripeid
        stripe.api_key = "sk_test_51NoSwASH8IAXzcwhSZwdrjUwGrpEiqaRk7ZBp3bfvkX3vI97jIGJQYGUeD65cb9UYTBzZy4Jbo8w82g5MYTojTdp00HRe4z6lD"
        #add customer in stripe too
        rem_cust_data = stripe.Customer.delete(
          sid = stripeid,
          stripe_account='acct_1NoSwASH8IAXzcwh',
        )
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        qry = "DELETE FROM customer_detail WHERE customer_id =" +custid
        cursor1.execute(qry)
        mysql.connection.commit()
       
    if(rem_cust_data["deleted"] == True):
        return "1"
    else:
        return "0"
    
        

@app.route('/getcustrecords', methods=['GET', 'POST'])
def getcustrecords():
    if flask.request.method == 'POST':
        result = {}
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer_detail')
        result = cursor.fetchall();
    return jsonify(result)

@app.route('/getinvoicerecords', methods=['GET', 'POST'])
def getinvoicerecords():
    if flask.request.method == 'POST':
        result = {}
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM invoice_detail')
        result = cursor.fetchall();
    return jsonify(result)


@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    
    sig_header = request.headers['STRIPE_SIGNATURE']
    endpoint_secret = 'whsec_13027e9210bb86a74e8cf20046a98e808632ebbfd2db10a7bce2fd6019c8972f'
 
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e
    
    # Handle the event
    if event['type'] == 'customer.created':
      customer_data = event['data']['object']
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      #store in db
      #store in db
      cursor.execute("INSERT INTO customer_detail VALUES (NULL, %s, %s, %s, %s,  NULL)", (customer_data["id"], customer_data["name"], customer_data["email"], customer_data["phone"],))
      mysql.connection.commit()
    
    else:
      print('Unhandled event type {}'.format(event['type']))
      
    return jsonify(success=True)

if __name__ == '__main__':
    app.run()
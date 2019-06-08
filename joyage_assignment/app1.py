from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import os
import sqlite3
app = Flask(__name__)

bcrypt = Bcrypt(app)

@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template("login.html")
	else:
		return render_template("login.html")

@app.route('/login', methods=['POST'])
def do_admin_login():
	connection = sqlite3.connect('database.db')
	cursor = connection.cursor()
	sql = """SELECT * FROM user where phone_no=%s""" %(request.form['phone']) 
	cursor.execute(sql)
	records = cursor.fetchall()
	print records==[]
	if records!=[]:
		for record in records:
			phone_no = record[1]
			password=record[2]
		if bcrypt.check_password_hash(password,request.form['pwd']):
			session['logged_in'] = True
			connection.commit()
			sql="select id from user where phone_no=%s" %(request.form['phone'])
			user_id = cursor.execute(sql).fetchone()[0]
			print(user_id)
			session['user_id']=user_id
			connection.commit()
			sql="select c.name from user_community u inner join communities c on c.id=u.community_id where u.user_id=%s" %(user_id)
			community_name = cursor.execute(sql).fetchall()
			community_list=[]
			for values in community_name:
				community_list.append(values[0])
			connection.commit()
			cursor.close()
			print(community_list)
			return render_template('display_values.html', variable=community_list)
		else:
			connection.commit()
			cursor.close()
			return render_template('login.html', error ="Wrong password!")
	if records==[]:
		return render_template('login.html', error ="Not Registered!")
		

@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('signin.html')		
		
		
@app.route("/logout")
def logout():
	print(session.get['user_id'])
	session['logged_in'] = False
	session['phone_no'] =False
	session['pwd']=False
	return home()

@app.route("/community_list", methods=['POST'])
def register_page():
	if request.method =="POST":
		details = request.form
		country_code = details['c_code']
		phone=details['phone']
		pwd = details['pwd']
		pw_hash = bcrypt.generate_password_hash(pwd)
		firstname=details['firstname']
		lastname=details['lastname']
		connect = sqlite3.connect('database.db')
		cursor = connect.cursor()
		sql="select * from user where phone_no=%s" %(phone)
		check = cursor.execute(sql).fetchall()
		connect.commit()
		
		print(check)
		if not check:
			session['phone_no']=phone
			sql_command2 = '''INSERT INTO user(country_code,phone_no,password,firstname,lastname) VALUES (?,?,?,?,?)''';
			cursor.execute(sql_command2,(country_code,phone,pw_hash,firstname,lastname))
			connect.commit()
			cursor.close()	
			return render_template("community.html")
		else:
			return render_template('signin.html', error ="User Already Registered!")


@app.route('/submit_selected_communities', methods=['GET', 'POST'])
def get_data():
    if request.method == 'POST':
        selected_community = request.form.getlist('community[]')
        if selected_community:
			connect = sqlite3.connect('database.db')
			cursor = connect.cursor()
			sql="select id from user where phone_no=%s" %(session['phone_no'])
			check = cursor.execute(sql).fetchone()[0]
			print(check)
			if check:
				for values in selected_community:
					print(values)
					connect = sqlite3.connect('database.db')
					cursor = connect.cursor()
					sql_command2 = "INSERT INTO user_community(user_id,community_id) VALUES (?,?)";
					cursor.execute(sql_command2,(check,values))
					connect.commit()
			sql="select from user where phone_no=%s" %(session['phone_no'])
			connect.commit()
			print (selected_community)
	sql="select c.name from user_community u inner join communities c on c.id=u.community_id where u.user_id=%s" %(check)
    check = cursor.execute(sql).fetchall()
    community_list=[]
    for values in check:
    	community_list.append(values[0])
    connect.commit()
    cursor.close()
    print(community_list)
    return render_template('display_values.html', variable=community_list)


#@app.route('/upadte_phone_num')
#def update_phoneno():


if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run(debug=True)

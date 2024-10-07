from flask import *
import base64
import mysql.connector

app = Flask(__name__, template_folder="template", static_url_path="/static")
app.secret_key = "abc"

def get_user_info(email, password):
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='project1'
        )
        mycursor = mydb.cursor()

        sql = "SELECT firstname, lastname, photo FROM customers WHERE email=%s AND password=%s"
        val = (email, password)

        mycursor.execute(sql, val)
        user_info = mycursor.fetchone()

        mycursor.close()
        mydb.close()

        return user_info

    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")
        return None

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")

@app.route('/product')
def product():
    return render_template("product.html")

@app.route('/gallery')
def gallery():
    return render_template("gallery.html")

@app.route('/contactus')
def contactus():
    return render_template("contactus.html")




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        details = request.form
        FirstName = details['firstname']
        LastName = details['lastname']
        Email = details['email']
        Password = details['password']
        ConfirmPassword = details['confirm_password']
        MobileNumber = details['mobileno']
        Address = details['address']
        Photo = None 
        role = details['role']

        if Password != ConfirmPassword:
            error = "Passwords are not matching."
            return render_template("signup.html", error=error)

        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                image_data = file.read()
                Photo = base64.b64encode(image_data).decode('utf-8')

        try:
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='project1'
            )
            mycursor = mydb.cursor()

            sql = "INSERT INTO customers (FirstName, LastName, Email, Password, ConfirmPassword, MobileNumber, Address, Photo, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (FirstName, LastName, Email, Password, ConfirmPassword, MobileNumber, Address, Photo, role)

            mycursor.execute(sql, val)
            mydb.commit()
            mydb.close()

            return render_template("signup_success.html")
        except mysql.connector.Error as err:
            return f"An error occurred: {err}"

    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='project1'
            )
            mycursor = mydb.cursor()

            sql = "SELECT firstname, lastname, photo, role FROM customers WHERE email=%s AND password=%s"
            val = (email, password)

            mycursor.execute(sql, val)
            user_info = mycursor.fetchone()

            mycursor.close()
            mydb.close()

            if user_info:
                firstname, lastname, photo_data, role = user_info
                session['email'] = email
                session['role'] = role 
                session['firstname'] = firstname  
                session['lastname'] = lastname
                
                if role == 'user':
                    return redirect(url_for('user_dashboard'))
                else:
                    return redirect(url_for('dashboard', firstname=firstname, lastname=lastname, photo_data=photo_data))
            else:
                error = 'Invalid email or password'
                return render_template('login.html', error=error)

        except mysql.connector.Error as err:
            return f"An error occurred: {err}"

    return render_template("login.html")

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        details = request.form
        product_id = details['productId']
        product_name = details['productName']
        price = details['price']

        encoded_image = None
        if 'productImage' in request.files:
            file = request.files['productImage']
            if file and allowed_file(file.filename):
                image_data = file.read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')

        try:
            mydb = get_db()
            mycursor = mydb.cursor()

            sql = "INSERT INTO products (product_id, product_name, price, image) VALUES (%s, %s, %s, %s)"
            val = (product_id, product_name, price, encoded_image)

            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()
            mydb.close()

            return redirect(url_for('product_list'))
        except mysql.connector.Error as err:
            return f"An error occurred: {err}"

    return render_template('add_product.html')

@app.route('/product_list')
def product_list():
    search_query = request.args.get('search', '')

    try:
        mydb = get_db()
        mycursor = mydb.cursor(dictionary=True)

        if search_query:
            sql = "SELECT id, product_id, product_name, price, image FROM products WHERE product_name LIKE %s"
            val = (f"%{search_query}%",)
            mycursor.execute(sql, val)
        else:
            sql = "SELECT id, product_id, product_name, price, image FROM products"
            mycursor.execute(sql)
        products = mycursor.fetchall()

        mycursor.close()
        mydb.close()

        return render_template('product_list.html', products=products)
    except mysql.connector.Error as err:
        return f"An error occurred: {err}"

def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='project1'
    )

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        details = request.form
        new_product_name = details['product_name']
        new_price = details['price']
        encoded_image = None

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                image_data = file.read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')

        try:
            mydb = get_db()
            mycursor = mydb.cursor()

            if encoded_image:
                sql = "UPDATE products SET product_name = %s, price = %s, image = %s WHERE id = %s"
                val = (new_product_name, new_price, encoded_image, product_id)
            else:
                sql = "UPDATE products SET product_name = %s, price = %s WHERE id = %s"
                val = (new_product_name, new_price, product_id)

            mycursor.execute(sql, val)
            mydb.commit()

            mycursor.close()
            mydb.close()

            return redirect(url_for('product_list'))
        except mysql.connector.Error as err:
            return f"An error occurred: {err}"
    else:
        try:
            mydb = get_db()
            mycursor = mydb.cursor(dictionary=True)

            sql = "SELECT * FROM products WHERE id = %s"
            val = (product_id,)
            mycursor.execute(sql, val)
            product = mycursor.fetchone()

            mycursor.close()
            mydb.close()

            if product:
                return render_template('edit_product.html', product=product)
            else:
                return "Product not found"
        except mysql.connector.Error as err:
            return f"An error occurred: {err}"

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        mydb = get_db()
        mycursor = mydb.cursor()
        sql = "DELETE FROM products WHERE id = %s"
        mycursor.execute(sql, (product_id,))
        mydb.commit()

        mycursor.close()
        mydb.close()

        return redirect(url_for('product_list'))
    except mysql.connector.Error as err:
        return f"An error occurred: {err}"

@app.route('/dashboard')
def dashboard():
    
    if 'email' in session:
        firstname = request.args.get('firstname')
        lastname = request.args.get('lastname')
        photo_data = request.args.get('photo_data')
        return render_template('dashboard.html', firstname=firstname, lastname=lastname, photo_data=photo_data)
    else:
        return redirect(url_for('login'))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/logout')
def logout():
    session.pop('email', None)
    response = make_response(redirect(url_for('login')))
    return response
    

@app.route('/user_dashboard')
def user_dashboard():
    if 'email' in session:
        if session.get('role') == 'user':
            try:
                mydb = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='root',
                    database='project1'
                )
                mycursor = mydb.cursor(dictionary=True)

                mycursor.execute("SELECT * FROM products")
                products = mycursor.fetchall()
                print(products)  # Add this line to inspect the data returned by the query

                mycursor.close()
                mydb.close()

                firstname = session.get('firstname')
                lastname = session.get('lastname')

                return render_template('user_dashboard.html', products=products, firstname=firstname, lastname=lastname)
            except mysql.connector.Error as err:
                return f"An error occurred: {err}"
        else:
            return "You are not authorized to access this page."
    else:
        return redirect(url_for('login'))

@app.route('/view_cart')
def view_cart():
    if 'email' in session:
        if session.get('role') == 'user':
            cart = session.get('cart', [])
            if cart:
                try:
                    mydb = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='root',
                        database='project1'
                    )
                    mycursor = mydb.cursor(dictionary=True)

                    placeholders = ','.join(['%s'] * len(cart))
                    sql = f"SELECT * FROM products WHERE product_id IN ({placeholders})"

                    mycursor.execute(sql, cart)
                    cart_products = mycursor.fetchall()

                    mycursor.close()
                    mydb.close()

                    return render_template('view_cart.html', cart_products=cart_products)
                except mysql.connector.Error as err:
                    app.logger.error(f"Database error occurred: {err}")
                    return "An error occurred while retrieving cart data. Please try again later."
            else:
                return render_template('view_cart.html', cart_products=[], message="Your cart is empty.")
        else:
            return "You are not authorized to access this page."
    else:
        return redirect(url_for('login'))




@app.route('/add_to_cart/<int:product_id>', methods=['GET','POST'])
def add_to_cart(product_id):
    if 'email' in session:
        if session.get('role') == 'user':
            
            cart = session.get('cart', [])
            cart.append(product_id)
            session['cart'] = cart
            return redirect(url_for('user_dashboard'))
        else:
            return "You are not authorized to perform this action."
    else:
        return redirect(url_for('login'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'email' in session:
        if session.get('role') == 'user':
            cart = session.get('cart', [])
            if product_id in cart:
                cart.remove(product_id)
                session['cart'] = cart
            return redirect(url_for('view_cart'))
        else:
            return "You are not authorized to perform this action."
    else:
        return redirect(url_for('login'))

def get_visitors():
    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='project1'
        )
        mycursor = mydb.cursor(dictionary=True)

        sql = "SELECT firstname, lastname FROM customers"
        mycursor.execute(sql)

        visitors = mycursor.fetchall()

        mycursor.close()
        mydb.close()

        return visitors

    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")
        return []

@app.route('/visitors')
def visitors():
    visitors = get_visitors()
    return render_template("visitors.html", visitors=visitors)

@app.route('/order', methods=['GET','POST'])
def order():
    if request.method == 'POST':
        
        
        full_name = request.form['full-name']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip']
        phone_number = request.form['phone-number']
        payment_option = request.form['payment-option']

        try:
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='project1'
            )
            cursor = mydb.cursor()

            
            sql = "INSERT INTO orders (full_name, address, city, state, zip_code, phone_number, payment_option) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (full_name, address, city, state, zip_code, phone_number, payment_option)
            cursor.execute(sql, val)
            mydb.commit()

            cursor.close()
            mydb.close()

            
            return redirect(url_for('order_summary',
                                    full_name=full_name,
                                    address=address,
                                    city=city,
                                    state=state,
                                    zip_code=zip_code,
                                    phone_number=phone_number,
                                    payment_option=payment_option))
        except mysql.connector.Error as err:
      
            app.logger.error(f"Database error occurred: {err}")
            return "An error occurred while placing the order. Please try again later."
    
   
    return render_template('order.html', error_message='Method Not Allowed'), 405


def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='project1'
    )


@app.route('/order_summary', methods=['GET','POST'])
def order_summary():
    if request.method == 'POST':
        try:
           
            order_details = request.json
            
           
            full_name = order_details['full_name']
            address = order_details['address']
            city = order_details['city']
            state = order_details['state']
            zip_code = order_details['zip_code']
            phone_number = order_details['phone_number']
            payment_option = order_details['payment_option']
            items = order_details['items']

            
            mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='project1'
            )
            cursor = mydb.cursor()

           
            sql_order = "INSERT INTO orders (full_name, address, city, state, zip_code, phone_number, payment_option) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val_order = (full_name, address, city, state, zip_code, phone_number, payment_option)
            cursor.execute(sql_order, val_order)
            order_id = cursor.lastrowid

            
            for item in items:
                product_name = item['name']
                price = item['price']
                quantity = item['quantity']
                sql_item = "INSERT INTO order_items (order_id, product_name, price, quantity) VALUES (%s, %s, %s, %s)"
                val_item = (order_id, product_name, price, quantity)
                cursor.execute(sql_item, val_item)

            mydb.commit()
            cursor.close()
            mydb.close()

            return "Your order has been successfully placed. Thank you!"

        except mysql.connector.Error as err:
            app.logger.error(f"Database error occurred: {err}")
            return "An error occurred while placing the order. Please try again later.", 500

    return render_template('order_summary.html')
@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form['email']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        error = "Passwords do not match."
        return render_template('forgot_password.html', error=error)

    try:
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='project1'
        )
        mycursor = mydb.cursor()

        sql = "SELECT email FROM customers WHERE email=%s"
        val = (email,)
        mycursor.execute(sql, val)
        user = mycursor.fetchone()

        if user:
            update_sql = "UPDATE customers SET password=%s, confirmpassword=%s WHERE email=%s"
            update_val = (new_password, confirm_password, email)
            mycursor.execute(update_sql, update_val)
            mydb.commit()
            success = "Password has been successfully reset."
            return render_template('forgot_password.html', success=success)
        else:
            error = "Email address not found."
            return render_template('forgot_password.html', error=error)

    except mysql.connector.Error as err:
        return f"An error occurred: {err}"

    finally:
        if 'mycursor' in locals():
            mycursor.close()
        if 'mydb' in locals():
            mydb.close()
            
if __name__ == "__main__":
    app.run(debug=True)

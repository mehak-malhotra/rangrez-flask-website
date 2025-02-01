from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    else:
        return render_template('login.html')
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match.")

        if check_email_exists(email):
            return render_template('login.html', error="Email already exists. Please login.")

        add_user_to_csv(username, email, password)

        return redirect(url_for('login'))
    else:
        return render_template('register.html')

def check_email_exists(email):
    with open('static/users.csv', 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row[email] == email:
                return True
    return False

def read_cart_from_csv():
    cart = []
    with open('static/cart.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cart.append({'name': row['Product Name'], 'price': row['Price'], 'image': row['Image']})
    return cart

def calculate_total_cost():
    total_cost = 0
    with open('static/cart.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            price_str = row['Price'].replace('Rs. ', '').replace(',', '')  
            price_float = float(price_str) if price_str else 0
            print("Price for {}: {}".format(row['Product Name'], price_float))  
            total_cost += price_float
    print("Total cost:", total_cost) 
    return total_cost

def add_user_to_csv(username, email, password):
    with open('static/users.csv', 'a', newline='') as file:
        fieldnames = ['username', 'email', 'password']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({'username': username, 'email': email, 'password': password})

@app.route('/bridal')
def bridal():
    lehengas = read_lehengas_from_csv('static/bridal.csv')
    return render_template('bridal.html', lehengas=lehengas)

@app.route('/designer')
def designer():
    lehengas = read_lehengas_from_csv('static/designer.csv')
    return render_template('designer.html', lehengas=lehengas)

@app.route('/indo_western')
def indo_western():
    lehengas = read_lehengas_from_csv('static/indo_western.csv')
    return render_template('indo_western.html', lehengas=lehengas)

def read_lehengas_from_csv(filename):
    lehengas = []
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            lehenga = {
                'name': row['Name'],
                'price': row['Price'],
                'offer': row['Offer'],
                'image': row['Image']
            }
            lehengas.append(lehenga)
    return lehengas


@app.route('/checkout', methods=['POST','GET'])
def checkout():
        return render_template('home.html')

@app.route('/cart')
def cart():
    total_cost = calculate_total_cost()
    cart = []
    with open('static/cart.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            cart.append({'name': row[0], 'price': row[1], 'image': row[2]})
    return render_template('cart.html', cart=cart[1:] , total_cost=total_cost)

def read_cart_from_csv():
    cart = []
    with open('static/cart.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cart.append({'name': row['Product Name'], 
                         'price': row['Price'], 
                         'image': row['Image']})
    return cart

@app.route('/remove_item_from_cart', methods=['POST'])
def remove_item_from_cart():
    updated_cart = []
    name = request.form['name']
    with open('static/cart.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] != name:
                updated_cart.append(row)
    with open('static/cart.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_cart)
    return redirect('/cart')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    image = data.get('image')

    with open('static/cart.csv', 'a', newline='') as csvfile:
        fieldnames = ['Product Name', 'Price', 'Image']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({'Product Name': name, 'Price': price, 'Image': image})

    return jsonify({'message': 'Item added to cart successfully!'})

if __name__ == "__main__":
    app.run(debug=True)

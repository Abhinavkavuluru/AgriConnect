from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify,g
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import paypalrestsdk
from twilio.rest import Client
from werkzeug.security import generate_password_hash
from flask_cors import CORS
from web3 import Web3
import json
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# MySQL configurations
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'flask_login'
}

# db_config = {
#     'host': 'host.docker.internal',  # ✅ This points to your actual machine from inside Docker
#     'user': 'root',
#     'password': '1234',
#     'database': 'flask_login'
# }

import os


app.secret_key = 'your_secret_key'  # Set a secret key for session management

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


# Database connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# Initial route (Redirects to login page)
@app.route('/')
def login_redirect():
    return redirect(url_for('login'))  # Always redirect to login initially



@app.route('/home_farmer')
def home_farmer():
    if 'logged_in' not in session or session.get('user_type') != 'farmer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))
    return render_template('home_farmer.html', email=session.get('email'), session_id=session.get('session_id'))


@app.route('/home_buyer')
def home_buyer():
    if 'logged_in' not in session or session.get('user_type') != 'buyer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))
    return render_template('home_buyer.html', email=session.get('email'), session_id=session.get('session_id'))


# Login route
import uuid  # Import UUID for unique session identifiers

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, password, user_type FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user and check_password_hash(user[1], password):
                    session.clear()  # Clears old session to prevent mix-ups
                    session['logged_in'] = True
                    session['user_id'] = user[0]
                    session['email'] = email
                    session['user_type'] = user[2]
                    session['session_id'] = str(uuid.uuid4())  # Unique session per login

                    # Redirect based on user type
                    if user[2] == 'farmer':
                        return redirect(url_for('home_farmer'))
                    elif user[2] == 'buyer':
                        return redirect(url_for('home_buyer'))
                    else:
                        flash('Unknown user type!', 'danger')
                        return redirect(url_for('login'))
                else:
                    flash('Invalid email or password.', 'danger')

            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')

            finally:
                cursor.close()
                conn.close()
        else:
            flash('Database connection failed.', 'danger')

    return render_template('login.html')



@app.before_request
def before_request():
    # Make the email from session available globally for all templates
    g.email = session.get('email')

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'email' not in session:
        return jsonify({"success": False, "error": "User not logged in"})

    data = request.get_json()
    receiver_email = data.get('receiver_email')  # Ensure correct field name
    message = data.get('message')
    sender_email = session['email']

    if not receiver_email or not message:
        return jsonify({"success": False, "error": "Invalid data"})

    print(f"Received message from {sender_email} to {receiver_email}: {message}")  # Debugging print

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert into `chat_messages` table
        cursor.execute("INSERT INTO chat_messages (sender_email, receiver_email, message) VALUES (%s, %s, %s)",
                       (sender_email, receiver_email, message))
        conn.commit()

        print("Message successfully inserted into the chat_messages table.")  # Debugging print

        cursor.close()
        conn.close()

        return jsonify({"success": True})

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging print
        return jsonify({"success": False, "error": str(e)})

@app.route('/home')
def home():
    if 'logged_in' not in session or not session['logged_in']:  # If user is not logged in
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    email = session.get('email')  # Get the user's email from session
    user_type = session.get('user_type')  # Get the user's type from session
    print(f"Logged in email: {email}") 
    if not email or not user_type:
        flash('User not found!', 'danger')
        return redirect(url_for('login'))

    # Redirect based on user type
    if user_type == 'farmer':
        return render_template('home_farmer.html', email=email)
    elif user_type == 'buyer':
        return render_template('home_buyer.html', email=email)
    else:
        flash('Unknown user type!', 'danger')
        return redirect(url_for('login'))

    

# Route to display the list of crops for buyers
@app.route('/view_crops')
def view_crops():
    if 'logged_in' not in session or not session['logged_in']:  # If user is not logged in
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Connect to the database to fetch crops
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT crop_name, price_per_ton, quantity, total_amount, farmer_email, created_at FROM crops")  # Fetch all crops from the database
            crops = cursor.fetchall()  # Get all rows from the result
            return render_template('crops_list.html', crops=crops)  # Pass the crops data to the template
        except Exception as e:
            flash(f'Error fetching crops: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    flash('Database connection failed.', 'danger')
    return redirect(url_for('home'))


# About page route
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/details', methods=['GET'])
def details():
    if 'email' not in session:
        return redirect(url_for('login'))

    farmer_email = session['email']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM crops WHERE farmer_email = %s", (farmer_email,))
    crops = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('details.html', crops=crops)

@app.route('/messages')
def messages():
    if 'logged_in' not in session or not session['logged_in']:
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))

    email = g.email  # Logged-in user's email

    conn = get_db_connection()
    grouped_messages = {}

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chat_messages WHERE sender_email = %s OR receiver_email = %s ORDER BY created_at ASC",
                (email, email)
            )
            messages = cursor.fetchall()

            # Group messages by the participant (either sender or receiver)
            for message in messages:
                other_user = message[1] if message[2] == email else message[2]  # Determine conversation partner
                if other_user not in grouped_messages:
                    grouped_messages[other_user] = []
                grouped_messages[other_user].append(message)

            return render_template('messages.html', grouped_messages=grouped_messages)

        except Exception as e:
            flash(f'Error fetching messages: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    flash('Database connection failed.', 'danger')
    return redirect(url_for('home'))

# Manual page route
@app.route('/manual')
def manual():
    return render_template('manual.html')

# Profile page route
@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['phone_number']
        user_type = request.form['user_type']  # Capture user type from the form
        hashed_password = generate_password_hash(password)

        # Connect to database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (email, password, phone_number, user_type) VALUES (%s, %s, %s, %s)",
                               (email, hashed_password, phone_number, user_type))
                conn.commit()
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))  # Redirect to login after successful registration
            except mysql.connector.IntegrityError:
                flash('Email already exists. Please try another one.', 'danger')
            except Exception as e:
                flash(f'Error occurred during registration: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Database connection failed.', 'danger')

    return render_template('register.html')  # Render registration page if not POST



@app.route('/details1', methods=['GET'])
def details1():
    if 'email' not in session:
        flash('Please log in to view or update your details.', 'warning')
        return redirect(url_for('login'))

    user_email = session['email']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, email, first_name, last_name, location, phone_number, upi_id FROM user_details WHERE email = %s", (user_email,))
    user_details = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('details1.html', user_details=user_details)

@app.route('/submit_details', methods=['POST'])
def submit_details():
    if 'email' not in session:
        flash('Please log in to enter details.', 'danger')
        return redirect(url_for('login'))

    email = session['email']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    location = request.form['location']
    phone_number = request.form['phone_number']
    upi_id = request.form.get('upi_id', None)  # Optional field

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_details WHERE email = %s", (email,))
    existing_details = cursor.fetchone()

    try:
        if existing_details:
            cursor.execute("""
                UPDATE user_details 
                SET first_name=%s, last_name=%s, location=%s, phone_number=%s, upi_id=%s 
                WHERE email=%s
            """, (first_name, last_name, location, phone_number, upi_id, email))
            flash('Details updated successfully!', 'success')
        else:
            cursor.execute("""
                INSERT INTO user_details (email, first_name, last_name, location, phone_number, upi_id) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (email, first_name, last_name, location, phone_number, upi_id))
            flash('Details submitted successfully!', 'success')

        conn.commit()

    except Exception as e:
        flash(f'Error submitting details: {str(e)}', 'danger')

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('details1'))

from datetime import datetime

@app.route('/add_crop', methods=['POST'])
def add_crop():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    crop_id = request.form.get('crop_id')  # Check if it's an edit
    crop_name = request.form['crop_name']
    price_per_ton = float(request.form['price_per_ton'])
    quantity = float(request.form['quantity'])
    total_amount = float(request.form['total_amount'])
    farmer_email = session.get('email')
    
    # Get the current timestamp
    created_at = datetime.now()  # This gets the local server time

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if crop_id:
            cursor.execute(
                "UPDATE crops SET crop_name=%s, price_per_ton=%s, quantity=%s, total_amount=%s WHERE id=%s AND farmer_email=%s",
                (crop_name, price_per_ton, quantity, total_amount, crop_id, farmer_email)
            )
            flash('Crop details updated successfully!', 'success')
        else:
            cursor.execute(
                "INSERT INTO crops (crop_name, price_per_ton, quantity, total_amount, farmer_email, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (crop_name, price_per_ton, quantity, total_amount, farmer_email, created_at)
            )
            flash('Crop added successfully!', 'success')

        conn.commit()
    except Exception as e:
        flash(f'Error updating crop: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('details'))



@app.route('/get_crops', methods=['GET'])
def get_crops():
    if 'email' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    farmer_email = session['email']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM crops WHERE farmer_email = %s", (farmer_email,))
    crops = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({"success": True, "crops": crops})

@app.route('/make_payment1')
def make_payment1():
    return render_template('make_payment1.html')

@app.route('/capture_payment', methods=['POST'])
def capture_payment():
    data = request.get_json()
    order_id = data.get("orderID")

    if not order_id:
        return jsonify({"success": False, "error": "Invalid Order ID"}), 400

    # Simulated response for local testing (no real money transfer)
    return jsonify({"success": True, "message": "Payment captured successfully (Test Mode)"})

@app.route('/payment_success')
def payment_success():
    name = request.args.get('name', 'N/A')  # Get name from query params
    amount = request.args.get('amount', '0.00')  # Get amount
    transaction_id = request.args.get('transaction_id', 'N/A')  # Get transaction ID

    return render_template('payment_success.html', name=name, amount=amount, transaction_id=transaction_id)

@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    return redirect(url_for('login'))  # Redirect to login page

@app.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('forgot_password.html')

# Function to send OTP
def send_otp_via_twilio(phone_number, otp):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your AgriConnect OTP is: {otp}. It is valid for 5 minutes.",
        from_=TWILIO_PHONE_NUMBER,
        to=f"+91{phone_number}"  # Adjust country code if needed
    )
    return message.sid

@app.route('/send_otp', methods=['POST'])
def send_otp():
    phone_number = request.form['phone_number']
    
    # Connect to the database
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database connection failed."})
    
    try:
        cursor = conn.cursor()
        # Check if phone number exists in the users table
        cursor.execute("SELECT email FROM users WHERE phone_number = %s", (phone_number,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "error": "There is no account matched with the entered mobile number."})
        
        # Generate a random 6-digit OTP
        otp = random.randint(100000, 999999)
        
        # Store OTP in session
        session['otp'] = otp
        session['phone_number'] = phone_number

        # Send OTP via Twilio
        send_otp_via_twilio(phone_number, otp)

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
    finally:
        cursor.close()
        conn.close()


# Verify OTP Route
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form['otp']
    stored_otp = session.get('otp')

    if stored_otp and str(entered_otp) == str(stored_otp):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route('/reset_password', methods=['POST'])
def reset_password():
    phone_number = request.form['phone_number']
    new_password = request.form['new_password']
    
    # Hash the new password before storing it
    hashed_password = generate_password_hash(new_password)

    # Connect to the database
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database connection failed."})

    try:
        cursor = conn.cursor()
        # Update password for the given phone number
        cursor.execute("UPDATE users SET password = %s WHERE phone_number = %s", (hashed_password, phone_number))
        conn.commit()

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
    finally:
        cursor.close()
        conn.close()



from web3 import Web3

# Connect to the Hardhat node running on the Docker network
web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))


if web3.is_connected():
    print("✅ Connected to Ethereum Network")
else:
    print("❌ Failed to connect to Ethereum")





# Load Smart Contract ABI (Ensure correct path)
with open("contracts/FarmerBuyerContract.json", "r") as abi_file:
    contract_data = json.load(abi_file)
    contract_abi = contract_data["abi"]  # Extract ABI


# Define Contract Address (Replace with actual deployed contract address)
contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

if web3.is_connected():
    print("✅ Connected to Ethereum Network")
else:
    print("❌ Failed to connect to Ethereum")


@app.route('/fetch_contract_details', methods=['GET'])
def fetch_contract_details():
    """Fetch contract details from MySQL using the contract address"""
    try:
        contract_address = request.args.get("contract_address")

        if not contract_address:
            return jsonify({"error": "Contract address is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM contracts WHERE contract_address = %s", (contract_address,))
        contract_data = cursor.fetchone()

        cursor.close()
        conn.close()

        if not contract_data:
            return jsonify({"error": "No contract found for the given address"}), 404

        return jsonify({
            "buyer": contract_data["buyer_address"],
            "farmer": contract_data["farmer_address"],
            "price": float(contract_data["price"]),
            "contract_years": contract_data["contract_years"],
            "quantity": contract_data["quantity"],
            "product_type": contract_data["product_type"],
            "payment_made": contract_data["payment_made"],
            "payment_completed_years": contract_data["payment_completed_years"],  # ✅ New Field
            "order_accepted": contract_data["order_accepted"],
            "delivery_confirmed": contract_data["delivery_confirmed"]
        })

    except Exception as e:
        print(f"❌ Error Fetching Contract Details: {e}")
        return jsonify({"error": str(e)}), 500

from flask_cors import cross_origin
from flask import g
@app.route('/deploy_contract', methods=['POST'])
@cross_origin()
def deploy_contract():
    """Store deployed contract details in MySQL with emails"""
    try:
        data = request.get_json()
        farmer_address = data.get("farmer_address")  # ✅ Use dynamic MetaMask address
        buyer_address = data.get("buyer_address")
        contract_years = int(data.get("contract_years"))
        price = float(data.get("price"))
        quantity = int(data.get("quantity"))
        product_type = data.get("product_type")
        contract_address = data.get("contract_address")  # Get deployed contract address
        buyer_email = data.get("buyer_email")  # ✅ Fetch buyer's email from frontend
        farmer_email = g.email  # ✅ Get farmer's email from session

        print(f"✅ Storing contract in database: {contract_address} with Farmer: {farmer_address} and Farmer Email: {farmer_email}")

        # ✅ Insert contract details into MySQL (initialize `payment_completed_years = 0`)
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO contracts 
            (farmer_address, buyer_address, contract_address, contract_years, price, quantity, product_type, 
             payment_completed_years, farmer_email, buyer_email)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (farmer_address, buyer_address, contract_address, contract_years, price, quantity, product_type, 0, farmer_email, buyer_email)

        cursor.execute(sql, values)
        conn.commit()

        print(f"✅ Contract successfully stored: {contract_address}")

        cursor.close()
        conn.close()

        return jsonify({"message": "Contract stored in MySQL successfully!", "contract_address": contract_address})

    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return jsonify({"error": f"MySQL Error: {err}"}), 500
    except Exception as e:
        print(f"❌ Error Storing Contract: {e}")
        return jsonify({"error": str(e)}), 500





from web3 import Web3

@app.route('/make_payment', methods=['POST'])
def make_payment():
    """Allow only the buyer to make a payment and update the database"""
    try:
        data = request.get_json()
        buyer_address = data.get("buyer_address")
        contract_address = data.get("contract_address")

        # ✅ Fetch contract details
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT payment_completed_years FROM contracts WHERE contract_address = %s", (contract_address,))
        contract_data = cursor.fetchone()

        cursor.close()
        conn.close()

        if not contract_data:
            return jsonify({"error": "Contract not found in database"}), 404

        completed_years = contract_data["payment_completed_years"]

        # ✅ Update MySQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE contracts 
            SET payment_made = TRUE, 
                payment_completed_years = payment_completed_years + 1,
                order_accepted = FALSE,
                delivery_confirmed = FALSE
            WHERE contract_address = %s
        """  
        
        cursor.execute(sql, (contract_address,))
        conn.commit()

        cursor.close()
        conn.close()

        print(f"✅ Payment recorded for contract: {contract_address}, Total completed years: {completed_years + 1}")

        return jsonify({
            "message": "Payment Successful!",
            "updated_completed_years": completed_years + 1
        })

    except Exception as e:
        print(f"❌ Error Processing Payment: {e}")
        return jsonify({"error": "Unexpected server error"}), 500



@app.route('/check_payment_validity', methods=['POST'])
def check_payment_validity():
    """Check if a payment is allowed before processing it on the blockchain"""
    try:
        data = request.get_json()
        buyer_address = data.get("buyer_address")
        contract_address = data.get("contract_address")

        # ✅ Fetch contract details
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT contract_years, payment_completed_years FROM contracts WHERE contract_address = %s", (contract_address,))
        contract_data = cursor.fetchone()

        cursor.close()
        conn.close()

        if not contract_data:
            return jsonify({"error": "Contract not found in database"}), 404

        total_years = contract_data["contract_years"]
        completed_years = contract_data["payment_completed_years"]

        # ✅ Ensure the buyer cannot overpay beyond contract duration
        if completed_years >= total_years:
            return jsonify({"error": "All contract payments have already been completed"}), 400

        return jsonify({"message": "Payment Allowed"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




from web3 import Web3

@app.route('/confirm_delivery', methods=['POST'])
def confirm_delivery():
    """Allow only the registered farmer to confirm delivery if payment is made"""
    try:
        data = request.get_json()
        farmer_address = data.get("farmer_address")
        contract_address = data.get("contract_address")

        if not contract_address or not farmer_address:
            print("❌ Contract address or farmer address is missing in request")
            return jsonify({"error": "Contract address and farmer address are required"}), 400

        try:
            # ✅ Convert to checksum address
            farmer_address = Web3.to_checksum_address(farmer_address)
            contract_address = Web3.to_checksum_address(contract_address)
        except ValueError as e:
            print(f"❌ Invalid Ethereum address format: {e}")
            return jsonify({"error": "Invalid contract or farmer address format"}), 400

        print(f"🔍 Converted Checksum Addresses: Farmer - {farmer_address}, Contract - {contract_address}")

        # ✅ Fetch contract details
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT farmer_address, payment_made FROM contracts 
            WHERE contract_address = %s
        """, (contract_address,))
        contract_data = cursor.fetchone()

        cursor.close()
        conn.close()

        if not contract_data:
            print(f"❌ Contract {contract_address} not found in database")
            return jsonify({"error": "Contract not found in database"}), 404

        database_farmer = Web3.to_checksum_address(contract_data["farmer_address"])
        payment_made = contract_data["payment_made"]

        print(f"✅ Found contract. Registered farmer: {database_farmer}, Payment Made: {payment_made}")

        # ✅ Ensure only the registered farmer can confirm delivery
        if farmer_address != database_farmer:
            print(f"❌ Unauthorized farmer {farmer_address} tried to confirm delivery.")
            return jsonify({"error": "Unauthorized farmer! Only the registered farmer can confirm delivery."}), 403

        # ✅ Ensure payment is made before confirming delivery
        if not payment_made:
            print(f"❌ Delivery confirmation attempted before payment.")
            return jsonify({"error": "Payment has not been completed yet. Please complete payment before confirming delivery."}), 400

        # ✅ Update MySQL database (NO BLOCKCHAIN TRANSACTION)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql = """
                UPDATE contracts 
                SET delivery_confirmed = TRUE 
                WHERE contract_address = %s
            """
            cursor.execute(sql, (contract_address,))
            conn.commit()

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ Database update error: {e}")
            return jsonify({"error": "Failed to update delivery status in database"}), 500

        print(f"✅ Delivery confirmed for contract: {contract_address}")

        return jsonify({"message": "Delivery Confirmed!"})

    except Exception as e:
        print(f"❌ Unexpected Error Confirming Delivery: {e}")
        return jsonify({"error": "Unexpected server error"}), 500


from web3 import Web3

from web3 import Web3

@app.route('/accept_order', methods=['POST'])
def accept_order():
    """Update order accepted status in the database and verify the buyer"""
    try:
        data = request.get_json()
        buyer_address = data.get("buyer_address")
        contract_address = data.get("contract_address")

        if not buyer_address or not contract_address:
            print("❌ Missing buyer address or contract address in request")
            return jsonify({"error": "Buyer address and contract address are required"}), 400

        try:
            buyer_address = Web3.to_checksum_address(buyer_address)  # ✅ Convert to checksum format
            contract_address = Web3.to_checksum_address(contract_address)
        except ValueError as e:
            print(f"❌ Invalid Ethereum address format: {e}")
            return jsonify({"error": "Invalid buyer or contract address format"}), 400

        print(f"🔍 Buyer Address Received: {buyer_address}")

        # ✅ Fetch contract details from the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT buyer_address, delivery_confirmed FROM contracts 
            WHERE contract_address = %s
        """, (contract_address,))
        contract_data = cursor.fetchone()

        if not contract_data:
            cursor.close()
            conn.close()
            print(f"❌ Contract not found for contract address: {contract_address}")
            return jsonify({"error": "Contract not found"}), 404

        stored_buyer = Web3.to_checksum_address(contract_data["buyer_address"])
        delivery_confirmed = contract_data["delivery_confirmed"]

        print(f"✅ Stored Buyer in Database: {stored_buyer}, Delivery Confirmed: {delivery_confirmed}")

        # ✅ Ensure only the registered buyer can accept the order
        if buyer_address != stored_buyer:
            print(f"❌ Unauthorized buyer {buyer_address} tried to accept the order.")
            return jsonify({"error": "Unauthorized buyer! Only the assigned buyer can accept the order."}), 403

        # ✅ Ensure delivery is confirmed before accepting the order
        if not delivery_confirmed:
            print(f"❌ Order acceptance attempted before delivery confirmation.")
            return jsonify({"error": "Delivery has not been confirmed yet. Please wait to confirm delivery by farmer before accepting the order."}), 400

        # ✅ Update MySQL database
        cursor.execute("""
            UPDATE contracts 
            SET order_accepted = TRUE
            WHERE contract_address = %s
        """, (contract_address,))
        conn.commit()

        cursor.close()
        conn.close()

        print(f"✅ Order accepted for contract {contract_address}")

        return jsonify({"message": "Order Accepted!"})

    except Exception as e:
        print(f"❌ Error Accepting Order: {e}")
        return jsonify({"error": "Unexpected server error"}), 500



@app.route('/view_contract')
def view_contract():
    if 'email' not in session:
        flash("You must be logged in to view contracts.", "warning")
        return redirect(url_for('login'))

    user_email = g.email  # Fetch logged-in user's email from session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch all contracts where the user is either a farmer or buyer
        cursor.execute("""
            SELECT farmer_address, buyer_address, contract_address, farmer_email, buyer_email 
            FROM contracts 
            WHERE farmer_email = %s OR buyer_email = %s
        """, (user_email, user_email))

        contracts = cursor.fetchall()  # Fetch all matching rows

        if not contracts:
            flash("No contracts found for this user.", "danger")
            return redirect(url_for('home'))

        # Prepare a list of contract details
        contract_list = []
        for contract in contracts:
            if user_email == contract["farmer_email"]:
                other_email = contract["buyer_email"]  # Show buyer's email
                other_address = contract["buyer_address"]  # Show buyer's blockchain address
            else:
                other_email = contract["farmer_email"]  # Show farmer's email
                other_address = contract["farmer_address"]  # Show farmer's blockchain address

            contract_list.append({
                "other_email": other_email,
                "other_address": other_address,
                "contract_address": contract["contract_address"]
            })

        return render_template('view_contract.html', contracts=contract_list)

    except Exception as e:
        flash(f"Error fetching contract details: {str(e)}", "danger")
        return redirect(url_for('home'))

    finally:
        cursor.close()
        conn.close()


@app.route("/submit_comment", methods=["POST"])
def submit_comment():
    data = request.get_json()

    # Extracting data from the incoming request
    contract_address = data.get("contract_address")
    comment = data.get("comment")

    # Check if both fields are provided
    if not contract_address or not comment:
        return jsonify({"success": False, "message": "Contract address and comment are required."})

    # Establish a database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the comment for the respective contract address
    try:
        cursor.execute("""
            UPDATE contracts
            SET comment = %s
            WHERE contract_address = %s
        """, (comment, contract_address))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "No contract found with the provided address."})

        return jsonify({"success": True, "message": "Comment submitted successfully!"})

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)})

    finally:
        cursor.close()
        conn.close()


        
@app.route("/get_comment_by_farmer_email", methods=["GET"])
def get_comment_by_farmer_email():
    farmer_email = request.args.get("farmer_email")

    if not farmer_email:
        return jsonify({"success": False, "message": "Farmer email is required."})

    # Establish a database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT c.comment
            FROM contracts c
            WHERE c.farmer_email = %s
        """, (farmer_email,))

        result = cursor.fetchone()

        if result:
            return jsonify({"success": True, "comment": result[0]})
        else:
            return jsonify({"success": False, "message": "No comment found for this farmer."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

    finally:
        cursor.close()
        conn.close()




@app.route('/buyer')
def buyer_page():
    if 'logged_in' not in session or not session['logged_in']:  # Check if the user is logged in
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    return render_template('buyer.html')

@app.route('/farmer')
def farmer_page():
    if 'logged_in' not in session or not session['logged_in']:  # Check if the user is logged in
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    return render_template('farmer.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


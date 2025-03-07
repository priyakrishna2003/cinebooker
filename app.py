from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
import uuid
import json
from flask import jsonify 
# import mysql.connector
# from mysql.connector import Error
from pymysql import MySQLError

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For print messages

# RDS configuration
rds_host = '127.0.0.1'  # Replace with your RDS endpoint
rds_port = 3306  # Default MySQL port
db_username = 'priya'  # Replace with your database username
db_password = 'Priyakrishna@2003'  # Replace with your database password
db_name = 'movie_ticketbooking4'  # Replace with your database name

print(rds_host)

# Connect to the RDS MySQL database
def connect_to_rds():
    try:
        connection = pymysql.connect(
            host=rds_host,
            user=db_username,
            password=db_password,
            database=db_name,
            port=rds_port
        )
        print("Connected to the database!")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_movies_data(): 
    data = [
        {
            "imageUrl": "https://static.toiimg.com/thumb/msid-113094554,width-400,resizemode-4/113094554.jpg",
            "name": "Jigra",
            "rating": "Rating: 8.2/10",
            "votes": "Total Votes: 150,000+"
        },
        {
            "imageUrl": "https://m.media-amazon.com/images/M/MV5BMTNjOWNlOGMtZjQ4Zi00NDNkLTg1OWMtMzFmM2QwY2I4MDYxXkEyXkFqcGc@._V1_.jpg",
            "name": "Vicky Vidya ka woh wala video",
            "rating": "Rating: 7.9/10",
            "votes": "Total Votes: 100,000+"
        },
        {
            "imageUrl": "https://i.pinimg.com/736x/41/cb/48/41cb487e857d661f3e342d1836efbcde.jpg",
            "name": "Stree 2",
            "rating": "Rating: 8.4/10",
            "votes": "Total Votes: 250,000+"
        },
        {
            "imageUrl": "https://i.ytimg.com/vi/6QGRnDMdvj4/sddefault.jpg",
            "name": "Sikaar",
            "rating": "Rating: 8.0/10",
            "votes": "Total Votes: 180,000+"
        },
        {
            "imageUrl": "https://i.ytimg.com/vi/-duZSm2EAME/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLB0Jb9ckLhtJ_OXwXg8A2qqmSOAvw",
            "name": "White Bird",
            "rating": "Rating: 7.8/10",
            "votes": "Total Votes: 90,000+"
        },
        {
            "imageUrl": "https://nenews.in/wp-content/uploads/2024/08/local-kung-fu-1200x720.jpg",
            "name": "Local Kung Fu 3",
            "rating": "Rating: 8.3/10",
            "votes": "Total Votes: 130,000+"
        }
    ]
        
    return data

# Homepage route where movies are displayed
@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("inside post")
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        Phone_number =request.form['phone_number']

        print("phone number: ", Phone_number, "\ntype: ",  type(Phone_number))
   
        connection = connect_to_rds()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO user (name, email, password, Phone_number) VALUES (%s, %s, %s, %s)",
                               (name, email, password, Phone_number))
                connection.commit()
                print("User registered successfully. Redirecting to login...")

                return redirect(url_for('login'))

            except pymysql.MySQLError as err:
                print(f"Error: {err}")
            finally:
                cursor.close()
                connection.close()
        else:
            print("Database connection failed!")
    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = connect_to_rds()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT * FROM user WHERE email=%s AND password=%s", (email, password))
                user = cursor.fetchone()

                if user:
                    print("current user", user)
                    session['user_id'] = user[0]
                    session['username'] = user[3]

                    print(f"User logged in: {user}. Redirecting to select movie...")
                    print(f"User logged in: {user}. Redirecting to select movie...")

                    return redirect(url_for('select_movie'))
                else:
                    print("Invalid login. Please try again.")
            except pymysql.MySQLError as err:
                print(f"Error: {err}")
            finally:
                cursor.close()
                connection.close()
        else:
            print("Database connection failed!")
    return render_template('login.html')

# @app.route('/select_movie')
# def  select_movie():
#     return render_template('select_movie.html')

# Route for displaying movie details based on movie_id
@app.route('/select_movie', methods=['GET', 'POST'])
def select_movie():
    
    connection = connect_to_rds()
    
    if request.method == 'POST':
        movie_id = request.form['movie_id']

        if connection:
            cursor = connection.cursor()
            try:
                # Fetch the movie details based on the movie_id from the 'movie_details' table

                cursor.execute("SELECT * FROM movie WHERE movie_id = %s", (movie_id,))
                movie = cursor.fetchone()

                if not movie:
                    print("Movie not found!")
                    return redirect(url_for('select_movie', movie_id=movie_id))

                if movie:
                    # Get the data from the form (you'll need to have a form in the HTML template for name, theater_id, and date)
                    name = session['username']
                    user_id = session['user_id']
                    # theater_id = request.form['theater_id']
                    # date = request.form['date']

                    # Insert booking details into the 'booking_details' table

                    session['booking_id'] = uuid.uuid4()

                    cursor.execute("""
                        INSERT INTO booking_details (booking_id, user_id,name, movie_id)
                        VALUES (%s, %s, %s, %s)
                    """, (session['booking_id'], user_id,name, movie_id))


                    connection.commit()

                    # print("Booking successful!", "success")
                    return redirect(url_for('seat_booking'))

            except pymysql.MySQLError as err:
                print(f"Error fetching movie or storing booking details: {err}")
                return redirect(url_for('register'))
            finally:
                cursor.close()
                connection.close()
        else:
            print("Failed to connect to the database!")
            return redirect(url_for('register'))

    # Render the movie.html template and pass the movie details
    return render_template('select_movie.html', movies=get_movies_data())



# Sample seat data
# seats = [{"seat_number": i, "selected": False} for i in range(1, 41)]  # 20 seats

@app.route('/seat', methods=['GET', 'POST'])
def seat_booking():
    print("set booking with method: ", request.method);

    if request.method == 'POST':
        try:

            print("POST request is",  request.form)
            connection = connect_to_rds()
            selected_seats = request.form['selected_seats']

            print("seat nmbers: ",  selected_seats)

            seat_list = json.dumps(list(map(int,selected_seats.split(',')))) 

            if connection:
                cursor = connection.cursor()
                    
                cursor.execute("""
                        UPDATE booking_details SET seats = %s WHERE booking_id = %s
                    """, (seat_list, session['booking_id']))
        
                connection.commit()
                print("Seat booking successful!")
                return redirect(url_for('booking'))
        except pymysql.MySQLError as err:
            print(f"Error fetching movie or storing booking details: {err}")
            return  redirect(url_for('seat_booking'))


    return render_template('seat.html')




#     if request.method == 'POST':
#         # Get booking details and selected seats
#         name = request.form['name']
#         selected_seats = request.form.getlist('selectedSeats')

#         connection = connect_to_rds()
        
#         if connection:
#             cursor = connection.cursor()
#             try:
#                 # Insert booking into booking_details
#                 cursor.execute("INSERT INTO booking_details (name) VALUES (%s)", (name,))
#                 booking_id = cursor.lastrowid  # Get the last inserted booking ID

#                 # Insert selected seats into booking_seats
#                 for seat in selected_seats:
#                     cursor.execute("INSERT INTO booking_seats (booking_id, seat_no) VALUES (%s, %s)", (booking_id, seat))
                
#                 connection.commit()
#                 print("Seats booked successfully!", "success")
#             except MySQLError as err:
#                 print(f"Error: {err}")
#             finally:
#                 cursor.close()
#                 connection.close()
        
#         # return redirect(url_for('seat'))

    # return render_template('seat.html', seats=seats)

# @app.route('/confirm', methods=['POST'])
# def confirm_booking():
#     # selected_seats = request.form['selected_seats']
#     seat_list = selected_seats.split(',') if selected_seats else []

#     #process seat_list as needed
#     return f"Seats confirmed: {','.join(seat_list)}" #display confirmed seats

@app.route('/bookingdetails')
def booking():
    try:
        connection = connect_to_rds()

        if connection:
            cursor = connection.cursor()

            cursor.execute("""SELECT m.name, b.name, b.seats FROM 
                            booking_details b join movie m on
                            b.movie_id=m.movie_id
                            where b.booking_id=%s""", (session['booking_id']))
            booking_details = cursor.fetchall()
            
            booking_details = list(booking_details[0])
            print(booking_details)
            seat = json.loads(booking_details[2])
            seat_count = len(seat)
            print(seat_count)
            total_price = seat_count * 300
            booking_details.append(total_price)
            print(booking_details)
            if len(booking_details) > 0:
                keys = ['movie', 'name', 'seats','total_price']
                ticket = dict(zip(keys, booking_details)) 

                # return ticket
            cursor.close()
            return render_template('bookingdetails.html', ticket = ticket , seat = seat)

    except pymysql.MySQLError as err:
        print(f"Error fetching movie or storing booking details: {err}")
        return  redirect(url_for('seat_booking'))

@app.route('/payment')
def confirm_payment():

    return render_template('payment.html')

@app.route('/ticket')
def ticket():
     try:
        connection = connect_to_rds()

        if connection:
            cursor = connection.cursor()

            cursor.execute("""SELECT m.name, b.name, b.seats FROM 
                            booking_details b join movie m on
                            b.movie_id=m.movie_id
                            where b.booking_id=%s""", (session['booking_id']))
            booking_details = cursor.fetchall()
            
            booking_details = list(booking_details[0])
            print(booking_details)
            seat = json.loads(booking_details[2])
            seat_count = len(seat)
            print(seat_count)
            total_price = seat_count * 300
            booking_details.append(total_price)
            print(booking_details)
            if len(booking_details) > 0:
                keys = ['movie', 'name', 'seats','total_price']
                ticket = dict(zip(keys, booking_details)) 

                # return ticket
            cursor.close()

            image = ""
            movie_name = ticket['movie']
            movies = get_movies_data()
            for movie in movies:
                if movie['name'] ==  movie_name:
                    image = movie['imageUrl']

            return render_template('ticket.html', ticket = ticket , seat = seat, image = image)
        
     except pymysql.MySQLError as err:
        print(f"Error fetching movie or storing booking details: {err}")
        return  redirect(url_for('select_movie'))


if __name__ == '__main__':
    app.run(debug=True, port=3000)
</create_file>


from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, request, jsonify, redirect
from flask_mail import Mail, Message
import json
import random
import csv



app = Flask(__name__)

DAYS_PER_WEEK = 7
SLOTS_PER_DAY = 3

movies = {}
seats_per_screen = {}
# schedule=[]
unscheduled_seats = 0




@app.route('/')
def index():
    return render_template('index.html')



@app.route('/inputPage')
def input_page():
    return render_template('inputPage.html')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'cineplanner21@gmail.com'  # Replace with your Gmail address
app.config['MAIL_PASSWORD'] = 'your_gmail_password'  # Replace with your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'cineplanner21@gmail.com'  # Replace with your Gmail address

mail = Mail(app)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['Name']
        phone = request.form['Phone']
        email = request.form['Email']
        message_content = request.form['Message']

        # Send email
        send_email(name, phone, email, message_content)

        # Redirect to a success page or do something else
        return redirect(url_for('success'))

    return render_template('contact.html')

@app.route('/success')
def success():
    return render_template('success.html')

def send_email(name, phone, email, message_content):
    subject = 'New Contact Form Submission'
    body = f"Name: {name}\nPhone: {phone}\nEmail: {email}\nMessage: {message_content}"

    message = Message(subject, recipients=['cineplanner21@gmail.com'])
    message.body = body

    try:
        mail.send(message)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")




@app.route('/schedulePage', methods=['POST'])
def schedule_page():
    num_movies = int(request.form.get("numMovies"))
    movie_names = request.form.get("movieNames").split('\n')
    seat_requests = list(map(int, request.form.get("seatRequests").split('\n')))
    num_screens = int(request.form.get("numScreens"))
    available_seats = list(map(int, request.form.get("availableSeats").split('\n')))
    schedule = [[None] * num_screens for _ in range(DAYS_PER_WEEK * SLOTS_PER_DAY)]

    for i in range(num_movies):
        movie_name = movie_names[i]
        demand = seat_requests[i]
        movies[movie_name] = {"demand": demand}

    for screen in range(num_screens):
        screen_name = f"Screen{screen + 1}"
        seats_per_screen[screen_name] = available_seats[screen]

    unscheduled_seats = 0

    for day in range(DAYS_PER_WEEK):
        for slot in range(SLOTS_PER_DAY):
            for screen in range(num_screens):
                movie_list = list(movies.keys())
                random.shuffle(movie_list)
                movie = None

                for candidate_movie in movie_list:
                    if movies[candidate_movie]["demand"] > 0:
                        scheduled_demand = min(
                            movies[candidate_movie]["demand"],
                            seats_per_screen[f"Screen{screen + 1}"],
                        )
                        movies[candidate_movie]["demand"] -= scheduled_demand
                        schedule[day * SLOTS_PER_DAY + slot][screen] = (
                            candidate_movie,
                            scheduled_demand,
                        )

                        unscheduled_seats += max(
                            0, movies[candidate_movie]["demand"]
                        )

                        for additional_screen in range(num_screens):
                            if (
                                additional_screen != screen
                                and movies[candidate_movie]["demand"] > 0
                            ):
                                scheduled_demand = min(
                                    movies[candidate_movie]["demand"],
                                    seats_per_screen[f"Screen{additional_screen + 1}"],
                                )
                                movies[candidate_movie]["demand"] -= scheduled_demand
                                schedule[day * SLOTS_PER_DAY + slot][
                                    additional_screen
                                ] = (candidate_movie, scheduled_demand)

                        break

    schedule_data = ""
    for day in range(DAYS_PER_WEEK):
        schedule_data += f"Day {day + 1}:\n"
        for slot in range(SLOTS_PER_DAY):
            schedule_data += f"{slot * 3:02d}:00pm:\n"
            for screen in range(num_screens):
                schedule_entry = schedule[day * SLOTS_PER_DAY + slot][screen]
                if schedule_entry:
                    movie, demand = schedule_entry
                    schedule_data += (
                        f"{slot * 3:02d}:00pm\t{' ' * 4}Screen {screen + 1} ({seats_per_screen[f'Screen{screen + 1}']} seats)\t{movie}\n"
                    )
    with open('schedule_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Day', 'Time Slot', 'Screen', 'Seats', 'Movie'])
        for day in range(DAYS_PER_WEEK):
            for slot in range(SLOTS_PER_DAY):
                for screen in range(num_screens):
                    schedule_entry = schedule[day * SLOTS_PER_DAY + slot][screen]
                    if schedule_entry:
                        movie, demand = schedule_entry
                        writer.writerow([day + 1, f"{slot * 3:02d}:00pm", screen + 1, seats_per_screen[f'Screen{screen + 1}'], movie])


    # Display the count of unscheduled seats
    # schedule_data += f"\nSeats that could not be scheduled: {unscheduled_seats}"
    print(schedule_data)

    return render_template("schedulePage.html", schedule_data=schedule_data, num_screens=num_screens)
# import pandas as pd
# import matplotlib
# matplotlib.use('Agg')  # Set the backend before importing pyplot
# import matplotlib.pyplot as plt
# from io import BytesIO
# import base64

# @app.route('/analysisPage')
# def analysis_page():
#     # Load your movies dataset (replace 'your_dataset.csv' with your actual dataset file)
#     movies_df = pd.read_csv('schedule_data.csv')

#     # Calculate scheduling efficiency
#     total_seats = sum(seats_per_screen.values()) * DAYS_PER_WEEK * SLOTS_PER_DAY
#     scheduled_seats = sum([entry[1] for day_schedule in schedule for entry in day_schedule if entry])
#     efficiency = scheduled_seats / total_seats if total_seats > 0 else 0

#     # Example Analysis: Movie Distribution Across Time Slots
#     movie_distribution = pd.DataFrame(schedule)
#     movie_distribution = movie_distribution.applymap(lambda x: 1 if x else 0)
#     total_movies_per_slot = movie_distribution.sum(axis=1)

#     # Plotting the bar chart
#     plt.figure(figsize=(30, 6))
#     plt.bar(range(len(total_movies_per_slot)), total_movies_per_slot, color='lightgreen')
#     plt.xlabel('Time Slot')
#     plt.ylabel('Number of Movies Scheduled')
#     plt.title('Movie Distribution Across Time Slots')
#     plt.xticks(range(DAYS_PER_WEEK * SLOTS_PER_DAY), [f'Day {i//SLOTS_PER_DAY + 1}, {i % SLOTS_PER_DAY * 3}:00pm' for i in range(DAYS_PER_WEEK * SLOTS_PER_DAY)])
#     plt.grid(axis='y')

#     # Save the plot to a BytesIO object
#     img_stream = BytesIO()
#     plt.savefig(img_stream, format='png')
#     img_stream.seek(0)
#     movie_distribution_chart = base64.b64encode(img_stream.read()).decode('utf-8')
#     plt.close()

#     return render_template('analysisPage.html', movie_distribution_chart=movie_distribution_chart, efficiency=efficiency)

# @app.after_request
# def after_request(response):
#     plt.savefig('static/images/efficiency_chart.png')  # Save the plot to a file
#     plt.close('all')  # Close the plot to release resources
#     return response

if __name__ == '__main__':
    app.run(debug=True)


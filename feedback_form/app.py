from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Initialize the database


def init_db():
    with sqlite3.connect('feedback.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            teacher TEXT,
            knowledge_base TEXT,
            communication_skills TEXT,
            sincerity TEXT,
            interest_generated TEXT,
            integration_material TEXT,
            integrate_content TEXT,
            accessibility TEXT,
            ability_design TEXT,
            overall_rating TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password TEXT
        )''')
        conn.commit()



@app.route('/')
def home():
    return redirect(url_for('register'))



@app.route('/feedback_form', methods=['GET', 'POST'])
def feedback_form():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    username = session['username']
    teachers = ["Rahul sir", "Deepak sir", "patale sir", "sanjay kumar", "ranu"]
    
    if request.method == 'POST':
        teacher = request.form['teacher']
        if not teacher:
            flash('Please select a teacher.')
            return redirect('/feedback_form')
        
        with sqlite3.connect('feedback.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM feedback WHERE user_id = ? AND teacher = ?', (user_id, teacher))
            existing_feedback = c.fetchone()
            
            if existing_feedback:
                flash('You have already reviewed this teacher. Please select another teacher.')
                for t in teachers:
                    c.execute('SELECT * FROM feedback WHERE user_id = ? AND teacher = ?', (user_id, t))
                    if not c.fetchone():
                        teacher = t
                        break
                else:
                    flash('You have already reviewed all teachers. Thank you!')
                    return redirect('/display_feedback')
        
        required_fields = ['knowledge_base', 'communication_skills', 'sincerity', 'interest_generated', 'integration_material', 'integrate_content', 'accessibility', 'ability_design', 'overall_rating']
        for field in required_fields:
            if field not in request.form or not request.form[field]:
                flash('Please fill out all fields.')
                return redirect('/feedback_form')

        data = (
            user_id,
            teacher,
            request.form['knowledge_base'],
            request.form['communication_skills'],
            request.form['sincerity'],
            request.form['interest_generated'],
            request.form['integration_material'],
            request.form['integrate_content'],
            request.form['accessibility'],
            request.form['ability_design'],
            request.form['overall_rating']
        )

        with sqlite3.connect('feedback.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO feedback (user_id, teacher, knowledge_base, communication_skills, sincerity, interest_generated, integration_material, integrate_content, accessibility, ability_design, overall_rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
            conn.commit()

        return redirect('/thankyou')
    
    else:
        with sqlite3.connect('feedback.db') as conn:
            c = conn.cursor()
            for teacher in teachers:
                c.execute('SELECT * FROM feedback WHERE user_id = ? AND teacher = ?', (user_id, teacher))
                if not c.fetchone():
                    break
            else:
                flash('You have already reviewed all teachers. Thank you!')
                return redirect('/logout')
    
    return render_template('feedback_form.html', username=username, teacher=teacher, teachers=teachers, all_reviews_completed=(teacher is None))




@app.route('/display_feedback2')
def display_feedback():
    with sqlite3.connect('feedback.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT user_id, teacher, knowledge_base, communication_skills, sincerity, interest_generated, integration_material, integrate_content, accessibility, ability_design, overall_rating 
            FROM feedback
        ''')
        feedbacks = c.fetchall()

    feedback_data = {}
    for feedback in feedbacks:
        user_id = feedback[0]
        teacher_name = feedback[1]
        feedback_dict = {
            'username': user_id,  # Assuming user_id can be used as username; adjust if necessary
            'knowledge_base': feedback[2],
            'communication_skills': feedback[3],
            'sincerity': feedback[4],
            'interest_generated': feedback[5],
            'integration_material': feedback[6],
            'integrate_content': feedback[7],
            'accessibility': feedback[8],
            'ability_design': feedback[9],
            'overall_rating': feedback[10]
        }

        if teacher_name not in feedback_data:
            feedback_data[teacher_name] = {}
        if user_id not in feedback_data[teacher_name]:
            feedback_data[teacher_name][user_id] = []
        
        feedback_data[teacher_name][user_id].append(feedback_dict)

    return render_template('display_feedback2.html', feedback_data=feedback_data)




@app.route('/thankyou')
def thank_you():
    i = 0
    while i<5 :
        i+=1
        return redirect('/feedback_form')
    flash('Thank you for your feedbacks.')
    return redirect('/logout')





@app.route('/display_users')
def display_users():
    with sqlite3.connect('feedback.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users')
        users = c.fetchall()
        # print(users)  # Debugging: Print user data to console
    
    return render_template('display_users.html', users=users)




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])  # Hash the password before storing

        with sqlite3.connect('feedback.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
            user = c.fetchone()
            if user:
                flash('You are already registered. Please log in.')
                return redirect('/login')

            c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('feedback.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = c.fetchone()

            if user and check_password_hash(user[3], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect('/feedback_form')
            else:
                flash('Login failed. Check your username and password and try again.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/login')

from flask import Flask, render_template, url_for, send_from_directory
import sqlite3
import matplotlib.pyplot as plt
import os



# Define the path to the charts directory
CHARTS_DIR = os.path.join(os.getcwd(), 'charts')

@app.route('/report')
def report():
    with sqlite3.connect('feedback.db') as conn:
        c = conn.cursor()
        
        # Fetch distinct teacher names
        c.execute('SELECT DISTINCT teacher FROM feedback')
        teachers = c.fetchall()
        
        # Fetch feedback data for each teacher
        feedback_data = {}
        for teacher in teachers:
            teacher_name = teacher[0]
            c.execute('SELECT knowledge_base, communication_skills, sincerity, interest_generated, integration_material, integrate_content, accessibility, ability_design, overall_rating FROM feedback WHERE teacher = ?', (teacher_name,))
            feedbacks = c.fetchall()
            feedback_data[teacher_name] = feedbacks

    # Create a directory for the charts if it doesn't exist
    if not os.path.exists(CHARTS_DIR):
        os.makedirs(CHARTS_DIR)

    # Clear out old charts
    for filename in os.listdir(CHARTS_DIR):
        file_path = os.path.join(CHARTS_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Generate and save bar charts for each teacher
    chart_paths = {}
    criteria = [
        'Knowledge Base', 'Communication Skills', 'Sincerity', 'Interest Generated',
        'Integration Material', 'Integrate Content', 'Accessibility', 'Ability Design', 'Overall Rating'
    ]
    categories = ['Very good', 'Good', 'Satisfactory', 'Unsatisfactory']
    
    for teacher, feedbacks in feedback_data.items():
        try:
            # Count occurrences of each rating category for each criterion
            counts = {criterion: {category: 0 for category in categories} for criterion in criteria}
            for feedback in feedbacks:
                for i, rating in enumerate(feedback):
                    if rating in counts[criteria[i]]:
                        counts[criteria[i]][rating] += 1

            # Generate bar chart
            plt.figure(figsize=(14, 8))
            bar_width = 0.2
            index = range(len(criteria))

            for i, category in enumerate(categories):
                values = [counts[criterion][category] for criterion in criteria]
                plt.bar([x + bar_width * i for x in index], values, bar_width, label=category)

            plt.xlabel('Criteria')
            plt.ylabel('Number of Users')
            plt.title(f'Feedback for {teacher}')
            plt.xticks([x + bar_width * (len(categories) / 2) for x in index], criteria, rotation=45)
            plt.legend()

            # Save the chart
            chart_filename = f'{teacher}_feedback.png'
            chart_path = os.path.join(CHARTS_DIR, chart_filename)
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()

            print(f'Chart saved: {chart_path}')  # Debug: Print chart path

            # Store the path to the chart
            chart_paths[teacher] = url_for('chart', filename=chart_filename)
        except Exception as e:
            print(f'Error generating chart for {teacher}: {e}')

    return render_template('report.html', chart_paths=chart_paths)

@app.route('/charts/<filename>')
def chart(filename):
    return send_from_directory(CHARTS_DIR, filename)




if __name__ == '__main__':
    init_db()
    app.run(debug=True)




from flask import Flask, render_template, request, redirect, url_for
import pickle
import numpy as np

# Load data from pickle files
try:
    popular_df = pickle.load(open('popular.pkl', 'rb'))
    pt = pickle.load(open('pt.pkl', 'rb'))
    books = pickle.load(open('books.pkl', 'rb'))
    similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))
except FileNotFoundError as e:
    print(f"Error loading file: {e}")
    exit(1)  # Exit if files are missing

app = Flask(__name__)

# Home route
@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

# Recommendation route
@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    
    # Convert user input and data to lowercase for case-insensitive matching
    user_input = user_input.lower()
    pt_lower = pt.index.str.lower()

    if user_input not in pt_lower:
        return render_template('recommend.html', data=[],
                               error="Book not found in the database.")

    index = np.where(pt_lower == user_input)[0][0]
    
    # Print debug info
    print(f"User input: {user_input}, Index found: {index}")

    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'].str.lower() == pt_lower[i[0]]]
        if not temp_df.empty:
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        else:
            print(f"No data found for: {pt.index[i[0]]}")
        
        data.append(item)

    return render_template('recommend.html', data=data)

# Contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Handle form submission from contact page
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    # Here you can process the form data (e.g., send email or store in a database)
    print(f"Name: {name}, Email: {email}, Message: {message}")
    
    # Redirect to the thank you page after submission
    return redirect(url_for('thank_you'))

# Thank you page route
@app.route('/thank_you')
def thank_you():
    return render_template('thankyou.html')

if __name__ == '__main__':
    app.run(debug=True)

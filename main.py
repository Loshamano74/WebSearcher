from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from googlesearch import search

app = Flask(__name__)

CACHE_DIR = "cache"
FIRST_TIME_FILE = "first_time.json"

def load_search_history():
    history_file_path = os.path.join(CACHE_DIR, "history.json")
    try:
        with open(history_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_search_history(history):
    history_file_path = os.path.join(CACHE_DIR, "history.json")
    with open(history_file_path, 'w') as file:
        json.dump(history, file)

def load_first_time():
    first_time_file_path = os.path.join(CACHE_DIR, FIRST_TIME_FILE)
    try:
        with open(first_time_file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"first_time": True}

def set_not_first_time():
    first_time_file_path = os.path.join(CACHE_DIR, FIRST_TIME_FILE)
    try:
        with open(first_time_file_path, 'w') as file:
            json.dump({"first_time": False}, file)
        print("first_time.json updated successfully")
    except Exception as e:
        print("Error updating first_time.json:", e)

@app.route('/')
def index():
    first_time = load_first_time()["first_time"]
    return render_template('index.html', first_time=first_time, search_results=None)

@app.route('/search', methods=['POST'])
def search_person():
    full_name = request.form['full_name']
    query = f"{full_name}"
    urls = list(search(query))

    # Load existing search history
    history = load_search_history()

    # Add current search to history
    history.append({"name": full_name, "results": urls})

    # Save updated search history
    save_search_history(history)

    if load_first_time()["first_time"]:
        set_not_first_time()

    return render_template('index.html', first_time=False, search_results=urls)

@app.route('/history')
def history():
    search_history = load_search_history()
    return jsonify(search_history)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    first_time_file_path = os.path.join(CACHE_DIR, FIRST_TIME_FILE)
    if not os.path.exists(first_time_file_path):
        with open(first_time_file_path, 'w') as file:
            json.dump({"first_time": True}, file)
        
    app.run(debug=True)

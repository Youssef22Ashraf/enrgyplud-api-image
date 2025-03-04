from flask import Flask, request, jsonify, send_from_directory
import os
from eppy import modeleditor
from eppy.modeleditor import IDF
from pyngrok import ngrok
import tempfile
from flask_cors import CORS
from dotenv import load_dotenv  # Import the dotenv library

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Set the EnergyPlus IDD file path
iddfile = "/usr/local/EnergyPlus/Energy+.idd"
IDF.setiddname(iddfile)

# Define the output directory for simulation results
OUTPUT_DIR = "/content/simulation_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set the ngrok auth token from the environment variable
ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))

# Root route
@app.route('/')
def index():
    return "Welcome to the EnergyPlus API! Use /api/run-simulation to run a simulation."

@app.route('/api/run-simulation', methods=['POST'])
def run_simulation():
    try:
        # Check if both IDF and EPW files are provided
        if 'idf_file' not in request.files or 'epw_file' not in request.files:
            return jsonify({'error': 'Both IDF and EPW files are required'}), 400

        idf_file = request.files['idf_file']
        epw_file = request.files['epw_file']

        # Check if the files are not empty
        if idf_file.filename == '' or epw_file.filename == '':
            return jsonify({'error': 'Empty file upload detected'}), 400

        # Create a temporary directory to store the uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            idf_path = os.path.join(temp_dir, idf_file.filename)
            epw_path = os.path.join(temp_dir, epw_file.filename)

            idf_file.save(idf_path)
            epw_file.save(epw_path)

            # Check if the files have the correct extensions
            if not idf_path.endswith('.idf') or not epw_path.endswith('.epw'):
                return jsonify({'error': 'Invalid file format. Please upload .idf and .epw files'}), 400

            # Run the EnergyPlus simulation
            idf = IDF(idf_path, epw_path)
            idf.run(
                expandobjects=True,
                readvars=True,
                output_directory=OUTPUT_DIR
            )

            # Locate the eplustbl.htm file
            eplus_table_path = os.path.join(OUTPUT_DIR, 'eplustbl.htm')
            if not os.path.exists(eplus_table_path):
                return jsonify({
                    'status': 'error',
                    'message': 'Simulation completed but eplustbl.htm was not generated'
                }), 500

            # Return the HTML file as a response
            return send_from_directory(
                OUTPUT_DIR,
                'eplustbl.htm',
                as_attachment=True,
                mimetype='text/html'
            )

    except Exception as e:
        # Handle any exceptions that occur during the simulation
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/output-files', methods=['GET'])
def list_output_files():
    try:
        # List all files in the output directory
        files = os.listdir(OUTPUT_DIR)
        return jsonify({
            'status': 'success',
            'files': files
        }), 200
    except Exception as e:
        # Handle any exceptions that occur while listing files
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def start_server():
    # Start the Flask app
    #ngrok.set_auth_token(userdata.get('NGROK AUTH TOKEN' ))
    #public_url = ngrok.connect(5000)
    #print(f"public URL: {public_url}")
    app.run(host='0.0.0.0', port=8080)  # Bind to all interfaces

if __name__ == '__main__':
    # Start the server when the script is run
    start_server()
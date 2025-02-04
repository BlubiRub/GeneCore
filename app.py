from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sklearn.cluster import KMeans
import os

# Initialize Flask app
app = Flask(__name__)

# Configure PostgreSQL database (adjust to use Docker's db service)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/cancer_data'  # db is the service name from docker-compose
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Variant table model
class Variant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gene = db.Column(db.String, nullable=False)
    variation = db.Column(db.String, nullable=False)
    variant_class = db.Column(db.Integer, nullable=False)

# Define the PatientData table model
class PatientData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msi = db.Column(db.Float, nullable=False)
    sv = db.Column(db.Float, nullable=False)
    data_type = db.Column(db.Integer, nullable=False)

# Function to initialize the database and import data if necessary
def initialize_database():
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
        if not Variant.query.first():  # Import data only if the database is empty
            import_variant_data('training_variants.csv')
        if not PatientData.query.first():  # Import data into PatientData table if empty
            import_patient_data('patient_data.csv')

# Function to import data into the Variant table
def import_variant_data(csv_file):
    data = pd.read_csv(csv_file)
    for _, row in data.iterrows():
        variant = Variant(
            id=row['ID'],
            gene=row['Gene'],
            variation=row['Variation'],
            variant_class=row['Class']
        )
        db.session.add(variant)
    db.session.commit()

# Function to import data into the PatientData table
def import_patient_data(csv_file):
    data = pd.read_csv(csv_file)
    for _, row in data.iterrows():
        patient_data = PatientData(
            msi=float(row['MSI']),  # Explicitly convert np.float64 to Python float
            sv=float(row['SV']),    # Explicitly convert np.float64 to Python float
            data_type=int(row['Type'])  # Ensure data_type is an integer
        )
        db.session.add(patient_data)
    db.session.commit()

# API endpoint to fetch top genes data
@app.route("/api/top_genes")
def get_top_genes():
    # Query data from the Variant table
    top_gene = (
        db.session.query(Variant.gene, db.func.count(Variant.id).label('ct'))
        .group_by(Variant.gene)
        .having(db.func.count(Variant.id) > 40)
        .all()
    )
    # Convert query results to a list of dictionaries
    top_gene_data = [{"gene": gene, "count": count} for gene, count in top_gene]
    return jsonify(top_gene_data)

# API endpoint to fetch patient data
@app.route("/api/patient_data")
def get_patient_data():
    # Fetch the data from the database
    patient_data = PatientData.query.all()
    # Convert data to a list of dictionaries
    patient_data_json = [{"msi": p.msi, "sv": p.sv, "cluster": p.data_type} for p in patient_data]
    return jsonify(patient_data_json)

# API endpoint to predict cluster
@app.route("/api/predict_cluster", methods=["POST"])
def predict_cluster_api():
    data = request.json
    msi = data.get('msi')
    sv = data.get('sv')

    if msi is None or sv is None:
        return jsonify({"error": "Missing MSI or SV value"}), 400

    # Get the current predefined clusters (data_type) from the database
    patient_data = PatientData.query.all()
    known_data = pd.DataFrame([(p.msi, p.sv, p.data_type) for p in patient_data], columns=['MSI', 'SV', 'Cluster'])

    # Train a KMeans model on the known data
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(known_data[['MSI', 'SV']])

    # Predict the cluster for the user-provided data
    prediction = kmeans.predict([[msi, sv]])[0]
    return jsonify({"predicted_cluster": int(prediction)})

# Route for landing page
@app.route("/")
def landing_page():
    return render_template("landing_page.html")

# Route to show the interactive gene variants plot
@app.route("/show_plot")
def show_plot():
    return render_template("show_plot.html")

# Route to show the interactive clustering plot
@app.route("/clustering")
def clustering():
    return render_template("clustering.html")

# Initialize the database before running the app
if __name__ == "__main__":
    initialize_database()  # Initialize the database and load data
    app.run(host="0.0.0.0", debug=True)
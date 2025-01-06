from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

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

# Function to create the plot
def create_plot():
    # Query data from the Variant table
    top_gene = (
        db.session.query(Variant.gene, db.func.count(Variant.id).label('ct'))
        .group_by(Variant.gene)
        .having(db.func.count(Variant.id) > 40)
        .all()
    )
    # Convert query results to DataFrame
    top_gene_df = pd.DataFrame(top_gene, columns=['Gene', 'ct'])

    # Create plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=top_gene_df,
        x='ct',
        y=top_gene_df['Gene'].str.strip(),
        size=4,
        legend=False,
    )
    plt.xlabel("Frequency")
    plt.ylabel("Gene")
    plt.title("Gene with the Most Variants")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save plot
    plot_path = os.path.join('static', 'plot.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path

@app.route("/")
def landing_page():
    return render_template("landing_page.html")

@app.route("/show_plot")
def show_plot():
    plot_path = create_plot()
    return render_template("show_plot.html", plot_url=plot_path)

@app.route("/clustering")
def clustering():
    # Fetch the data from the database
    patient_data = PatientData.query.all()
    
    # Convert data to DataFrame
    data = pd.DataFrame([(p.msi, p.sv, p.data_type) for p in patient_data], columns=['MSI', 'SV', 'Cluster'])

    # Create a plot of the predefined clusters (grouped by data_type)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=data, x='SV', y='MSI', hue='Cluster', palette='viridis', s=100)
    plt.title('Predefined Clustering of Patients')
    plt.xlabel('SV')  # X-axis is SV
    plt.ylabel('MSI')  # Y-axis is MSI
    plt.grid(True)
    plt.tight_layout()

    # Save the plot
    plot_path = os.path.join('static', 'clustering_plot.png')
    plt.savefig(plot_path)
    plt.close()

    return render_template("clustering.html", plot_url=plot_path)

@app.route("/predict", methods=["GET", "POST"])
def predict_cluster():
    predicted_cluster = None
    msi = None
    sv = None

    if request.method == "POST":
        # Get MSI and SV from the form
        msi = float(request.form['msi'])
        sv = float(request.form['sv'])
        
        # Get the current predefined clusters (data_type) from the database
        patient_data = PatientData.query.all()
        known_data = pd.DataFrame([(p.msi, p.sv, p.data_type) for p in patient_data], columns=['MSI', 'SV', 'Cluster'])

        # Train a KMeans model on the known data
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(known_data[['MSI', 'SV']])

        # Predict the cluster for the user-provided data
        prediction = kmeans.predict([[msi, sv]])[0]
        
        # Map the predicted cluster to the corresponding data_type
        predicted_cluster = prediction

    # Return the results to the template
    return render_template("predict.html", predicted_cluster=predicted_cluster, msi=msi, sv=sv)

# Initialize the database before running the app
if __name__ == "__main__":
    initialize_database()  # Initialize the database and load data
    app.run(debug=True)

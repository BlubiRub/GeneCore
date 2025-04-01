from flask import Flask, render_template, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from sklearn.cluster import KMeans
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Configure PostgreSQL database (adjust to use Docker's db service)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5432/cancer_data'  # Adjust this URI as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set the secret key (for sessions and security)
app.config['SECRET_KEY'] = 'secret_token'

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
    data_type = db.Column(db.Integer, db.ForeignKey('variant_details.id'), nullable=False)

# Define the VariantDetails table model
class VariantDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    resolution = db.Column(db.String, nullable=True)

    # Relationship to PatientData
    patient_data = db.relationship('PatientData', backref=db.backref('variant_details', lazy=True))


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
            msi=float(row['Anzahl Mikrosatelitenmutationen (MSI)']),  # Explicitly convert np.float64 to Python float
            sv=float(row['Anzahl struktureller Variationen(SV)']),    # Explicitly convert np.float64 to Python float
            data_type=int(row['Type'])  # Ensure data_type is an integer
        )
        db.session.add(patient_data)
    db.session.commit()

# Setup Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')

# Add the models to the admin interface
admin.add_view(ModelView(PatientData, db.session))
admin.add_view(ModelView(VariantDetails, db.session))
admin.add_view(ModelView(Variant, db.session))
admin.add_link(MenuLink(name="Back to Home", category="", url="/"))

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

@app.route("/api/patient_data")
def get_patient_data():
    patient_data = PatientData.query.all()
    patient_data_json = [
        {
            "msi": float(p.msi),
            "sv": float(p.sv),
            "cluster_id": int(p.data_type),
            "cluster_name": p.variant_details.name if p.variant_details else "Unknown",
            "treatment_option": p.variant_details.resolution if p.variant_details else "N/A"
        }
        for p in patient_data
    ]
    return jsonify(patient_data_json)


@app.route("/api/predict_cluster", methods=["POST"])
def predict_cluster_api():
    data = request.json
    msi = data.get('msi')
    sv = data.get('sv')

    if msi is None or sv is None:
        return jsonify({"error": "Missing MSI or SV value"}), 400

    # Fetch patient data from DB
    patient_data = PatientData.query.all()
    known_data = pd.DataFrame([
        (float(p.msi), float(p.sv), int(p.data_type))  # Ensure conversion
        for p in patient_data
    ], columns=['MSI', 'SV', 'Cluster'])

    # Train KMeans model
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    known_data['Predicted'] = kmeans.fit_predict(known_data[['MSI', 'SV']])

    # Map KMeans labels to actual clusters
    cluster_mapping = {}
    for kmeans_label in range(2):
        most_common_actual = known_data[known_data['Predicted'] == kmeans_label]['Cluster'].mode()[0]
        cluster_mapping[kmeans_label] = most_common_actual

    # Predict the cluster
    kmeans_cluster = int(kmeans.predict([[msi, sv]])[0])
    predicted_cluster = cluster_mapping[kmeans_cluster]  # Ensure correct mapping

    variant = VariantDetails.query.filter_by(id=int(predicted_cluster)).first()
    cluster_name = variant.name if variant else "Unknown"
    treatment_option = variant.resolution if variant else "N/A"

    return jsonify({
        "predicted_cluster": int(predicted_cluster),
        "predicted_cluster_name": cluster_name,
        "treatment_option": treatment_option
    })


# Initialize the database before running the app
if __name__ == "__main__":
    initialize_database()  # Initialize the database and load data
    app.run(host="0.0.0.0", debug=True)

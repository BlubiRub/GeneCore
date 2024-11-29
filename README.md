# GeneCore

This repository contains a Python web application built with Flask. Follow the steps below to set up the project and run the application.

---

## Prerequisites

Before starting, ensure you have the following installed on your system:

- [Python (3.7 or later)](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- A terminal/command prompt

---

## Setup Instructions

1. **Clone the Repository**  
   Open a terminal and clone this repository using:
   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the Project Directory**  
   Move into the project's root directory::
   ```bash
   cd <repository-name>
   ```

3. **Set Up a Virtual Environment**  
   Create a virtual environment in the project folder:
   ```bash
   python -m venv .venv
   ```
   This creates a virtual environment named .venv.

4. **Activate the Virtual Environment**  
   - On Windows:
   ```bash
   .venv\Scripts\activate
   ```
   - Mac/Linux:
   ```bash
   source .venv/bin/activate
   ```
   When activated, you’ll see the virtual environment’s name (e.g., .venv) in your terminal prompt.

5. **Install Required Dependencies**  
   Install the required Python packages from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
1. Ensure the Virtual Environment is Active\
   If not already active, activate it as described in step 4.

2. Run the Flask App
   Use the following command to start the application:
   ```bash
   python app.py
   ```

3. Access the Application
   Open your web browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

# GeneCore

This repository contains a Python web application built with Flask, now fully containerized using Docker. Follow the steps below to set up the project and run the application.

---

## Prerequisites

Before starting, ensure you have the following installed on your system:

- [Docker](https://www.docker.com/get-started)
- [Git](https://git-scm.com/)
- A terminal/command prompt

---

## Setup Instructions (Dockerized Version)

1. **Clone the Repository**\
   Open a terminal and clone this repository using:

   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the Project Directory**\
   Move into the project's root directory:

   ```bash
   cd <repository-name>
   ```

3. **Build the Docker Image**\
   Run the following command to build the Docker image:

   ```bash
   docker build -t genecore .
   ```

4. **Run the Application in a Docker Container**\
   Execute the following command to start the container:

   ```bash
   docker run -p 5000:5000 genecore
   ```

5. **Access the Application**\
   Open your web browser and go to:

   ```
   http://127.0.0.1:5000/
   ```

---

## Stopping the Docker Container

To stop the running container, find the container ID using:

```bash
docker ps
```

Then stop it with:

```bash
docker stop <container-id>
```


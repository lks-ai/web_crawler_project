# Web Crawler Project

This project is an autonomous real-time web crawler built with Python. It indexes and synchronizes web content for target websites, storing data in a local SQLite database with vector embeddings for efficient retrieval.

## Features

- **JavaScript Rendering:** Uses Playwright to render JavaScript content, ensuring all visible content is indexed.
- **Efficient Synchronization:** Checks HTTP headers (`Last-Modified` and `ETag`) before fetching pages to avoid unnecessary downloads.
- **SQLite Database:** Stores data locally with a relational and atomic architecture using UUID v4.
- **Vector Embeddings:** Utilizes OpenAI's Ada embeddings for efficient storage and retrieval using vectors and cosine similarity.
- **Multithreaded Crawler:** Employs asynchronous programming for efficient crawling of large websites.
- **Content Chunking:** Splits content into natural chunks of approximately 1200 tokens.
- **FastAPI Server:** Provides `/recall` and `/storage` endpoints for interaction and data management.
- **Dockerized Deployment:** Easily deployable using Docker and Docker Compose for consistent environments.

## Project Structure

```
web_crawler_project/
├── api/
│   └── main.py
├── crawler/
│   └── crawler.py
├── database/
│   ├── models.py
│   └── setup.sql
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
├── setup_database.py
├── setup.sh
├── README.md
└── .gitignore
```

## Setup

### **1. Clone the Repository**

First, clone the repository to your local machine:

```bash
git clone https://github.com/lks-ai/web_crawler_project.git
cd web_crawler_project
```

### **2. Environment Variables**

Create a `.env` file in the root directory to store your environment variables securely:

```bash
touch .env
```

Add the following to the `.env` file:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

**Note:** Replace `your_actual_openai_api_key_here` with your actual OpenAI API key.

### **3. Docker Setup**

#### **a. Prerequisites**

Ensure that Docker and Docker Compose are installed on your machine. If not, follow the [official Docker installation guide](https://docs.docker.com/get-docker/) and the [Docker Compose installation guide](https://docs.docker.com/compose/install/).

#### **b. Build and Run Containers**

Use Docker Compose to build and start the services:

```bash
docker-compose up --build
```

This command will:

- **Build** the Docker images based on the provided `Dockerfile`.
- **Start** two services:
  - **API Service:** Runs the FastAPI server on port `8000`.
  - **Crawler Service:** Executes the web crawler script.

#### **c. Accessing the Application**

- **FastAPI Server:** Accessible at `http://localhost:8000`
  - **Recall Endpoint:** `http://localhost:8000/recall`
  - **Storage Endpoint:** `http://localhost:8000/storage`
  
- **Swagger Documentation:** Available at `http://localhost:8000/docs`

#### **d. Stopping the Services**

To stop the running containers, press `Ctrl + C` in the terminal where Docker Compose is running. To remove the containers, networks, and volumes, run:

```bash
docker-compose down
```

## Usage

### **1. Running the Crawler**

The crawler is automatically started as part of the Docker Compose services. It will begin indexing the target websites defined in the `crawler/crawler.py` script.

### **2. Interacting with the API**

You can interact with the API endpoints using tools like `curl`, `Postman`, or directly via the Swagger UI.

- **Recall Endpoint:**

  **Request:**
  
  ```bash
  curl -X POST "http://localhost:8000/recall" -H "Content-Type: application/json" -d '{"query": "Your query here"}'
  ```

  **Response:**
  
  ```json
  {
    "results": [
      {
        "score": 0.95,
        "content": "Relevant content snippet..."
      },
      ...
    ]
  }
  ```

- **Storage Endpoint:**

  **Request:**
  
  ```bash
  curl -X POST "http://localhost:8000/storage" -H "Content-Type: application/json" -d '{"page_id": "page-uuid", "content": "New content to store."}'
  ```

  **Response:**
  
  ```json
  {
    "success": true
  }
  ```

## Deployment on a Remote Server with Docker

Follow these steps to deploy the project on a remote server using Docker.

### **1. Prepare the Remote Server**

- **Provision a Server:**
  
  Choose a cloud provider (e.g., AWS, DigitalOcean, Google Cloud) and provision a server instance with sufficient resources.

- **Install Docker and Docker Compose:**

  Connect to your server via SSH and install Docker:

  ```bash
  # Update package list
  sudo apt-get update

  # Install prerequisites
  sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

  # Add Docker’s official GPG key
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

  # Set up the stable repository
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  # Install Docker Engine
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io

  # Install Docker Compose
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose

  # Verify installations
  docker --version
  docker-compose --version
  ```

### **2. Clone the Repository on the Server**

SSH into your server and clone the repository:

```bash
git clone https://github.com/your-username/web_crawler_project.git
cd web_crawler_project
```

### **3. Configure Environment Variables**

Create and populate the `.env` file on the server:

```bash
touch .env
```

Edit the `.env` file using a text editor like `nano`:

```bash
nano .env
```

Add the following content:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

**Save and exit** the editor (`Ctrl + X`, then `Y`, and `Enter` in `nano`).

### **4. Build and Start Docker Containers**

Run Docker Compose to build and start the services:

```bash
docker-compose up --build -d
```

- The `-d` flag runs the containers in detached mode.

### **5. Verify the Deployment**

- **Check Running Containers:**

  ```bash
  docker-compose ps
  ```

  You should see both `web_crawler_api` and `web_crawler_crawler` services running.

- **Access the API:**

  Open your browser and navigate to `http://your-server-ip:8000/docs` to access the Swagger UI.

### **6. Manage the Services**

- **View Logs:**

  ```bash
  docker-compose logs -f
  ```

- **Stop the Services:**

  ```bash
  docker-compose down
  ```

- **Restart the Services:**

  ```bash
  docker-compose restart
  ```

### **7. Secure the Deployment (Optional but Recommended)**

- **Set Up a Reverse Proxy:**

  To serve the FastAPI application over standard HTTP/HTTPS ports and enable SSL, consider setting up a reverse proxy using Nginx or Traefik.

- **Firewall Configuration:**

  Ensure that only necessary ports are open. For example, allow traffic on port `8000` or the port used by your reverse proxy.

- **Environment Variable Security:**

  Ensure that the `.env` file is secured and not exposed publicly. Avoid committing it to version control.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

MIT License

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Playwright](https://playwright.dev/)
- [Docker](https://www.docker.com/)
- [OpenAI](https://openai.com/)




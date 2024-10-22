# Web Crawler Project

This project is an autonomous real-time web crawler built with Python. It indexes and synchronizes web content for target websites, storing data in a local SQLite database with vector embeddings for efficient retrieval.

## Features

- Renders JavaScript content using Playwright.
- Checks HTTP headers to avoid unnecessary page fetches.
- Stores data in SQLite with vector embeddings using OpenAI Ada embeddings.
- Multithreaded crawler for efficient indexing.
- FastAPI server with  and  endpoints.
- Relational and atomic database architecture using UUID v4.

## Setup

Run the setup script to initialize the project.

```bash
./setup.sh
```

## Usage

Start the crawler and the API server.

```bash
python crawler/crawler.py
python api/main.py
```

## License

MIT License

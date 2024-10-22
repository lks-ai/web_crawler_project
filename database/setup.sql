-- Enable UUID extension if needed
-- SQLite does not support UUID natively, store as TEXT

CREATE TABLE clients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    website_url TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sites (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    start_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP,
    last_update TIMESTAMP
);

CREATE TABLE client_sites (
    client_id TEXT,
    site_id TEXT,
    PRIMARY KEY (client_id, site_id),
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (site_id) REFERENCES sites(id)
);

CREATE TABLE pages (
    id TEXT PRIMARY KEY,
    site_id TEXT,
    content_hash TEXT,
    title TEXT,
    metadata JSON,
    last_checked TIMESTAMP,
    last_update TIMESTAMP,
    avg_update_delta INTEGER,
    FOREIGN KEY (site_id) REFERENCES sites(id)
);

CREATE TABLE content_chunks (
    id TEXT PRIMARY KEY,
    page_id TEXT,
    content TEXT,
    embedding BLOB,
    FOREIGN KEY (page_id) REFERENCES pages(id)
);

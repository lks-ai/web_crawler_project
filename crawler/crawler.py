import asyncio
import hashlib
import uuid
import json
import logging
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from aiohttp import ClientSession
from playwright.async_api import async_playwright
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from database.models import Base, Client, Site, ClientSite, Page, ContentChunk

import openai
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./database/web_crawler.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Constants
MAX_WORKERS = 10
CHUNK_SIZE = 1200  # tokens
EMBEDDING_MODEL = "text-embedding-ada-002"

# Utility functions
def generate_uuid() -> str:
    return str(uuid.uuid4())

def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

async def get_page_content(url: str, session: ClientSession, playwright) -> Optional[str]:
    try:
        async with playwright.chromium.launch(headless=True) as browser:
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            content = await page.content()
            await page.close()
            await context.close()
            return content
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

async def fetch_head(url: str, session: ClientSession) -> Optional[dict]:
    try:
        async with session.head(url, timeout=10) as response:
            headers = response.headers
            return headers
    except Exception as e:
        logger.error(f"HEAD request failed for {url}: {e}")
        return None

async def embed_text(text: str) -> List[float]:
    try:
        response = openai.Embedding.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        embedding = response['data'][0]['embedding']
        return embedding
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        return []

async def process_page(url: str, session: ClientSession, playwright, db_session: AsyncSession):
    logger.info(f"Processing URL: {url}")
    headers = await fetch_head(url, session)
    if headers is None:
        return

    last_modified = headers.get('Last-Modified')
    etag = headers.get('ETag')

    # Fetch or create page entry
    result = await db_session.execute(select(Page).where(Page.url == url))
    page = result.scalar_one_or_none()

    if page:
        # Check if the page has been updated
        if last_modified and page.last_update:
            last_mod_datetime = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
            if last_mod_datetime <= page.last_update:
                logger.info(f"No update for {url}")
                return

    # Fetch page content
    content = await get_page_content(url, session, playwright)
    if content is None:
        return

    content_hash = compute_hash(content)

    if page and page.content_hash == content_hash:
        logger.info(f"No content change for {url}")
        return

    # Update or create page entry
    if not page:
        page = Page(
            id=generate_uuid(),
            url=url,
            content_hash=content_hash,
            title="",  # Extract title as needed
            metadata={},
            last_checked=datetime.utcnow(),
            last_update=datetime.utcnow(),
            avg_update_delta=0
        )
        db_session.add(page)
    else:
        page.content_hash = content_hash
        page.last_checked = datetime.utcnow()
        page.last_update = datetime.utcnow()

    await db_session.commit()

    # Chunk content
    chunks = chunk_content(content, CHUNK_SIZE)

    for chunk in chunks:
        embedding = await embed_text(chunk)
        if not embedding:
            continue
        content_chunk = ContentChunk(
            id=generate_uuid(),
            page_id=page.id,
            content=chunk,
            embedding=json.dumps(embedding)  # Store as JSON string
        )
        db_session.add(content_chunk)

    try:
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        logger.error(f"Integrity error when adding chunks for {url}")

def chunk_content(content: str, max_tokens: int) -> List[str]:
    # Simple chunking based on paragraphs
    paragraphs = content.split('\n\n')
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for para in paragraphs:
        tokens = len(para.split())
        if current_tokens + tokens > max_tokens:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
                current_tokens = 0
        current_chunk += para + "\n\n"
        current_tokens += tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

async def crawl_site(site_url: str):
    async with async_playwright() as playwright:
        async with aiohttp.ClientSession() as session:
            db = async_session()
            await db.begin()
            try:
                # Add site to database if not exists
                result = await db.execute(select(Site).where(Site.url == site_url))
                site = result.scalar_one_or_none()
                if not site:
                    site = Site(
                        id=generate_uuid(),
                        url=site_url,
                        start_url=site_url,
                        created_at=datetime.utcnow(),
                        last_checked=datetime.utcnow(),
                        last_update=datetime.utcnow()
                    )
                    db.add(site)
                    await db.commit()

                # For simplicity, crawl only the start_url
                await process_page(site_url, session, playwright, db)

            except Exception as e:
                logger.error(f"Error crawling site {site_url}: {e}")
                await db.rollback()
            finally:
                await db.close()

async def main():
    # Example usage
    sites_to_crawl = [
        "https://example.com"
    ]

    tasks = []
    for site in sites_to_crawl:
        tasks.append(crawl_site(site))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

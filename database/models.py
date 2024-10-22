import uuid
from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP, JSON, BLOB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    website_url = Column(String, nullable=False)
    metadata = Column(JSON)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')

    sites = relationship('ClientSite', back_populates='client')

class Site(Base):
    __tablename__ = 'sites'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String, nullable=False)
    start_url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP')
    last_checked = Column(TIMESTAMP)
    last_update = Column(TIMESTAMP)

    client_sites = relationship('ClientSite', back_populates='site')
    pages = relationship('Page', back_populates='site')

class ClientSite(Base):
    __tablename__ = 'client_sites'
    client_id = Column(String, ForeignKey('clients.id'), primary_key=True)
    site_id = Column(String, ForeignKey('sites.id'), primary_key=True)

    client = relationship('Client', back_populates='sites')
    site = relationship('Site', back_populates='client_sites')

class Page(Base):
    __tablename__ = 'pages'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(String, ForeignKey('sites.id'))
    content_hash = Column(String)
    title = Column(String)
    metadata = Column(JSON)
    last_checked = Column(TIMESTAMP)
    last_update = Column(TIMESTAMP)
    avg_update_delta = Column(Integer)

    site = relationship('Site', back_populates='pages')
    content_chunks = relationship('ContentChunk', back_populates='page')

class ContentChunk(Base):
    __tablename__ = 'content_chunks'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    page_id = Column(String, ForeignKey('pages.id'))
    content = Column(Text)
    embedding = Column(BLOB)  # Store as JSON string

    page = relationship('Page', back_populates='content_chunks')

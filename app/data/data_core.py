import datetime
from .. import db
from ..db_class.db import *
from app.db_class.db import Data
import uuid

def generate_sample_data(user_id=None):
    """Generate 30 sample data entries for testing pagination"""
    
    sample_texts = [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning algorithms improve with more data",
        "Cloud computing has revolutionized software deployment",
        "Pagination helps manage large datasets efficiently",
        "Database optimization requires careful indexing",
        "REST APIs follow standard HTTP protocols",
        "Authentication and authorization are security essentials",
        "WebSockets enable real-time communication",
        "Microservices architecture improves scalability",
        "Docker containers standardize application deployment",
        "Kubernetes orchestrates containerized applications",
        "DevOps practices bridge development and operations",
        "Continuous integration enables faster releases",
        "Load balancing distributes traffic across servers",
        "Caching strategies improve application performance",
    ]
    
    for i in range(30):
        data_entry = Data(
            name=f"Data Sample {i + 1}",
            data=f"Raw data content for sample {i + 1}",
            content=sample_texts[i % len(sample_texts)],
            user_id=user_id,
            created_at=datetime.datetime.now(tz=datetime.timezone.utc),
            updated_at=datetime.datetime.now(tz=datetime.timezone.utc),
            uuid=str(uuid.uuid4()),
        )
        db.session.add(data_entry)
    
    db.session.commit()
    return True



def get_data_page(page):
    """Return all data by page"""
    return Data.query.paginate(page=page, per_page=5, max_per_page=5)



def get_total_data_count():
    """Return total count of data entries"""
    return Data.query.count()




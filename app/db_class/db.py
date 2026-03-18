from .. import db
import uuid    
import datetime

class ComponentExample(db.Model):
    """
    Entity to store component examples with code, usage, and documentation
    Used to showcase different components and their implementations
    """
    __tablename__ = 'component_examples'
    
    # Primary Keys & Identifiers
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    
    # Basic Information
    title = db.Column(db.String(128), nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, index=True)
    
    # Image - Store only the filename, not the binary data
    image_filename = db.Column(db.String(255), nullable=True)
    
    # Code & Implementation
    vue_code = db.Column(db.Text, nullable=False)
    html_code = db.Column(db.Text)
    css_code = db.Column(db.Text)
    javascript_code = db.Column(db.Text)
    
    # Documentation
    usage_guide = db.Column(db.Text)
    features = db.Column(db.Text)
    requirements = db.Column(db.Text)
    
    # Metadata
    difficulty = db.Column(db.String(20), default="beginner")
    tags = db.Column(db.String(255))
    version = db.Column(db.String(20), default="1.0.0")
    
    # Status & Visibility
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_featured = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, nullable=True, index=True)
    
    def __repr__(self):
        return f'<ComponentExample {self.title} v{self.version}>'
    
    def get_image_url(self):
        """Get the URL path to the component image"""
        if self.image_filename:
            return f'/static/images/components/{self.image_filename}'
        return '/static/images/components/placeholder.png'
    def increment_views(self):
        """Increment the views count for the component"""
        self.views_count += 1
        self.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)
        db.session.commit()
    def has_image(self):
        """Check if component has an image"""
        return self.image_filename is not None
    
    def to_json(self, include_code=True):
        """
        Convert the ComponentExample instance to a JSON-serializable dictionary.
        Args:
            include_code (bool): Whether to include full code snippets
        Returns:
            dict: JSON-serializable representation
        """
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'tags': self.tags.split(',') if self.tags else [],
            'version': self.version,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'views_count': self.views_count,
            'image_url': self.get_image_url(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_code:
            data.update({
                'vue_code': self.vue_code,
                'html_code': self.html_code,
                'css_code': self.css_code,
                'javascript_code': self.javascript_code,
                'usage_guide': self.usage_guide,
                'features': self.features,
                'requirements': self.requirements,
            })
        return data
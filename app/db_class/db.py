from .. import db
import uuid    
import datetime
from .. import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import  UserMixin, AnonymousUserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, index=True)
    password_hash = db.Column(db.String(128))
    api_key = db.Column(db.String(60), index=True)
    
    def is_admin(self):
        r = Role.query.get(self.role_id)
        if r.admin:
            return True
        return False

    def read_only(self):
        r = Role.query.get(self.role_id)
        if r.read_only:
            return True
        return False
    def role(self):
        # return the name of the role associated with the user
        return Role.query.get(self.role_id).name
    def username(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def password(self):
        raise AttributeError('`password` is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_json(self):
        return {
            "id": self.id, 
            "first_name": self.first_name, 
            "last_name": self.last_name, 
            "email": self.email, 
            "org_id": self.org_id, 
            "role_id": self.role_id
        }

class AnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False

    def read_only(self):
        return True
    
login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String, nullable=True)
    admin = db.Column(db.Boolean, default=False)
    read_only = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            "id": self.id, 
            "name": self.name,
            "description": self.description,
            "admin": self.admin,
            "read_only": self.read_only
        }
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
    

class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=True)
    data = db.Column(db.Text, nullable=True)
    uuid = db.Column(db.String(36), unique=True, nullable=True, default=lambda: str(uuid.uuid4()), index=True)
    created_at = db.Column(db.DateTime, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    content = db.Column(db.Text, nullable=True)

    # Relationship with User
    user = db.relationship('User', backref=db.backref('data', lazy=True , cascade="all, delete-orphan"))

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'data': self.data,
            'uuid': self.uuid,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
   
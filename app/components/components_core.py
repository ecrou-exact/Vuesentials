from sqlalchemy import or_

from .. import db
from ..db_class.db import ComponentExample
import datetime
import os
import secrets
from werkzeug.utils import secure_filename
from PIL import Image
import io

# Configuration
UPLOAD_FOLDER = 'app/static/images/components'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
IMAGE_THUMBNAIL_SIZE = (500, 400)  # Width x Height


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size(file):
    """Get file size in bytes"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size


def validate_image(file):
    """Validate image file"""
    errors = []
    
    # Check if file exists
    if not file or file.filename == '':
        return True, []  # Image est optionnelle
    
    # Check file extension
    if not allowed_file(file.filename):
        errors.append('Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WebP')
        return False, errors
    
    # Check file size
    if get_file_size(file) > MAX_FILE_SIZE:
        errors.append(f'File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit')
        return False, errors
    
    # Try to open as image
    try:
        file.seek(0)
        img = Image.open(file)
        img.verify()
        file.seek(0)
    except Exception as e:
        errors.append(f'Invalid image file: {str(e)}')
        return False, errors
    
    return True, errors


def save_component_image(file, component_id):
    """
    Save component image with thumbnail generation
    Returns: (filename, error_message) or (None, error_message)
    """
    
    # Validate image
    is_valid, errors = validate_image(file)
    if not is_valid:
        return None, " | ".join(errors)
    
    # If no file, return None (image is optional)
    if not file or file.filename == '':
        return None, None
    
    try:
        # Create upload folder if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f'component_{component_id}_{secrets.token_hex(8)}.{file_ext}'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Open image and resize/optimize
        file.seek(0)
        img = Image.open(file)
        
        # Convert RGBA to RGB if needed (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize to thumbnail size (maintain aspect ratio)
        img.thumbnail(IMAGE_THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        
        # Save image
        img.save(filepath, quality=85, optimize=True)
        
        return filename, None
    
    except Exception as e:
        return None, f"Error saving image: {str(e)}"


def CreateComponent(data):
    """Create a new component example in the database"""
    try:
        # Get image file from data
        image_file = data.get('image')
        image_filename = None
        image_error = None
        
        # Create component first without image to get the ID
        new_component = ComponentExample(
            title=data.get('title'),
            description=data.get('description', ''),
            category=data.get('category'),
            vue_code=data.get('vue_code'),
            html_code=data.get('html_code', ''),
            css_code=data.get('css_code', ''),
            javascript_code=data.get('javascript_code', ''),
            usage_guide=data.get('usage_guide', ''),
            features=data.get('features', ''),
            requirements=data.get('requirements', ''),
            difficulty=data.get('difficulty', 'beginner'),
            tags=data.get('tags', ''),
            version=data.get('version', '1.0.0'),
            is_active=data.get('is_active', True),
            is_featured=data.get('is_featured', False),
            views_count=0,
            created_at=datetime.datetime.now(tz=datetime.timezone.utc),
            updated_at=datetime.datetime.now(tz=datetime.timezone.utc),
        )
        
        # Add to session to get ID
        db.session.add(new_component)
        db.session.flush()  # Flush to get the ID without committing
        
        # Save image if provided
        if image_file and image_file.filename != '':
            image_filename, image_error = save_component_image(image_file, new_component.id)
            
            if image_error:
                db.session.rollback()
                return None, f"Image error: {image_error}", False
            
            # Update component with image filename
            if image_filename:
                new_component.image_filename = image_filename
        
        # Commit all changes
        db.session.commit()
        
        return new_component, "Component created successfully.", True
    
    except Exception as e:
        db.session.rollback()
        print(f"Error creating component: {str(e)}")
        return None, f"Error creating component: {str(e)}", False
    
def get_component_by_id(component_id):
    """Get component example by ID"""
    return ComponentExample.query.get(component_id)

def get_related_components(category, exclude_id, limit=4):
    """Get related components by category, excluding the current one"""
    return ComponentExample.query.filter(
        ComponentExample.category == category,
        ComponentExample.id != exclude_id
    ).order_by(ComponentExample.created_at.desc()).limit(limit).all()


def get_component_by_id(component_id):
    """
    Get a single component by ID
    
    Args:
        component_id (int): Component ID
        
    Returns:
        ComponentExample or None: Component object if found
    """
    try:
        return ComponentExample.query.filter_by(
            id=component_id, 
            is_active=True
        ).first()
    except Exception as e:
        print(f"Error getting component by ID: {str(e)}")
        return None


def get_component_by_uuid(uuid):
    """
    Get a single component by UUID
    
    Args:
        uuid (str): Component UUID
        
    Returns:
        ComponentExample or None: Component object if found
    """
    try:
        return ComponentExample.query.filter_by(
            uuid=uuid,
            is_active=True
        ).first()
    except Exception as e:
        print(f"Error getting component by UUID: {str(e)}")
        return None


def get_related_components(category, exclude_id=None, limit=4):
    """
    Get related components in the same category
    
    Args:
        category (str): Component category
        exclude_id (int): Component ID to exclude
        limit (int): Maximum number of components to return
        
    Returns:
        list: List of ComponentExample objects
    """
    try:
        query = ComponentExample.query.filter_by(
            category=category,
            is_active=True
        )
        
        if exclude_id:
            query = query.filter(ComponentExample.id != exclude_id)
        
        return query.limit(limit).all()
    except Exception as e:
        print(f"Error getting related components: {str(e)}")
        return []


def get_all_categories():
    """
    Get all available component categories
    
    Returns:
        list: List of dicts with category info
    """
    try:
        categories = db.session.query(
            ComponentExample.category
        ).filter_by(is_active=True).distinct().all()
        
        categories_data = [
            {'id': i, 'name': cat[0]}
            for i, cat in enumerate(categories)
        ]
        
        return sorted(categories_data, key=lambda x: x['name'])
    except Exception as e:
        print(f"Error getting categories: {str(e)}")
        return []


def get_components_list(
    page=1,
    per_page=12,
    search_query='',
    search_field='all',
    sort_by='newest',
    category_filter='',
    difficulty_filter=''
):
    """
    Get paginated list of components with filters
    
    Args:
        page (int): Page number
        per_page (int): Items per page
        search_query (str): Search text
        search_field (str): 'all', 'title', 'description', 'tags'
        sort_by (str): 'newest', 'oldest', 'most_viewed', 'most_favorites'
        category_filter (str): Filter by category
        difficulty_filter (str): Filter by difficulty
        
    Returns:
        tuple: (paginated_results, total_count, total_pages)
    """
    try:
        # Start with active components
        query = ComponentExample.query.filter_by(is_active=True)
        
        # Apply search filter
        if search_query:
            search_query = search_query.strip()
            
            if search_field == 'title':
                query = query.filter(
                    ComponentExample.title.ilike(f'%{search_query}%')
                )
            elif search_field == 'description':
                query = query.filter(
                    ComponentExample.description.ilike(f'%{search_query}%')
                )
            elif search_field == 'tags':
                query = query.filter(
                    ComponentExample.tags.ilike(f'%{search_query}%')
                )
            else:  # 'all'
                query = query.filter(
                    or_(
                        ComponentExample.title.ilike(f'%{search_query}%'),
                        ComponentExample.description.ilike(f'%{search_query}%'),
                        ComponentExample.tags.ilike(f'%{search_query}%')
                    )
                )
        
        # Apply category filter
        if category_filter:
            category_filter = category_filter.strip()
            query = query.filter(
                ComponentExample.category.ilike(f'%{category_filter}%')
            )
        
        # Apply difficulty filter
        if difficulty_filter:
            difficulty_filter = difficulty_filter.strip().lower()
            query = query.filter(
                ComponentExample.difficulty == difficulty_filter
            )
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        if sort_by == 'oldest':
            query = query.order_by(ComponentExample.created_at.asc())
        elif sort_by == 'most_viewed':
            query = query.order_by(ComponentExample.views_count.desc())
        elif sort_by == 'most_favorites':
            query = query.order_by(ComponentExample.views_count.desc())
        else:  # 'newest' (default)
            query = query.order_by(ComponentExample.created_at.desc())
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated, total_count, paginated.pages
    
    except Exception as e:
        print(f"Error getting components list: {str(e)}")
        return None, 0, 0


def increment_views(component_id):
    """
    Increment view count for a component
    
    Args:
        component_id (int): Component ID
        
    Returns:
        bool: True if successful
    """
    try:
        component = ComponentExample.query.get(component_id)
        if component:
            component.views_count += 1
            component.updated_at = datetime.datetime.now(
                tz=datetime.timezone.utc
            )
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error incrementing views: {str(e)}")
        return False


def component_to_dict(component, include_full_code=True):
    """
    Convert component to dictionary
    
    Args:
        component (ComponentExample): Component object
        include_full_code (bool): Include full code or just preview
        
    Returns:
        dict: Component data dictionary
    """
    try:
        data = {
            'id': component.id,
            'uuid': component.uuid,
            'title': component.title,
            'description': component.description,
            'category': component.category,
            'difficulty': component.difficulty,
            'tags': component.tags or '',
            'version': component.version,
            'views_count': component.views_count,
            'is_featured': component.is_featured,
            'is_active': component.is_active,
            'created_at': component.created_at.isoformat() if component.created_at else None,
            'get_image_url': component.get_image_url(),
        }
        
        if include_full_code:
            data.update({
                'vue_code': component.vue_code,
                'html_code': component.html_code,
                'css_code': component.css_code,
                'javascript_code': component.javascript_code,
                'usage_guide': component.usage_guide,
                'features': component.features,
                'requirements': component.requirements,
            })
        else:
            # Just preview for list view
            data['vue_code'] = component.vue_code[:100] if component.vue_code else ''
        
        data['favorites'] = 0  # Placeholder for favorites tracking
        
        return data
    except Exception as e:
        print(f"Error converting component to dict: {str(e)}")
        return {}


def get_featured_components(limit=6):
    """
    Get featured components for homepage
    
    Args:
        limit (int): Maximum number of components
        
    Returns:
        list: List of featured ComponentExample objects
    """
    try:
        return ComponentExample.query.filter_by(
            is_active=True,
            is_featured=True
        ).order_by(ComponentExample.created_at.desc()).limit(limit).all()
    except Exception as e:
        print(f"Error getting featured components: {str(e)}")
        return []


def get_recent_components(limit=8):
    """
    Get recently created components
    
    Args:
        limit (int): Maximum number of components
        
    Returns:
        list: List of recent ComponentExample objects
    """
    try:
        return ComponentExample.query.filter_by(is_active=True)\
            .order_by(ComponentExample.created_at.desc())\
            .limit(limit).all()
    except Exception as e:
        print(f"Error getting recent components: {str(e)}")
        return []


def get_most_viewed_components(limit=8):
    """
    Get most viewed components
    
    Args:
        limit (int): Maximum number of components
        
    Returns:
        list: List of most viewed ComponentExample objects
    """
    try:
        return ComponentExample.query.filter_by(is_active=True)\
            .order_by(ComponentExample.views_count.desc())\
            .limit(limit).all()
    except Exception as e:
        print(f"Error getting most viewed components: {str(e)}")
        return []


def search_components(search_query, limit=10):
    """
    Simple component search
    
    Args:
        search_query (str): Search text
        limit (int): Maximum results
        
    Returns:
        list: List of matching ComponentExample objects
    """
    try:
        if not search_query or not search_query.strip():
            return []
        
        search_query = search_query.strip()
        return ComponentExample.query.filter_by(is_active=True).filter(
            or_(
                ComponentExample.title.ilike(f'%{search_query}%'),
                ComponentExample.description.ilike(f'%{search_query}%'),
                ComponentExample.tags.ilike(f'%{search_query}%')
            )
        ).limit(limit).all()
    except Exception as e:
        print(f"Error searching components: {str(e)}")
        return []


def get_components_by_category(category, limit=None):
    """
    Get all components in a category
    
    Args:
        category (str): Category name
        limit (int): Optional limit
        
    Returns:
        list: List of ComponentExample objects
    """
    try:
        query = ComponentExample.query.filter_by(
            category=category,
            is_active=True
        ).order_by(ComponentExample.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    except Exception as e:
        print(f"Error getting components by category: {str(e)}")
        return []


def get_components_by_difficulty(difficulty, limit=None):
    """
    Get all components by difficulty level
    
    Args:
        difficulty (str): Difficulty level
        limit (int): Optional limit
        
    Returns:
        list: List of ComponentExample objects
    """
    try:
        query = ComponentExample.query.filter_by(
            difficulty=difficulty.lower(),
            is_active=True
        ).order_by(ComponentExample.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    except Exception as e:
        print(f"Error getting components by difficulty: {str(e)}")
        return []
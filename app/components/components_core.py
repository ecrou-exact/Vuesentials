from flask import current_app, json
from sqlalchemy import or_
from .. import db
from ..db_class.db import ComponentExample
import datetime
import os
import secrets
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
    
    if not file or file.filename == '':
        return True, []  

    if not allowed_file(file.filename):
        errors.append('Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WebP')
        return False, errors
    

    if get_file_size(file) > MAX_FILE_SIZE:
        errors.append(f'File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit')
        return False, errors
    
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
    
    is_valid, errors = validate_image(file)
    if not is_valid:
        return None, " | ".join(errors)
    
    if not file or file.filename == '':
        return None, None
    
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f'component_{component_id}_{secrets.token_hex(8)}.{file_ext}'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        

        file.seek(0)
        img = Image.open(file)
        

        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        

        img.thumbnail(IMAGE_THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        

        img.save(filepath, quality=85, optimize=True)
        
        return filename, None
    
    except Exception as e:
        return None, f"Error saving image: {str(e)}"

def UpdateComponent(form_dict):
    try:
        import os
        from flask import current_app
        import datetime
        
        component_id = form_dict.get('id')
        
        if not component_id:
            return None, 'Component ID not provided', False
        
        component = ComponentExample.query.get(component_id)
        
        if not component:
            return None, f'Component with ID {component_id} not found', False
        
        component.title = form_dict.get('title', component.title)
        component.category = form_dict.get('category', component.category)
        component.description = form_dict.get('description', component.description)
        component.difficulty = form_dict.get('difficulty', component.difficulty)
        component.version = form_dict.get('version', component.version)
        component.tags = form_dict.get('tags', component.tags)
        
        component.vue_code = form_dict.get('vue_code', component.vue_code)
        component.html_code = form_dict.get('html_code', component.html_code)
        component.css_code = form_dict.get('css_code', component.css_code)
        component.javascript_code = form_dict.get('javascript_code', component.javascript_code)
        
        component.usage_guide = form_dict.get('usage_guide', component.usage_guide)
        component.features = form_dict.get('features', component.features)
        component.requirements = form_dict.get('requirements', component.requirements)
        
        component.is_featured = form_dict.get('is_featured', component.is_featured)
        component.is_active = form_dict.get('is_active', component.is_active)
        
        component.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)
        
        image_file = form_dict.get('image')
        
        if image_file and hasattr(image_file, 'filename') and image_file.filename:
            old_image = component.image_filename
            
            result = save_component_image(image_file, component_id)
            filename, error = result
            
            if filename:
                component.image_filename = filename
                
                if old_image:
                    try:
                        old_path = os.path.join(
                            current_app.config.get('UPLOAD_FOLDER', 'app/static/images/components'),
                            old_image
                        )
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception as e:
                        print(f"Error deleting old image: {str(e)}")
            else:
                return None, error or 'Image upload failed', False
        
        db.session.commit()
        
        return component, f'Component "{component.title}" updated successfully!', True
    
    except Exception as e:
        db.session.rollback()
        print(f"Error updating component: {str(e)}")
        return None, f'Error updating component: {str(e)}', False

def CreateComponent(data):
    """Create a new component example in the database"""
    try:

        image_file = data.get('image')
        image_filename = None
        image_error = None
        

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
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        

        db.session.add(new_component)
        db.session.flush()  

        if image_file and image_file.filename != '':
            image_filename, image_error = save_component_image(image_file, new_component.id)
            
            if image_error:
                db.session.rollback()
                return None, f"Image error: {image_error}", False
            
 
            if image_filename:
                new_component.image_filename = image_filename
        
      
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

        query = ComponentExample.query.filter_by(is_active=True)

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
        

        if category_filter:
            category_filter = category_filter.strip()
            query = query.filter(
                ComponentExample.category.ilike(f'%{category_filter}%')
            )

        if difficulty_filter:
            difficulty_filter = difficulty_filter.strip().lower()
            query = query.filter(
                ComponentExample.difficulty == difficulty_filter
            )
        
        total_count = query.count()
        

        if sort_by == 'oldest':
            query = query.order_by(ComponentExample.created_at.asc())
        elif sort_by == 'most_viewed':
            query = query.order_by(ComponentExample.views_count.desc())
        elif sort_by == 'most_favorites':
            query = query.order_by(ComponentExample.views_count.desc())
        else:  
            query = query.order_by(ComponentExample.created_at.desc())
        

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated, total_count, paginated.pages
    
    except Exception as e:
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
            data['vue_code'] = component.vue_code[:100] if component.vue_code else ''
        return data
    except Exception as e:
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
        return []

import os
import zipfile
import io
from datetime import datetime, timezone

def get_component_zip_file(component_id):
    """
    Create a ZIP file containing all component files organized in folders
    
    Structure:
    component-name/
    ├── vue/
    │   └── component.vue
    ├── html/
    │   └── template.html
    ├── css/
    │   └── styles.css
    ├── javascript/
    │   └── script.js
    ├── docs/
    │   ├── usage-guide.md
    │   ├── features.md
    │   └── requirements.md
    └── metadata.json
    """
    try:
        component = ComponentExample.query.filter_by(id=component_id).first()
        
        if not component:
            return None
        
        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()
        
        # Create ZIP with component name as root folder
        component_folder = component.title.replace(' ', '-').lower()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            # Vue code
            if component.vue_code:
                zip_file.writestr(
                    f'{component_folder}/vue/component.vue',
                    component.vue_code
                )
            
            # HTML code
            if component.html_code:
                zip_file.writestr(
                    f'{component_folder}/html/template.html',
                    component.html_code
                )
            
            # CSS code
            if component.css_code:
                zip_file.writestr(
                    f'{component_folder}/css/styles.css',
                    component.css_code
                )
            
            # JavaScript code
            if component.javascript_code:
                zip_file.writestr(
                    f'{component_folder}/javascript/script.js',
                    component.javascript_code
                )
            
            # Documentation files
            docs_content = {}
            
            if component.usage_guide:
                zip_file.writestr(
                    f'{component_folder}/docs/usage-guide.md',
                    component.usage_guide
                )
            
            if component.features:
                zip_file.writestr(
                    f'{component_folder}/docs/features.md',
                    component.features
                )
            
            if component.requirements:
                zip_file.writestr(
                    f'{component_folder}/docs/requirements.md',
                    component.requirements
                )
            
            # Create metadata file
            metadata = {
                'title': component.title,
                'description': component.description,
                'version': component.version,
                'category': component.category,
                'difficulty': component.difficulty,
                'tags': component.tags.split(',') if component.tags else [],
                'created_at': component.created_at.isoformat() if component.created_at else None,
                'updated_at': component.updated_at.isoformat() if component.updated_at else None,
            }
            
            zip_file.writestr(
                f'{component_folder}/metadata.json',
                json.dumps(metadata, indent=2)
            )
            
            # Create README
            readme_content = f"""# {component.title}

**Version:** {component.version}
**Category:** {component.category}
**Difficulty:** {component.difficulty}

## Description

{component.description or 'No description provided'}

## Tags

{', '.join(component.tags.split(',')) if component.tags else 'No tags'}

## File Structure
```
{component_folder}/
├── vue/
│   └── component.vue           # Vue component code
├── html/
│   └── template.html           # HTML template
├── css/
│   └── styles.css              # CSS styles
├── javascript/
│   └── script.js               # JavaScript code
├── docs/
│   ├── usage-guide.md          # How to use this component
│   ├── features.md             # Component features
│   └── requirements.md         # Requirements & dependencies
├── metadata.json               # Component metadata
└── README.md                   # This file
```

## Usage

See `docs/usage-guide.md` for detailed usage instructions.

## Features

See `docs/features.md` for a list of features.

## Requirements

See `docs/requirements.md` for dependencies and requirements.

---

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            zip_file.writestr(
                f'{component_folder}/README.md',
                readme_content
            )
        
        # Reset buffer position to beginning
        zip_buffer.seek(0)
        return zip_buffer
        
    except Exception as e:
        print(f"Error creating ZIP file: {str(e)}")
        return None
    
def DeleteComponent(component_id):
    """
    Delete a component by ID
    
    Args:
        component_id (int): Component ID to delete
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        component = ComponentExample.query.filter_by(id=component_id).first()
        
        if not component:
            return False, "Component not found"
        

        if component.image_filename:
            image_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'static',
                'images',
                'components',
                component.image_filename
            )
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image: {str(e)}")

        db.session.delete(component)
        db.session.commit()
        
        return True, f"Component '{component.title}' deleted successfully"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting component: {str(e)}"
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import FileField, StringField, TextAreaField, SelectField, SubmitField, BooleanField
from wtforms.validators import InputRequired, DataRequired, ValidationError, Length, Optional
from flask import url_for
import re

from app.db_class.db import ComponentExample


class AddComponentExampleForm(FlaskForm):
    """
    Form for creating and editing component examples
    Follows the same validation pattern as AddNewRuleForm
    """
    
    # Basic Information
    title = StringField(
        'Component Title',
        validators=[
            InputRequired(message='Component title is required'),
            Length(min=3, max=128, message='Title must be between 3 and 128 characters')
        ],
        render_kw={
            'placeholder': 'Enter component title (e.g., "Pagination Basic")...',
            'class': 'form-control rounded-3'
        }
    )
    
    category = SelectField(
        'Category',
        choices=[],
        validators=[DataRequired(message='Category is required')],
        render_kw={'class': 'form-select rounded-3'}
    )
    
    description = TextAreaField(
        'Description',
        validators=[Optional(), Length(max=1000)],
        render_kw={
            'placeholder': 'Describe the component purpose and functionality...',
            'rows': 3,
            'class': 'form-control rounded-3'
        }
    )
    
    # Difficulty Level
    difficulty = SelectField(
        'Difficulty Level',
        choices=[
            ('beginner', 'Beginner - Easy to understand and implement'),
            ('intermediate', 'Intermediate - Requires some knowledge'),
            ('advanced', 'Advanced - Complex implementation')
        ],
        default='beginner',
        validators=[DataRequired()],
        render_kw={'class': 'form-select rounded-3'}
    )
    
    # Version
    version = StringField(
        'Version',
        default='1.0.0',
        validators=[
            InputRequired(message='Version is required'),
            Length(min=5, max=20, message='Version format should be like 1.0.0')
        ],
        render_kw={
            'placeholder': '1.0.0',
            'class': 'form-control rounded-3'
        }
    )
    
    # Tags
    tags = StringField(
        'Tags',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Enter tags separated by comma (e.g., pagination,responsive,vue3)...',
            'class': 'form-control rounded-3'
        }
    )

    # Image Upload (Optional)
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Only image files are allowed !'), InputRequired(message='Image is required')
    ])
    
    # Code Section
    vue_code = TextAreaField(
        'Component Code',
        validators=[InputRequired(message='Component code is required')],
        render_kw={
            'placeholder': '''const ComponentYourComponent = {
...component code here...
};
export default ComponentYourComponent;
            ''',
            'rows': 10,
            'class': 'form-control rounded-3',
            'id': 'vue-editor'
        }
    )
    
    html_code = TextAreaField(
        'HTML Markup (Optional)',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Optional: HTML markup example...',
            'rows': 8,
            'class': 'form-control rounded-3',
            'id': 'html-editor'
        }
    )
    
    css_code = TextAreaField(
        'CSS Styling (Optional)',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Optional: CSS styling for the component...',
            'rows': 8,
            'class': 'form-control rounded-3',
            'id': 'css-editor'
        }
    )
    
    javascript_code = TextAreaField(
        'JavaScript Code (Optional)',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Optional: Additional JavaScript if needed...',
            'rows': 8,
            'class': 'form-control rounded-3',
            'id': 'js-editor'
        }
    )
    
    # Documentation
    usage_guide = TextAreaField(
        'Usage Guide',
        validators=[Optional(), Length(max=2000)],
        render_kw={
            'placeholder': 'How to use this component - include props, events, examples...',
            'rows': 6,
            'class': 'form-control rounded-3'
        }
    )
    
    features = TextAreaField(
        'Features',
        validators=[Optional()],
        render_kw={
            'placeholder': 'List the key features of this component (one per line)...',
            'rows': 4,
            'class': 'form-control rounded-3'
        }
    )
    
    requirements = TextAreaField(
        'Requirements & Dependencies',
        validators=[Optional()],
        render_kw={
            'placeholder': 'List dependencies and requirements (e.g., Vue 3.0+, Bootstrap 5+)...',
            'rows': 3,
            'class': 'form-control rounded-3'
        }
    )
    
    # Status
    is_featured = BooleanField(
        'Feature on homepage',
        render_kw={'class': 'form-check-input'}
    )
    
    is_active = BooleanField(
        'Active',
        default=True,
        render_kw={'class': 'form-check-input'}
    )
    
    # Submit
    submit = SubmitField(
        'Create Component',
        render_kw={'class': 'btn btn-primary btn-lg'}
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate category choices
        categories = [
            ('pagination', 'Pagination'),
            ('forms', 'Forms'),
            ('tables', 'Tables'),
            ('buttons', 'Buttons'),
            ('modals', 'Modals'),
            ('navigation', 'Navigation'),
            ('cards', 'Cards'),
            ('alerts', 'Alerts'),
            ('badges', 'Badges'),
            ('tooltips', 'Tooltips'),
            ('dropdowns', 'Dropdowns'),
            ('spinners', 'Spinners'),
            ('other', 'Other')
        ]
        self.category.choices = categories
    
    def validate_title(self, field):
        """Check if component with same title already exists"""
        existing = ComponentExample.query.filter_by(title=field.data, is_active=True).first()
        
        if existing:
            edit_url = url_for('component.edit_example', example_id=existing.id)
            raise ValidationError(
                f'Component already exists. '
                f'<a href="{edit_url}">Edit this component (ID: {existing.id})</a> instead?'
            )
    
    def validate_version(self, field):
        """Validate version format (semantic versioning)"""
        version_pattern = re.compile(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$')
        
        if not version_pattern.match(field.data):
            raise ValidationError(
                'Invalid version format. Use semantic versioning (e.g., 1.0.0 or 1.0.0-beta)'
            )
    
    def validate_tags(self, field):
        """Validate and normalize tags"""
        if not field.data:
            return
        
        # Split tags by comma, semicolon, or space
        tags = re.split(r'[,;\s]+', field.data.strip())
        tags = [t.strip() for t in tags if t.strip()]
        
        if not tags:
            return
        
        # Validate tag length
        invalid_tags = [t for t in tags if len(t) > 30]
        if invalid_tags:
            raise ValidationError(
                f'Tag(s) too long (max 30 chars): {", ".join(invalid_tags)}'
            )
        
        # Validate tag format (alphanumeric + dash/underscore)
        invalid_format = [t for t in tags if not re.match(r'^[a-zA-Z0-9\-_]+$', t)]
        if invalid_format:
            raise ValidationError(
                f'Invalid tag format (alphanumeric, dash, underscore only): {", ".join(invalid_format)}'
            )
        
        # Store normalized tags back
        field.data = ','.join(tags)
    
    def validate_vue_code(self, field):
        """Validate Vue.js code content"""
        if not field.data or len(field.data.strip()) < 10:
            raise ValidationError('Vue code must not be empty and have meaningful content')
        
        # Basic check for Vue syntax
        if '<template>' not in field.data and 'export default' not in field.data:
            raise ValidationError(
                'Vue code should contain <template> or export default'
            )


class EditComponentExampleForm(AddComponentExampleForm):
    """
    Form for editing component examples
    Inherits from AddComponentExampleForm but modifies some validation
    """
    
    submit = SubmitField(
        'Update Component',
        render_kw={'class': 'btn btn-primary btn-lg'}
    )
    
    def __init__(self, example_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.example_id = example_id
        self.image.validators = [
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Only image files are allowed!'),
        Optional() 
    ]
    
    def validate_title(self, field):
        """Allow same title for the current example, but not for others"""
        existing = ComponentExample.query.filter_by(
            title=field.data,
            is_active=True
        ).filter(ComponentExample.id != self.example_id).first()
        
        if existing:
            raise ValidationError('Component with this title already exists')
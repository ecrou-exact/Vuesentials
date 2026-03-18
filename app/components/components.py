from flask import Blueprint, flash, jsonify, render_template, redirect, url_for, request
from app.components.forms import AddComponentExampleForm
from app.utils.utils import form_to_dict
from . import components_core as ComponentsModels

components_blueprint = Blueprint(
    'components',
    __name__,
    template_folder='templates',
    static_folder='static'
)

@components_blueprint.route("/create", methods=["GET", "POST"])
def create():
    """Create a new component example"""
    form = AddComponentExampleForm()
    
    if form.validate_on_submit():
        try:
            # Prepare form data
            form_dict = form_to_dict(form)
            
            # Get the image file from the form
            image_file = request.files.get('image')
            form_dict['image'] = image_file
            
            # Create component
            new_component, message, success = ComponentsModels.CreateComponent(form_dict)
            
            if success:
                flash(message, 'success')
                return redirect(url_for('components.create'))
            else:
                flash(message, 'danger')
                return render_template('components/actions/create.html', form=form, error=message)
        
        except Exception as e:
            flash(f"Unexpected error: {str(e)}", 'danger')
            return render_template('components/actions/create.html', form=form, error=str(e))
    
    return render_template('components/actions/create.html', form=form)

@components_blueprint.route("/<int:component_id>", methods=["GET"])
def detail(component_id):
    """Display component detail page"""
    

    component = ComponentsModels.get_component_by_id(component_id)
    if not component:
        flash('Component not found', 'danger')
        return redirect(url_for('components.list'))
    
    component.increment_views()
    related_components = ComponentsModels.get_related_components(component.category, component.id)
    
    return render_template(
        'components/actions/detail.html',
        component=component,
        related_components=related_components
    )

@components_blueprint.route('/list_page', methods=['GET'])
def list_page():
    """Render the components list page"""
    return render_template('components/actions/list.html')

@components_blueprint.route('/list', methods=['GET'])
def get_components_list():
    """
    Get paginated list of components with filters
    
    Query parameters:
    - page (int): Page number (default: 1)
    - search (str): Search query
    - search_field (str): 'all', 'title', 'description', 'tags'
    - sort_by (str): 'newest', 'oldest', 'most_viewed', 'most_favorites'
    - category (str): Filter by category
    - difficulty (str): Filter by difficulty level
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('search', '', type=str)
        search_field = request.args.get('search_field', 'all', type=str)
        sort_by = request.args.get('sort_by', 'newest', type=str)
        category_filter = request.args.get('category', '', type=str)
        difficulty_filter = request.args.get('difficulty', '', type=str)
        per_page = 12
        
        # Get components using core models
        paginated, total_count, total_pages = ComponentsModels.get_components_list(
            page=page,
            per_page=per_page,
            search_query=search_query,
            search_field=search_field,
            sort_by=sort_by,
            category_filter=category_filter,
            difficulty_filter=difficulty_filter
        )
        
        if paginated is None:
            return jsonify({'error': 'Failed to fetch components'}), 500
        
        # Convert components to dict
        components_data = [
            ComponentsModels.component_to_dict(component, include_full_code=False)
            for component in paginated.items
        ]
        
        return jsonify({
            'components': components_data,
            'total_components': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }), 200
    
    except Exception as e:
        print(f"Error in get_components_list: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
 
@components_blueprint.route('/categories', methods=['GET'])
def get_component_categories():
    """Get all available component categories"""
    try:
        categories = ComponentsModels.get_all_categories()
        return jsonify({'categories': categories}), 200
    
    except Exception as e:
        print(f"Error in get_component_categories: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
 
@components_blueprint.route('/<int:component_id>', methods=['GET'])
def get_component_detail(component_id):
    """Get a single component with full details"""
    try:
        component = ComponentsModels.get_component_by_id(component_id)
        
        if not component:
            return jsonify({'error': 'Component not found'}), 404
        
        # Increment view count
        ComponentsModels.increment_views(component_id)
        
        # Get related components
        related_components = ComponentsModels.get_related_components(
            category=component.category,
            exclude_id=component_id,
            limit=4
        )
        
        # Convert to dict
        component_data = ComponentsModels.component_to_dict(
            component,
            include_full_code=True
        )
        
        related_data = [
            ComponentsModels.component_to_dict(comp, include_full_code=False)
            for comp in related_components
        ]
        
        return jsonify({
            'component': component_data,
            'related_components': related_data
        }), 200
    
    except Exception as e:
        print(f"Error in get_component_detail: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
 
@components_blueprint.route('/featured', methods=['GET'])
def get_featured():
    """Get featured components"""
    try:
        components = ComponentsModels.get_featured_components(limit=6)
        components_data = [
            ComponentsModels.component_to_dict(comp, include_full_code=False)
            for comp in components
        ]
        return jsonify({'components': components_data}), 200
    
    except Exception as e:
        print(f"Error in get_featured: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
 
@components_blueprint.route('/recent', methods=['GET'])
def get_recent():
    """Get recently created components"""
    try:
        components = ComponentsModels.get_recent_components(limit=8)
        components_data = [
            ComponentsModels.component_to_dict(comp, include_full_code=False)
            for comp in components
        ]
        return jsonify({'components': components_data}), 200
    
    except Exception as e:
        print(f"Error in get_recent: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
 
@components_blueprint.route('/most-viewed', methods=['GET'])
def get_most_viewed():
    """Get most viewed components"""
    try:
        components = ComponentsModels.get_most_viewed_components(limit=8)
        components_data = [
            ComponentsModels.component_to_dict(comp, include_full_code=False)
            for comp in components
        ]
        return jsonify({'components': components_data}), 200
    
    except Exception as e:
        print(f"Error in get_most_viewed: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
 
@components_blueprint.route('/search', methods=['GET'])
def search():
    """Search components"""
    try:
        query = request.args.get('q', '', type=str)
        limit = request.args.get('limit', 10, type=int)
        
        components = ComponentsModels.search_components(query, limit=limit)
        components_data = [
            ComponentsModels.component_to_dict(comp, include_full_code=False)
            for comp in components
        ]
        
        return jsonify({'components': components_data}), 200
    
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
 
@components_blueprint.route('/category/<category>', methods=['GET'])
def get_by_category(category):
    """Get components by category"""
    try:
        components = ComponentsModels.get_components_by_category(category)
        components_data = [
            ComponentsModels.component_to_dict(comp, include_full_code=False)
            for comp in components
        ]
        
        return jsonify({
            'category': category,
            'components': components_data,
            'count': len(components_data)
        }), 200
    
    except Exception as e:
        print(f"Error in get_by_category: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
 
@components_blueprint.route('/difficulty/<difficulty>', methods=['GET'])
def get_by_difficulty(difficulty):
    """Get components by difficulty"""
    try:
        components = ComponentsModels.get_components_by_difficulty(difficulty)
        components_data = [
            ComponentsModels.component_to_dict(comp, include_full_code=False)
            for comp in components
        ]
        
        return jsonify({
            'difficulty': difficulty,
            'components': components_data,
            'count': len(components_data)
        }), 200
    
    except Exception as e:
        print(f"Error in get_by_difficulty: {str(e)}")
        return jsonify({'error': str(e)}), 500
 
 
@components_blueprint.route('/list-page', methods=['GET'])
def components_list_page():
    """Render the components list page"""
    return render_template('components/list.html')
 
 
# Register blueprint with app
def register_components_list_routes(app):
    """Register all components list routes with the Flask app"""
    app.register_blueprint(components_blueprint)
 
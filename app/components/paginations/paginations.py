from flask import Blueprint, render_template


paginations_blueprint = Blueprint(
    'paginations',
    __name__,
    template_folder='templates',
    static_folder='static'
)
@paginations_blueprint.route("/")
def paginations():
    return render_template("/components/lists/paginations.html")
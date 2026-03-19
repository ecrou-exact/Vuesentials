from flask import Flask, Blueprint, render_template, request
from .data import data_core as DataModel

home_blueprint = Blueprint(
    'home',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@home_blueprint.route("/")
def home():
    return render_template("home.html")


@home_blueprint.route("/fetchData" , methods=["GET"])
def fetchData():
    """Fetch data for exemple component"""
    page = request.args.get('page', 1, type=int)
    
    data_paginated = DataModel.get_data_page(page)
    total_data = DataModel.get_total_data_count()
    
    if data_paginated.items:
        data_list = []
        for item in data_paginated.items:
            data_list.append(item.to_json())
        
        return {
            "data": data_list,
            "total_pages": data_paginated.pages,
            "total_items": total_data,
            "current_page": page,
            "success": True,
            "message": "Data fetched successfully"
        }, 200
    
    return {"message": "No data found", "success": False}, 404
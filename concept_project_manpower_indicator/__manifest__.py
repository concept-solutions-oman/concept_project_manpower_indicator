{
    "name": "concept Project Manpower Indicator",
    "version": "1.0.0",
    "summary": "Add Start/Stop manpower indicator buttons to Project Tasks",
    "category": "Project",
    "author": "Concept Solutions ",
    "website": "https://www.csloman.com",
    "license": "OPL-1",
    "price": "15.00",
    "currency": "USD",
    "images": ["static/description/banner.png"],
    "depends": ["project", "mail", "web", "hr"],
    "data": [
       "security/ir.model.access.csv",
       "views/manpower_log_views.xml",
       "views/manpower_current_log_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'concept_project_manpower_indicator/static/src/start_stop_button.js',
            'concept_project_manpower_indicator/static/src/start_stop_button.xml', # This file now has the correct content
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
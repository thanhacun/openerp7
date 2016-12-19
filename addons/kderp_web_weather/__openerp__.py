# __openerp__.py
{
    'name': "Client Weather",
    'description': "Client Weather",
    'category': 'KDERP Apps',
    'depends': ['web', 'kderp_web_api'],
    'js': ['static/src/js/weather.js'],
    'css': ['static/src/css/weather.css'],
    'qweb': ['static/src/xml/weather.xml']
}

{
   'name': 'Keen-IT Thema',
   'description': 'Keen thema ontwikkeld door Vroege Oogst',
   'category': 'Website/Theme',
   'version': '0.0.2',
   'author': 'Yvo Rolefes - Vroege Oogst',
   'license': 'LGPL-3',
   'depends': ['website'],
   'data': [
       'views/website_templates.xml',
       'data/presets.xml',
   ],
   'assets': {
        'web._assets_primary_variables': [
            'website_keen/static/src/scss/primary_variables.scss'
        ],
        'web.assets_frontend': [
            'website_keen/static/src/js/keen.js',
            'website_keen/static/src/scss/keen.scss',
            'website_keen/static/src/scss/keen_navbar.scss',
        ],
   },
   'application': False,
   'auto_install': False,
}
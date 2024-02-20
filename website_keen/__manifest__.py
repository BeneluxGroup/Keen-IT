{
   'name': 'Keen-IT Thema',
   'description': 'Keen thema ontwikkeld door Vroege Oogst',
   'category': 'Website/Theme',
   'version': '17.0',
   'author': 'Yvo Rolefes - Vroege Oogst',
   'license': 'LGPL-3',
   'depends': ['website'],
   'assets': {
        'web.assets_frontend': [
            #('prepend', 'website_airproof/static/src/scss/primary_variables.scss'),
            'website_keen/static/src/js/keen.js',
            'website_keen/static/src/scss/keen.scss',
        ],
   },
}
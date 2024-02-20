{
   'name': 'Keen Thema',
   'description': 'Keen thema ontwikkeld door Vroege Oogst',
   'category': 'Website/Theme',
   'version': '17.0.0',
   'author': 'Yvo Rolefes - Vroege Oogst',
   'license': '...',
   'depends': ['website'],
   'data': [
      # ...
   ],
   'assets': {
        'web.assets_frontend': [
            ('prepend', 'website_airproof/static/src/scss/primary_variables.scss'),
            'website_keen/static/src/js/keen.js',
            'website_keen/static/src/scss/keen.scss',
        ],
   },
}
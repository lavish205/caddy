from tornado.template import Loader
from tornado.options import define, options
import os

# Make file paths relative to settings
path = lambda root, *a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = path(ROOT, 'media')
TEMPLATE_ROOT = path(ROOT, 'dipper/templates')


define('port', default=8888, help='run on the given port', type=int)
define('config', default=None, help='tornado config file')
define('debug', default=False, help='debug mode')
options.parse_command_line()
define('TEMPLATE_ROOT', default=TEMPLATE_ROOT, type=str,
       help='template root path')


# APIs key
AMADEUS_API_KEY = os.environ.get('AMADEUS_API_KEY')
UBER_CLIENT_ID = os.environ.get('UBER_CLIENT_ID')
UBER_SERVICE_TOKEN = os.environ.get('UBER_SERVICE_TOKEN')
UBER_CLIENT_SECRET = os.environ.get('UBER_CLIENT_SECRET')

define('AMADEUS_API_KEY', default=AMADEUS_API_KEY, type=str, help='amadeus api key')
define('UBER_CLIENT_ID', default=UBER_CLIENT_ID, type=str, help='uber client id')
define('UBER_SERVICE_TOKEN', default=UBER_SERVICE_TOKEN, type=str, help='uber service token')
define('UBER_CLIENT_SECRET', default=UBER_CLIENT_SECRET, type=str, help='uber client secret')


settings['static_path'] = MEDIA_ROOT
settings['static_url_prefix'] = '/app_static/'
settings['cookie_secret'] = "your-cookie-secret"
settings['xsrf_cookies'] = False
settings['template_loader'] = Loader(TEMPLATE_ROOT)

if options.config:
    options.parse_config_file(options.config)

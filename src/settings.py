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


if options.config:
    options.parse_config_file(options.config)

settings = dict()
settings['static_path'] = MEDIA_ROOT
settings['static_url_prefix'] = '/app_static/'
settings['cookie_secret'] = "your-cookie-secret"
settings['xsrf_cookies'] = False
settings['template_loader'] = Loader(TEMPLATE_ROOT)
settings['debug'] = True

if options.config:
    options.parse_config_file(options.config)

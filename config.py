from decouple import config

# Bot settings
BOT_TOKEN = '7548527414:AAEA-4WBptWx13gdMk_4sXV8AekPiCCp0LQ'
ADMIN_IDS = []# list(map(int, config('ADMIN_IDS', default='').split(',')))

# Backend API settings
API_URL = config('API_URL', default='https://volkov-egor.tech/api')
API_USERNAME = config('API_USERNAME', default='admin')
API_PASSWORD = config('API_PASSWORD', default='admin')

# Default VPN settings
DEFAULT_TRAFFIC_LIMIT_GB = float(config('DEFAULT_TRAFFIC_LIMIT_GB', default='10'))
DEFAULT_EXPIRATION_DAYS = int(config('DEFAULT_EXPIRATION_DAYS', default='30'))

# Other settings
LOG_LEVEL = config('LOG_LEVEL', default='INFO')
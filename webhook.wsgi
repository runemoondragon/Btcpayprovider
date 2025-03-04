import sys
import os

# Add your application directory to the Python path
sys.path.insert(0, '/path/to/your/application')

# Set environment variables
os.environ['BTCPAY_URL'] = 'https://bti.btcpayprovider.com'
os.environ['ADMIN_API_KEY'] = 'your_api_key'

# Import your application
from webhook_listener import app as application 
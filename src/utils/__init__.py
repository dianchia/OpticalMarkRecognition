import urllib3
from .web_utils import create_session
from .excel_utils import fix_ic, forms2int, validate_name

urllib3.disable_warnings()

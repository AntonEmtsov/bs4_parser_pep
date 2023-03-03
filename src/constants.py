from pathlib import Path
from urllib.parse import urljoin


BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
RESULTS = 'results'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
PARSER_OPTION_FILE = 'file'
PARSER_OPTION_PRETTY = 'pretty'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEPS_URL = 'https://peps.python.org/'
WHATS_NEW_URL = urljoin(MAIN_DOC_URL, 'whatsnew/')

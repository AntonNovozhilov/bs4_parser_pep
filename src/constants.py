from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
NAMEDATE = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'Active': ('Active',),
    'Accepted': ('Accepted',),
    'Deferred': ('Deferred',),
    'Final': ('Final',),
    'Provisional': ('Provisional',),
    'Rejected': ('Rejected',),
    'Superseded': ('Superseded',),
    'Withdrawn': ('Withdrawn',),
    'Draft': ('Draft',),
    '': (),
}

from db import DBConnect
from state_db import DBState

TOKEN = 'YOUR_TOKEN_HERE'
db = DBConnect('postgres', '1812')
db_state = DBState('postgres', '1812')
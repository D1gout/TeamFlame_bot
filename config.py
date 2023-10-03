from db import DBConnect
from state_db import DBState

TOKEN = '6679498473:AAF4W-J5JtXTbKcoRDlt9BnsUqThsAEPCRY'
db = DBConnect('postgres', '1812')
db_state = DBState('postgres', '1812')
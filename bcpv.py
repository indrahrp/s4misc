import bcp
HOST='s4-de-id-data.cptsdxoamyod.us-east-1.rds.amazonaws.com'
user='sema4user'
user_pwd='Sema4morgan123'
conn = bcp.Connection(host='HOST', driver='mssql', username=user, password=user_pwd)
my_bcp = bcp.BCP(conn)
file = bcp.DataFile(file_path='/tmp/testf', delimiter=',')
my_bcp.load(input_file=file, table='table_name')
import pypyodbc

driver = 'ODBC Driver 17 for SQL Server'
print("driver:{}".format(driver))
#con = pypyodbc.connect('DRIVER={driver};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password')
server='s4-de-id-data-prod.cptsdxoamyod.us-east-1.rds.amazonaws.com'
database='test-database'
username='admin'
password='Sema4Morgan123'
#cnxn = pypyodbc.connect('Driver={driver},Server='s4-de-id-data-prod.cptsdxoamyod.us-east-1.rds.amazonaws.com',Database='test-database',uid='admin',pwd='Sema4Morgan123'')
cnxn = pypyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
print (str(cnxn))
cursor = cnxn.cursor()
cursor.execute("SELECT @@version;")

#cursor = cnxn.cursor()
print ("Connected {}:", format(str(cursor)))
row = cursor.fetchone()
while row:
    print row
    row = cursor.fetchone()





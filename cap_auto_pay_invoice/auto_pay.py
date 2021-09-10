import xmlrpc.client

common = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
db = "v12_ent"
username = "admin"
password = "admin"
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object')
models.execute(db, uid, password, 'account.invoice', 'auto_payment', uid, 28, 7, 1)

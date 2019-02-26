import xmlrpclib
proxy = xmlrpclib.ServerProxy("http://localhost:35001/")
print "%s" % str(proxy.action_status(list(["wls_admin"])))

# xmlrpclib.Fault
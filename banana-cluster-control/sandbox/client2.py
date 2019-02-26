import xmlrpclib
proxy = xmlrpclib.ServerProxy("http://localhost:9999/")

print "%s" % str(proxy.return_list(5))
print "%s" % str(proxy.return_dict("bob", 5))
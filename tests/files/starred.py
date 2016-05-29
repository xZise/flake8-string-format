# Test some var/kwargs cases

print("{0}".format(*[42]))
# Error: P204
print("{name}".format(*[42]))
print("{0} {name}".format(42, **{'name': 1337}))

# Test some var/kwargs cases

print("{0}".format(*[42]))
# Error: FMT204
print("{name}".format(*[42]))
print("{0} {name}".format(42, **{'name': 1337}))

# Error: FMT204
print(str.format("{name}", *[42]))

# Error: FMT301
print("{0}".format(1, 2, *[42]))
# Error: FMT302
print("{a}".format(b=47, **{'a': 42}))

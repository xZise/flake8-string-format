# Test some var/kwargs cases

print("{0}".format(*[42]))
# Error: STRF204
print("{name}".format(*[42]))
print("{0} {name}".format(42, **{'name': 1337}))

# Error: STRF204
print(str.format("{name}", *[42]))

# Error: STRF301
print("{0}".format(1, 2, *[42]))
# Error: STRF302
print("{a}".format(b=47, **{'a': 42}))

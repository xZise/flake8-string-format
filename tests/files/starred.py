# Test some var/kwargs cases

print("{0}".format(*[42]))
# Error: P204
print("{name}".format(*[42]))
print("{0} {name}".format(42, **{'name': 1337}))

# Error: P204
print(str.format("{name}", *[42]))

# Allow multiple kwargs/starargs
print("{0} {1}".format(*[42], *[47]))
print("{a} {b}".format(**{'a': 42}, **{'b': 47}))

# Error: P301
print("{0}".format(*[42], 1, 2))
# Error: P302
print("{a}".format(b=47, **{'a': 42}))

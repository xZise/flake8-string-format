# Python >=3.5
# Allow multiple kwargs/starargs

print("{0} {1}".format(*[42], *[47]))
print("{a} {b}".format(**{'a': 42}, **{'b': 47}))

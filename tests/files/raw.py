# Test checking raw strings

# Error: P103 (>PY26)
x = "bar {}"
# Error: P103 (>PY26,raw)
x = r"bar {}"

# Error: P201
print(r"regex {0}".format())

# Error: P201
print(br"regex {0}".format())

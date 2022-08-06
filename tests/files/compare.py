def test_equals_const():
    return "a" == "{}"


def test_equals_format(a):
    # Error: P101 (18), P201 (18), P302 (18)
    return "a" == "{}".format(a=a)


def test_in_const():
    return "a" in "{}"


def test_in_format(a):
    # Error: P101 (18), P201 (18), P302 (18)
    return "a" in "{}".format(a=a)


def test_with_assert_const(value):
    assert value == '{}'


def test_with_assert_format(value, a):
    # Error: P101 (20), P201 (20), P302 (20)
    assert value == '{}'.format(a=a)

_l = [1, [b"2", [True, "3", {"1234567890": -70000}], False, 0.5], None]
DATA = {"bar": False, "wee": {b"2": 1000, True: _l}, "foo": 3.14159265359}


def assertListEqual(x, y):
    assert len(x) == len(y)
    for i in range(len(x)):
        item_x = x[i]
        item_y = y[i]
        type_x = type(item_x)
        type_y = type(item_y)
        assert type_x == type_y
        if type_x is list:
            assertListEqual(item_x, item_y)
            continue
        if type_x is dict:
            assertDictEqual(item_x, item_y)
            continue
        assert item_x == item_y


def assertDictEqual(x, y):
    assert len(x) == len(y)
    for k_x, v_x in x.items():
        assert k_x in y
        v_y = y[k_x]
        type_x = type(v_x)
        type_y = type(v_y)
        assert type_x == type_y
        if type_x is list:
            assertListEqual(v_x, v_y)
            continue
        if type_x is dict:
            assertDictEqual(v_x, v_y)
            continue
        assert v_x == v_y

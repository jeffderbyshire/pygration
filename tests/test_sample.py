""" content of test_sample.py """


def func(x_int):
    """ test func """
    return x_int + 1


def test_answer():
    """ test answer """
    assert func(3) == 5

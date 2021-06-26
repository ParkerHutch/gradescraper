from gradescraper.structures.term import Term


def test_comparison():
    assert Term('Spring', 2021) == Term('Spring', 2021)
    assert Term('Fall', 2021) > Term('Spring', 2021)
    assert Term('Spring', 2021) < Term('Summer', 2021)
    assert Term('Fall', 2022) > Term('Spring', 2021)


def test_init():
    a = Term('Spring', 2021)
    assert a.season == 'Spring'
    assert a.year == 2021
    split_init = Term(*'Fall 2022'.split(' '))
    assert split_init.season == 'Fall'
    assert split_init.year == '2022'

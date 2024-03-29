import functools


@functools.total_ordering
class Term:
    """A class to represent a school term that courses can take place during.

    Note:
        Currently only the 4 seasons are valid entries for the season attribute.
        Terms occuring further in the past are evaluated as less than terms 
        occuring more recently when compared.

    Attributes:
        season (str): the term's season.
        year (int): the term's year.
    """
    year: int
    season: str

    def __init__(self, season: str, year: int):
        """Create a Term for the given season during the given year.

        Args:
            season (str): the term's season.
            year (int): the term's year.
        """
        self.season = season
        self.year = year

    def __repr__(self) -> str:
        return f'{self.season} {self.year}'

    def __gt__(self, o: object):
        # More recent terms are greater than older terms
        # TODO handle unexpected seasons
        season_values = {"Spring": 0, "Summer": 1, "Fall": 2, "Winter": 3}
        if self.year > o.year:
            return True
        elif season_values[self.season] > season_values[o.season]:
            return True
        else:
            return False

    def __eq__(self, o: object):
        return self.year == o.year and self.season == o.season

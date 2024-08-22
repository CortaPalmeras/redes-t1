
class PersonQuery:
    def __init__(self,
                 social: str,
                 fnames: list[str],
                 lnames: list[str]) -> None:
        self.social = social
        self.fnames = fnames
        self.lnames = lnames

class QueryError:
    def __init__(self, reason: str):
        self.reason = reason

class QueryValidator:
    def __init__(self, socials: set[str], allows_all: bool) -> None:
        self.socials = socials
        self.allows_all = allows_all

    def validate(self,
                 social: str,
                 fnames: list[str],
                 lnames: list[str]) -> PersonQuery | QueryError:
        if social == 'all':
            if not self.allows_all:
                return QueryError('"all" is not allowed by the server.')

        elif social not in self.socials:
            return QueryError(f'requested plataform "{social}" not in the list of allowed plataforms:\n{self.socials}')
        
        def valid_name(name: str):
            return name.islower() and name.isalpha() and name.isascii()

        for name in fnames:
            if not valid_name(name):
                return QueryError(f'name "{name}" contains an invalid character.')

        for name in lnames:
            if not valid_name(name):
                return QueryError(f'name "{name}" contains an invalid character.')

        return PersonQuery(social, fnames, lnames)
        
        

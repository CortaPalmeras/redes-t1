import typing

class ValidQuery(typing.NamedTuple):
    name: str
    social: str

class QueryError(typing.NamedTuple):
    error: str

QueryValidator = typing.Callable[[list[str]], ValidQuery | QueryError]

def valid_name(name: str) -> bool:
    return name.islower() and name.isalpha() and name.isascii()

def validate_names(names: list[str]) -> str | None:
    for name in names:
        if not valid_name(name):
            return name
    return None


def master_query_validator(query_parts: list[str]) -> ValidQuery | QueryError:
    if len(query_parts) < 4:
        return QueryError(f'invalid ammount of arguments: {len(query_parts)}')

    social = query_parts[0]
    names = query_parts[1:]

    invalid_name = validate_names(names)
    if invalid_name != None:
        return QueryError(f'name "{invalid_name}" contains an invalid character.')

    return ValidQuery('/' + '/'.join(names), social)


def simple_query_validator(query_parts: list[str]) -> ValidQuery | QueryError:
    if len(query_parts) < 3:
        return QueryError(f'invalid ammount of arguments: {len(query_parts)}')

    invalid_name = validate_names(query_parts)
    if invalid_name != None:
        return QueryError(f'name "{invalid_name}" contains an invalid character.')

    return ValidQuery(' '.join(query_parts), 'all')


def multisocial_query_validator(socials: set[str]) -> QueryValidator:
    def validate_multisocial_query(query_parts: list[str]) -> ValidQuery | QueryError:
        if len(query_parts) < 4:
            return QueryError(f'invalid ammount of arguments: {len(query_parts)}')

        social = query_parts[0]
        names = query_parts[1:]

        if social != 'all' and social not in socials:
            return QueryError(f'requested plataform "{social}" not in the list of allowed plataforms: {socials}')

        invalid_name = validate_names(names)
        if invalid_name != None:
            return QueryError(f'name "{invalid_name}" contains an invalid character.')

        return ValidQuery(' '.join(names), social) 

    return validate_multisocial_query




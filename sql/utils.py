def snake_case(s):
    return s.lower().replace(' ', '_')


def pascal_case(s):
    return s.title().replace(' ', '').replace('_', '')

from django.http import HttpRequest


def create_session(request: HttpRequest) -> bool:
    """Creates a session if it does not exist

    Args:
        request (HttpRequest): HttpRequest object

    Returns:
        bool: True if created, otherwise False - session exists
    """
    session = request.session
    if session.session_key is None:
        session.create()
        return True

    return False

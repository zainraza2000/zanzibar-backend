import time
import jwt
from common.models import LoginMethod
from common.app_config import config


def generate_access_token(login_method: LoginMethod, person=None, email=None):
    """
    Generate JWT token with embedded user data to avoid database calls during authentication.

    Args:
        login_method: LoginMethod instance
        person: Person instance (optional, will be fetched if not provided)
        email: Email instance (optional, will be fetched if not provided)
    """
    expiry = time.time() + int(config.ACCESS_TOKEN_EXPIRE)

    # If person or email not provided, we'll need to fetch them
    # This should ideally be passed from the calling code to avoid extra DB calls
    payload = {
        'email_id': login_method.email_id,
        'person_id': login_method.person_id,
        'exp': expiry,
    }

    # Add person data if available
    if person:
        payload.update({
            'person_first_name': person.first_name or '',
            'person_last_name': person.last_name or '',
            'person_entity_id': person.entity_id,
        })

    # Add email data if available
    if email:
        payload.update({
            'email_address': email.email,
            'email_is_verified': email.is_verified,
            'email_entity_id': email.entity_id,
        })

    token = jwt.encode(payload, config.AUTH_JWT_SECRET, algorithm='HS256')
    return token, expiry


def parse_access_token(access_token: str):
    """
    Parse and validate JWT token, returning decoded payload if valid.
    """
    try:
        decoded_token = jwt.decode(
            access_token,
            config.AUTH_JWT_SECRET,
            algorithms=['HS256']
        )
        exp_time = decoded_token['exp']
        if time.time() <= exp_time:
            return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def create_person_from_token(token_data):
    """
    Create a Person object from JWT token data to avoid database calls.
    """
    from common.models.person import Person

    return Person(
        entity_id=token_data.get('person_entity_id', token_data.get('person_id')),
        first_name=token_data.get('person_first_name', ''),
        last_name=token_data.get('person_last_name', ''),
    )


def create_email_from_token(token_data):
    """
    Create an Email object from JWT token data to avoid database calls.
    """
    from common.models.email import Email

    return Email(
        entity_id=token_data.get('email_entity_id', token_data.get('email_id')),
        person_id=token_data.get('person_id'),
        email=token_data.get('email_address', ''),
        is_verified=token_data.get('email_is_verified', False),
    )

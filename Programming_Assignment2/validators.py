import messages


def sign_up_validator(auth_seller, cmd_tokens):
    expected_args_count = 3

    if len(cmd_tokens) != expected_args_count + 1:
        return False, messages.CMD_NOT_ENOUGH_ARGS % expected_args_count

    if auth_seller:
        return False, messages.USER_ALREADY_SIGNED_IN

    return True, None


def sign_in_validator(auth_seller, cmd_tokens):
    expected_args_count = 2

    if len(cmd_tokens) != expected_args_count + 1:
        return False, messages.CMD_NOT_ENOUGH_ARGS % expected_args_count

    if auth_seller:
        if auth_seller.seller_id == cmd_tokens[1]:
            return None, messages.USER_ALREADY_SIGNED_IN
        else:
            return None, messages.USER_OTHER_SIGNED_IN
    
    return True, None


"""
    This validator is basic validator that returns (True, None) 
    when a seller is authenticated and the number of command tokens is 1.
    Returns (False, <message>) otherwise.
"""


def basic_validator(auth_sellers, cmd_tokens):
    if auth_sellers:
        return True, None
    elif not auth_sellers and len(cmd_tokens) == 1:
        return False, messages.USER_NOT_AUTHORIZED
    else:
        return False, messages.CMD_INVALID_ARGS


def quit_validator(cmd_tokens):
    if len(cmd_tokens) == 1:
        return True, None
    else:
        return False, messages.CMD_INVALID_ARGS

def change_stock_validator(auth_seller, cmd_tokens):
    expected_args_count = 3

    if not auth_seller:
        return False, messages.USER_NOT_AUTHORIZED
    
    if len(cmd_tokens) != expected_args_count + 1:
        return False, messages.CMD_NOT_ENOUGH_ARGS % expected_args_count
    
    return True, None

def subscribe_validator(auth_seller, cmd_tokens):
    expected_args_count = 1

    if not auth_seller:
        return False, messages.USER_NOT_AUTHORIZED
    elif len(cmd_tokens) != expected_args_count + 1:
        return False, messages.CMD_NOT_ENOUGH_ARGS % expected_args_count

    return True, None

def ship_validator(cmd_tokens):
    if len(cmd_tokens) <= 1:
        return False, messages.CMD_NOT_ENOUGH_ARGS_AT_LEAST % 1
    else:
        return True, None

def show_cart_validator(cmd_tokens):
    expected_args_count = 1

    if len(cmd_tokens) == expected_args_count + 1:
        return True, None
    else:
        return False, messages.CMD_NOT_ENOUGH_ARGS % expected_args_count

def change_cart_validator(cmd_tokens):
    expected_args_count = 5

    if len(cmd_tokens) == expected_args_count + 1:
        return True, None
    else:
        return False, messages.CMD_NOT_ENOUGH_ARGS % expected_args_count

def purchase_cart_validator(cmd_tokens):
    expected_args_count = 1

    if len(cmd_tokens) == expected_args_count + 1:
        return True, None
    else:
        return False, messages.CMD_NOT_ENOUGH_ARGS % expected_args_count

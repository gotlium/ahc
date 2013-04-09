import string
import random


def approved(password):
    group = select(password[0])
    for character in password[1:]:
        trial = select(character)
        if trial is group:
            return False
        group = trial
    return True


def select(character):
    for group in (string.ascii_uppercase,
                  string.ascii_lowercase,
                  #string.punctuation,
                  string.digits):
        if character in group:
            return group
    raise ValueError('Character was not found in any group!')


def random_password(max_value=15):
    total = string.ascii_letters + string.digits # + string.punctuation
    password = ''.join(random.sample(total, max_value))
    while not approved(password):
        password = ''.join(random.sample(total, max_value))
    return password

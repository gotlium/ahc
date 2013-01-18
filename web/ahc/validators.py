import sys
import os

from django.core.exceptions import ValidationError

sys.path.insert(0, os.path.normpath(os.path.dirname(__file__)) + '/../../')

from libraries.helpers import isValidSshPublicKey


def validate_folder(folder):
	if len(folder.split('/')) < 3:
		raise ValidationError('Select path from root.')

def validate_ssh_key(key):
	if not isValidSshPublicKey(key):
		raise ValidationError("Public key is not a valid.")
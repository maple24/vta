import os
import sys
sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3]))

from vat.library.GenericHelper import GenericHelper
print(GenericHelper.get_hostname())
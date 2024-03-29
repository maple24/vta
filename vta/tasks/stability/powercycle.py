# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

import os
import sys

sys.path.append(os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4]))

"""
if you want to import without adding system path, call module as part of package
# python -m vta.tasks.powercycle
"""
from vta.library.GenericHelper import GenericHelper

print(GenericHelper.get_hostname())

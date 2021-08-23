
# Before loading the module, if the analytic_size option is given, check it.
# Its value must be an integer greater or equal to the default value.
from odoo.tools import config
errors = ["[analytic]"]
try:
    assert int(config.get_misc('analytic', 'analytic_size', 5)) >= 5
except (ValueError, AssertionError):
    errors.append("analytic_size must be an integer greater/equal to 5.")
try:
    assert config.get_misc('analytic', 'translate', False) in [True, False]
except (AssertionError):
    errors.append("translate must be a boolean value.")
if len(errors) > 1:
    config.parser.error("\n * ".join(errors))


#from . import MetaAnalytic	#SARFRAZ
from . import analytic_code
from . import analytic_dimension
from . import analytic_structure

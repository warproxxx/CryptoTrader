import logging

import sys
import timesearch



if __name__ == "__main__":
    handler = logging.StreamHandler()
    log_format = '{levelname}:timesearch.{module}.{funcName}: {message}'
    handler.setFormatter(logging.Formatter(log_format, style='{'))
    logging.getLogger().addHandler(handler)
    
    status_code = timesearch.main(sys.argv[1:])
    raise SystemExit(status_code)
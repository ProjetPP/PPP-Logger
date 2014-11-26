#!/usr/bin/env python3
import os
import unittest

def main(): # pragma: no cover
    os.environ['PPP_LOGGER_CONFIG'] = 'example_config.json'
    testsuite = unittest.TestLoader().discover('tests/')
    results = unittest.TextTestRunner(verbosity=1).run(testsuite)
    if results.errors or results.failures:
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    main()

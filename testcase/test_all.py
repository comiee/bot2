import unittest

if __name__ == '__main__':
    paths = [
        'test_communication',
        'test_robot',
    ]

    suite = unittest.TestSuite()
    for path in paths:
        discover = unittest.TestLoader().discover(path, pattern="*.py")
        suite.addTest(discover)

    runner = unittest.TextTestRunner()
    runner.run(suite)

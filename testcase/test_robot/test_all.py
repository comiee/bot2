import unittest

if __name__ == '__main__':
    suite = unittest.TestSuite()

    discover = unittest.TestLoader().discover('.', pattern="*.py")
    suite.addTest(discover)

    runner = unittest.TextTestRunner()
    runner.run(suite)

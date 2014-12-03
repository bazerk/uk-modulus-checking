import unittest
# noinspection PyProtectedMember
from ukmodulus import validate_number, _clean_input, _get_weightings, ModulusWeight, _run_check


class SimpleValidationTests(unittest.TestCase):
    def test_clean_input(self):
        self.assertRaises(ValueError, _clean_input, 'invalid')
        self.assertRaises(ValueError, _clean_input, '12a3456')
        self.assertRaises(ValueError, _clean_input, '1234567', 6)
        self.assertEqual(_clean_input('12-34-56'), '123456')
        self.assertEqual(_clean_input('12 34 56'), '123456')


class RunAlgorithmChecks(unittest.TestCase):
    def test_dbla(self):
        cases = [
            (ModulusWeight('', '', 'DBLAL', [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], None), '49927312345678', False),
        ]
        for case in cases:
            self.assertEqual(_run_check(case[1], case[0]), case[2])


class ValcadosDataLoadingTests(unittest.TestCase):
    """
    These test the loading of the valacdos.txt data
    """
    def test_valid_weightings(self):
        weightings = _get_weightings('010005')
        self.assertEqual(len(weightings), 1)
        self.assertEqual(weightings[0].algorithm, 'MOD11')
        self.assertEqual(weightings[0].exception_code, None)
        self.assertEqual(weightings[0].weightings, [0, 0, 0, 0, 0, 0, 8, 7, 6, 5, 4, 3, 2, 1])
        weightings = _get_weightings('070116')
        self.assertEqual(len(weightings), 2)
        self.assertEqual(weightings[0].algorithm, 'MOD11')
        self.assertEqual(weightings[0].exception_code, '12')
        self.assertEqual(weightings[1].algorithm, 'MOD10')
        weightings = _get_weightings('989999')
        self.assertEqual(len(weightings), 2)
        self.assertEqual(weightings[0].algorithm, 'MOD11')
        self.assertEqual(weightings[1].algorithm, 'DBLAL')

    def test_invalid_weightings(self):
        weightings = _get_weightings('010003')
        self.assertEqual(len(weightings), 0)
        weightings = _get_weightings('049999')
        self.assertEqual(len(weightings), 0)
        weightings = _get_weightings('999999')
        self.assertEqual(len(weightings), 0)


class ValacdosTests(unittest.TestCase):
    """
    These are the test cases listed in the Vocalink documentation (v3.10)
    """

    def test_case_no1(self):
        self.assertEqual(validate_number('089999', '66374958'), True)

    # def test_case_no23(self):
    #     self.assertEqual(validate_number('938063', '15764273'), False)


if __name__ == '__main__':
    unittest.main()

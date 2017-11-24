import unittest
# noinspection PyProtectedMember
from ukmodulus import (validate_number, _clean_input, _get_weightings,
                       ModulusWeight, _run_check, _sc_subs,
                       _normalize_account_number_and_code)


class SimpleValidationTests(unittest.TestCase):
    def test_clean_input(self):
        self.assertRaises(ValueError, _clean_input, 'invalid')
        self.assertRaises(ValueError, _clean_input, '12a3456')
        self.assertRaises(ValueError, _clean_input, '1234567', [6])
        self.assertEqual(_clean_input('12-34-56'), '123456')
        self.assertEqual(_clean_input('12 34 56'), '123456')

    def test_normalization(self):
        test_table = [
            # account_number, sortcode, expected_account_number, expected_sort_code
            ('0123456789', '090050', '23456789', '090050'),
            ('0123456789', '080050', '01234567', '080050'),
            ('123456789', '080050', '23456789', '080051'),
            ('1234567', '080050', '01234567', '080050'),
            ('123456', '080050', '00123456', '080050'),
        ]

        for test_entry in test_table:
            account_number, sortcode, expected_account_number, expected_sort_code = test_entry

            res_acc, res_sort = _normalize_account_number_and_code(account_number, sortcode)

            self.assertEqual(res_acc, expected_account_number)
            self.assertEqual(res_sort, expected_sort_code)


class RunAlgorithmChecks(unittest.TestCase):
    def test_dbla(self):
        cases = [
            (ModulusWeight('', '', 'DBLAL', [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], None), '499273', '12345678',
             True),
            (ModulusWeight('', '', 'DBLAL', [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], None), '499273', '12345679',
             False),
        ]
        for case in cases:
            self.assertEqual(_run_check(case[1], case[2], case[0]), case[3])

    def test_mod10(self):
        cases = [
            (ModulusWeight('', '', 'MOD10', [0, 0, 0, 0, 0, 0, 7, 1, 3, 7, 1, 3, 7, 1], None), '080211', '11111111',
             True),
            (ModulusWeight('', '', 'MOD10', [0, 0, 0, 0, 0, 0, 7, 1, 3, 7, 1, 3, 7, 1], None), '080211', '11111112',
             False),
        ]
        for case in cases:
            self.assertEqual(_run_check(case[1], case[2], case[0]), case[3])

    def test_mod11(self):
        cases = [
            (ModulusWeight('', '', 'MOD11', [0, 0, 0, 0, 0, 0, 7, 5, 8, 3, 4, 6, 2, 1], None), '000000', '58177632',
             True),
            (ModulusWeight('', '', 'MOD11', [0, 0, 0, 0, 0, 0, 7, 5, 8, 3, 4, 6, 2, 1], None), '000000', '58177633',
             False),
        ]
        for case in cases:
            self.assertEqual(_run_check(case[1], case[2], case[0]), case[3])

    def test_exception_1(self):
        cases = [
            (ModulusWeight('', '', 'DBLAL', [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], '1'), '499273', '12345678',
             False),
            (ModulusWeight('', '', 'DBLAL', [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], '1'), '499273', '12345671',
             True),
        ]

        for case in cases:
            self.assertEqual(_run_check(case[1], case[2], case[0]), case[3])

    def test_exception_3(self):
        cases = [
            (ModulusWeight('', '', 'DBLAL', [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], '3'), '499273', '12645678',
             True),
            (ModulusWeight('', '', 'DBLAL', [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1], '3'), '499273', '12945671',
             True),
        ]
        for case in cases:
            self.assertEqual(_run_check(case[1], case[2], case[0]), case[3])

    def test_exception_4(self):
        cases = [
            (ModulusWeight('', '', 'MOD11', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], '4'), '000000', '00000009',
             True),
            (ModulusWeight('', '', 'MOD11', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], '4'), '000000', '00000011',
             False),
        ]
        for case in cases:
            self.assertEqual(_run_check(case[1], case[2], case[0]), case[3])


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

    def test_scsubs(self):
        self.assertEqual(_sc_subs.get('938173', None), '938017')
        self.assertEqual(_sc_subs.get('938654', None), '938621')
        self.assertEqual(_sc_subs.get('838654', None), None)


class ValacdosTests(unittest.TestCase):
    """
    These are the test cases listed in the Vocalink documentation (v3.10)
    """

    def test_case_no1(self):
        self.assertEqual(validate_number('089999', '66374958'), True)

    def test_case_no2(self):
        self.assertEqual(validate_number('107999', '88837491'), True)

    def test_case_no3(self):
        self.assertEqual(validate_number('202959', '63748472'), True)

    def test_case_no4(self):
        self.assertEqual(validate_number('871427', '46238510'), True)

    def test_case_no5(self):
        self.assertEqual(validate_number('872427', '46238510'), True)

    def test_case_no6(self):
        self.assertEqual(validate_number('871427', '09123496'), True)

    def test_case_no7(self):
        self.assertEqual(validate_number('871427', '99123496'), True)

    def test_case_no8(self):
        self.assertEqual(validate_number('820000', '73688637'), True)

    def test_case_no9(self):
        self.assertEqual(validate_number('827999', '73988638'), True)

    def test_case_no10(self):
        self.assertEqual(validate_number('827101', '28748352'), True)

    def test_case_no11(self):
        self.assertEqual(validate_number('134020', '63849203'), True)

    def test_case_no12(self):
        self.assertEqual(validate_number('118765', '64371389'), True)

    def test_case_no13(self):
        self.assertEqual(validate_number('200915', '41011166'), True)

    def test_case_no14(self):
        self.assertEqual(validate_number('938611', '07806039'), True)

    def test_case_no15(self):
        self.assertEqual(validate_number('938600', '42368003'), True)

    def test_case_no16(self):
        self.assertEqual(validate_number('938063', '55065200'), True)

    def test_case_no17(self):
        self.assertEqual(validate_number('772798', '99345694'), True)

    def test_case_no18(self):
        self.assertEqual(validate_number('086090', '06774744'), True)

    def test_case_no19(self):
        self.assertEqual(validate_number('309070', '02355688'), True)

    def test_case_no20(self):
        self.assertEqual(validate_number('309070', '12345668'), True)

    def test_case_no21(self):
        self.assertEqual(validate_number('309070', '12345677'), True)

    def test_case_no22(self):
        self.assertEqual(validate_number('309070', '99345694'), True)

    def test_case_no23(self):
        self.assertEqual(validate_number('938063', '15764273'), False)

    def test_case_no24(self):
        self.assertEqual(validate_number('938063', '15764264'), False)

    def test_case_no25(self):
        self.assertEqual(validate_number('938063', '15763217'), False)

    def test_case_no26(self):
        self.assertEqual(validate_number('118765', '64371388'), False)

    def test_case_no27(self):
        self.assertEqual(validate_number('203099', '66831036'), False)

    def test_case_no28(self):
        self.assertEqual(validate_number('203099', '58716970'), False)

    def test_case_no29(self):
        self.assertEqual(validate_number('089999', '66374959'), False)

    def test_case_no30(self):
        self.assertEqual(validate_number('107999', '88837493'), False)

    def test_case_no31(self):
        self.assertEqual(validate_number('074456', '12345112'), True)

    def test_case_no32(self):
        self.assertEqual(validate_number('070116', '34012583'), True)

    def test_case_no33(self):
        self.assertEqual(validate_number('074456', '11104102'), True)

    def test_case_no34(self):
        self.assertEqual(validate_number('180002', '00000190'), True)


if __name__ == '__main__':
    unittest.main()

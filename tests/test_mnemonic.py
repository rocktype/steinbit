import unittest

from steinbit.mnemonic import mnemonics


class MnemonicTest(unittest.TestCase):

    def test_nnemonic(self):
        result = mnemonics([
            'Some prefixes are duplicated',
            'Some prefixes are the same',
            'Some are different',
            'Some vowels',
            'Removed'])
        self.assertListEqual(
            result, [
                'SMPRFXSR1', 'SMPRFXSR2', 'SMRDFFRN',
                'SMVOWELS', 'REMOVED'])

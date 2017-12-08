import os
import shutil
import unittest

from supporting_files import utils

class UtilsTestCases(unittest.TestCase):

    def setUp(self):
        # Define testdir
        self.testdir = 'testdir'

    def tearDown(self):
        # Cleanup 'testdir', if present
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)

    def test_get_extension_nii(self):
        """ Get extension if .nii """
        fname = 'T1w.nii'
        ext = utils.get_extension(fname)
        self.assertEqual('.nii', ext)

    def test_get_extension_niigz(self):
        """ Get extension if .nii.gz """
        fname = 'T1w.nii.gz'
        ext = utils.get_extension(fname)
        self.assertEqual('.nii.gz', ext)

    def test_get_extension_tsv(self):
        """ Get extension if .tsv """
        fname = 'T1w.tsv'
        ext = utils.get_extension(fname)
        self.assertEqual('.tsv', ext)

    def test_get_extension_none(self):
        """ Assert function returns None if no extension present """
        fname = 'sub-01_T1w'
        ext = utils.get_extension(fname)
        self.assertIsNone(ext)

if __name__ == "__main__":

    unittest.main()
    run_module_suite()

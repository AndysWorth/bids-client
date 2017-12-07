import csv
import json
import os
import shutil
import unittest

import flywheel

import export_bids

class BidsExportTestCases(unittest.TestCase):

    def setUp(self):
        # Define testdir
        self.testdir = 'testdir'

    def tearDown(self):
        # Cleanup 'testdir', if present
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)

    def _create_json(self, filename, contents):
        with open(filename, 'w') as fp:
            fp.write(json.dumps(contents))

    def _create_tsv(self, filename, contents):
        with open(filename, 'w') as fp:
            writer = csv.writer(fp, delimiter='\t')
            for row in contents:
                writer.writerow(row)

    def test_validate_dirname_valid(self):
        """ Assert function does not raise error when valid dirname an input"""
        # Get directory the test script is in...
        os.mkdir(self.testdir)
        # Call function
        export_bids.validate_dirname(self.testdir)

    def test_validate_dirname_doesnotexist(self):
        """ Assert function raises error when dirname does not exist"""
        # Define path that does not exist
        dirname = '/pathdoesnotexist'
        # Assert SystemExit raised
        with self.assertRaises(SystemExit) as err:
            export_bids.validate_dirname(dirname)

    def test_validate_dirname_file(self):
        """ Assert function raises error when file used as an input"""
        # Get filename of the test script
        filename = os.path.abspath(__file__)
        # Assert SystemExit raised
        with self.assertRaises(SystemExit) as err:
            export_bids.validate_dirname(filename)

    def test_define_path_valid(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {
                'info': {
                    namespace: {
                        'Path': '',
                        'Folder': '/',
                        'Filename': 'test.json'
                        }
                    }
                }
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is as expected
        self.assertEqual(path,
                '/test/test.json'
                )



if __name__ == "__main__":

    unittest.main()
    run_module_suite()

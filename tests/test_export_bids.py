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

    def test_define_path_empty_filename(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {
                'info': {
                    namespace: {
                        'Path': '/this/is/the/path',
                        'Folder': 'path',
                        'Filename': ''
                        }
                    }
                }
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is empty string
        self.assertEqual(path, '')

    def test_define_path_no_info(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {'test': {'test2': 'abcdef'}}
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is empty string
        self.assertEqual(path, '')

    def test_define_path_no_namespace(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {'info': {'test2': 'abcdef'}}
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is empty string
        self.assertEqual(path, '')

    def test_define_path_namespace_is_NA(self):
        """ """
        # Define inputs
        outdir = '/test/'
        namespace = 'BIDS'
        f = {'info': {namespace: 'NA'}}
        # Call function
        path = export_bids.define_path(outdir, f, namespace)
        # Assert path is empty string
        self.assertEqual(path, '')

    def test_create_json_BIDS_present(self):
        """ """
        # Define inputs
        bids_info = {
                'BIDS': {
                    'test1': 'abc',
                    'test2': 'def'
                    },
                'test1': 'abc',
                'test2': 'def'
                }
        os.mkdir(self.testdir)
        path = os.path.join(self.testdir, 'test.json')
        # Call function
        export_bids.create_json(bids_info, path, 'BIDS')
        # Ensure JSON file is created
        self.assertTrue(os.path.exists(path))

    def test_create_json_BIDS_notpresent(self):
        """ """
        # Define inputs
        bids_info = {
                'test1': 'abc',
                'test2': 'def'
                }
        os.mkdir(self.testdir)
        path = os.path.join(self.testdir, 'test.json')
        # Call function
        export_bids.create_json(bids_info, path, 'BIDS')
        # Ensure JSON file is created
        self.assertTrue(os.path.exists(path))

    def test_create_json_func_taskname(self):
        """ """
        # Define inputs
        bids_info = {
                'BIDS': {'Task': 'testtaskname'},
                'test1': 'abc',
                'test2': 'def'
                }
        os.mkdir(self.testdir)
        dirname = os.path.join(self.testdir, 'func')
        os.mkdir(dirname)
        path = os.path.join(dirname, 'test.json')
        # Call function
        export_bids.create_json(bids_info, path, 'BIDS')
        # Ensure JSON file is created
        self.assertTrue(os.path.exists(path))
        # Read in the JSON file, and assert
        with open(path, 'r') as jsonfile:
            json_contents = json.load(jsonfile)
        # Check 'TaskName' is in JSON and correct
        self.assertEqual(json_contents['TaskName'],
                'testtaskname')

    def test_exclude_containers(self):
        container = {
            'info': {
                'BIDS': {
                    'template': 'acquisition',
                    'ignore': False
                }
            },
            'label': 'Acquisition_Label_Test'
        }
        self.assertTrue(not export_bids.is_container_excluded(container, 'BIDS'))
        container = {
            'info': {
                'BIDS': {
                    'template': 'acquisition',
                    'ignore': True
                }
            },
            'label': 'Acquisition_Label_Test'
        }
        self.assertTrue(export_bids.is_container_excluded(container, 'BIDS'))

    def test_exclude_ignored_files(self):
        container = {
            'info': {
                'BIDS': {
                    'template': 'func_file',
                    'ignore': False
                }
            }
        }
        self.assertTrue(not export_bids.is_file_excluded(container, 'BIDS', True))
        container = {
            'info': {
                'BIDS': {
                    'template': 'func_file',
                    'ignore': True
                }
            }
        }
        self.assertTrue(export_bids.is_file_excluded(container, 'BIDS', True))


if __name__ == "__main__":

    unittest.main()
    run_module_suite()

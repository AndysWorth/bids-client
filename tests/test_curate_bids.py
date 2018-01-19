import os
import shutil
import unittest

import flywheel

import curate_bids
from supporting_files.templates import BIDS_TEMPLATE

class BidsCurateTestCases(unittest.TestCase):

    def setUp(self):
        # Define testdir
        self.testdir = 'testdir'

    def tearDown(self):
        # Cleanup 'testdir', if present
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)

    def test_validate_meta_info_valid1(self):
        """ """
        # Define meta information
        meta_info = {'info': {'BIDS': {}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_valid2(self):
        """ """
        # Define meta information - Path is empty string - this is ok!!
        meta_info = {'info': {'BIDS': {'Path': '', 'extra': 'test'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_valid3(self):
        """ """
        # Define meta information - Folder is empty string - this is ok!!
        meta_info = {'info': {'BIDS': {'Folder': '', 'extra': 'test'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_valid4(self):
        """ """
        # Define meta information - not required fields...
        meta_info = {'info': {'BIDS': {
            'Run': '', 'Ce': '',
            'Mod': '', 'Acq': '', 'Rec': ''}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_valid5(self):
        """ """
        # Define meta information - not required fields...
        meta_info = {'info': {'BIDS': {'Run': 1}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')
        # Assert run numebr is still an integer
        self.assertEqual(meta_info['info']['BIDS']['Run'], 1)

    def test_validate_meta_info_invalid1(self):
        """ """
        # Define meta information - Task value is missing
        meta_info = {'info': {'BIDS': {'template': 'task_events_file', 'Task': '', 'Modality': 'bold'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
                'Missing required property: Task. ')

    def test_validate_meta_info_invalid2(self):
        """ """
        # Define meta information - Filename is missing
        meta_info = {'info': {'BIDS': {'template': 'anat_file', 'Filename': '', 'extra': 'test'}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
                'Missing required property: Filename. ')

    def test_validate_meta_info_invalid3(self):
        """ """
        # Define meta information - Modality value is missing
        meta_info = {'info': {'BIDS': {'template': 'anat_file', 'Modality': ''}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
                'Missing required property: Modality. ')

    def test_validate_meta_info_invalid_characters1(self):
        """ """
        # Define meta information - invalid characters in multiple keys
        meta_info = {'info': {'BIDS': {
            'template': 'anat_file',
            'Modality': 'invalid._#$*%',
            'Ce': 'invalid2.',
            'Mod': '_invalid2',
            'Filename': ''
            }}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == False
        self.assertFalse(meta_info['info']['BIDS']['valid'])
        # Assert error message is correct
        self.assertEqual(meta_info['info']['BIDS']['error_message'],
                'Invalid characters in property: Ce. '+\
                'Missing required property: Filename. ' +\
                'Invalid characters in property: Mod. '+\
                'Invalid characters in property: Modality. '
                )

    def test_validate_meta_info_no_BIDS(self):
        """ """
        # Define meta information w/o BIDS info
        meta_info = {'info': {'test1' : 'abc', 'test2': 'def'}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS': 'NA' is in meta_info
        self.assertEqual(meta_info['info']['BIDS'], 'NA')

    def test_validate_meta_info_no_info(self):
        """ """
        # Define meta information w/o BIDS info
        meta_info = {'other_info': 'test'}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS': 'NA' is in meta_info
        self.assertEqual(meta_info['info']['BIDS'], 'NA')

    def test_validate_meta_info_BIDS_NA(self):
        """ """
        # Define meta information w/ BIDS NA
        meta_info = {'info': {'BIDS': 'NA'}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS': 'NA' is in meta_info
        self.assertEqual(meta_info['info']['BIDS'], 'NA')

    def test_validate_meta_info_already_valid(self):
        """ """
        # Define meta information - not required fields...
        meta_info = {'info': {'BIDS': {
            'Filename': 'sub-01_ses-02_T1w.nii.gz',
            'Modality': 'T1w',
            'valid': True,
            'error_message': ''}}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')

    def test_validate_meta_info_was_invalid(self):
        """ """
        # Define meta information - not required fields...
        meta_info = {'info': {'BIDS': {
            'Task': 'testtask', 'Modality': 'bold',
            'Filename': 'sub-01_ses-02_task-testtask_bold.nii.gz',
            'valid': False,
            'error_message': 'Missing required property: Task. ',
            }}}
        # Call function
        curate_bids.validate_meta_info(meta_info, BIDS_TEMPLATE)
        # Assert 'BIDS.valid' == True
        self.assertTrue(meta_info['info']['BIDS']['valid'])
        # Assert error message is empty string
        self.assertEqual(meta_info['info']['BIDS']['error_message'], '')


if __name__ == "__main__":

    unittest.main()
    run_module_suite()

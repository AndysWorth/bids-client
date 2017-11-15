import os
import shutil
import unittest

import flywheel

import upload_bids

class BidsUploadTestCases(unittest.TestCase):

    def setUp(self):
        # Define testdir
        self.testdir = 'testdir'

    def tearDown(self):
        # Cleanup 'testdir', if present
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)

    def test_validate_dirname_valid(self):
        """ Assert function does not raise error when valid dirname an input"""
        # Get directory the test script is in...
        dirname = os.path.dirname(os.path.abspath(__file__))
        # Call function
        upload_bids.validate_dirname(dirname)

    def test_validate_dirname_doesnotexist(self):
        """ Assert function raises error when dirname does not exist"""
        # Define path that does not exist
        dirname = '/pathdoesnotexist'
        # Assert SystemExit raised
        with self.assertRaises(SystemExit) as err:
            upload_bids.validate_dirname(dirname)

    def test_validate_dirname_file(self):
        """ Assert function raises error when file used as an input"""
        # Get filename of the test script
        filename = os.path.abspath(__file__)

        # Assert SystemExit raised
        with self.assertRaises(SystemExit) as err:
            upload_bids.validate_dirname(filename)

    def test_classify_acquisition_T1w(self):
        """ Assert T1w image classified as anatomy_t1w """
        full_fname = '/sub-01/ses-123/anat/sub-01_ses-123_T1w.nii.gz'
        classification = upload_bids.classify_acquisition(full_fname)
        print(classification)
        self.assertEqual('anatomy_t1w', classification)

    def test_classify_acquisition_T2w(self):
        """ Assert T2w image classified as anatomy_t2w """
        full_fname = '/sub-01/anat/sub-01_T2w.nii.gz'
        classification = upload_bids.classify_acquisition(full_fname)
        print(classification)
        self.assertEqual('anatomy_t2w', classification)

    def test_get_extension_nii(self):
        """ Get extension if .nii """
        fname = 'T1w.nii'
        ext = upload_bids.get_extension(fname)
        self.assertEqual('.nii', ext)

    def test_get_extension_niigz(self):
        """ Get extension if .nii.gz """
        fname = 'T1w.nii.gz'
        ext = upload_bids.get_extension(fname)
        self.assertEqual('.nii.gz', ext)

    def test_get_extension_tsv(self):
        """ Get extension if .tsv """
        fname = 'T1w.tsv'
        ext = upload_bids.get_extension(fname)
        self.assertEqual('.tsv', ext)

    def test_get_extension_none(self):
        """ Assert function returns None if no extension present """
        fname = 'sub-01_T1w'
        ext = upload_bids.get_extension(fname)
        self.assertIsNone(ext)

    def test_fill_in_properties_anat(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii.gz',
                'file': {
                    'name': 'sub-01_ses-01_acq-01_ce-label1_rec-label2_run-01_mod-label3_T1w.nii.gz',
                    'info': {
                        'BIDS': {
                            'Ce': '',
                            'Rec': '',
                            'Run': '',
                            'Mod': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'anat'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Ce': 'label1',
                    'Rec': 'label2',
                    'Run': 1,
                    'Mod': 'label3',
                    'Modality': 'T1w',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_fill_in_properties_func(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii',
                'file': {
                    'name': 'sub-01_ses-01_task-label1_acq-01_rec-label2_run-01_echo-2_bold.nii',
                    'info': {
                        'BIDS': {
                            'Task': '',
                            'Rec': '',
                            'Run': '',
                            'Echo': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'func'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Task': 'label1',
                    'Rec': 'label2',
                    'Run': 1,
                    'Echo': 2,
                    'Modality': 'bold',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_fill_in_properties_dwi(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii.gz',
                'file': {
                    'name': 'sub-01_ses-01_acq-01_run-01_dwi.nii.gz',
                    'info': {
                        'BIDS': {
                            'Run': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'dwi'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Run': 1,
                    'Modality': 'dwi',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_fill_in_properties_fmap1(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii.gz',
                'file': {
                    'name': 'sub-01_ses-01_acq-01_run-03_phasediff.nii.gz',
                    'info': {
                        'BIDS': {
                            'Run': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'fmap'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Run': 3,
                    'Modality': 'phasediff',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)

    def test_fill_in_properties_fmap2(self):
        """ """
        # Define inputs
        context = {
                'ext': '.nii.gz',
                'file': {
                    'name': 'sub-01_ses-01_acq-01_dir-label1_run-03_epi.nii.gz',
                    'info': {
                        'BIDS': {
                            'Dir': '',
                            'Run': '',
                            'Modality': '',
                            'Folder': '',
                            'Filename': ''
                            }
                        }
                    }
                }
        folder_name = 'fmap'
        # Define expected outputs
        meta_info_expected = {
                'BIDS': {
                    'Dir': 'label1',
                    'Run': 3,
                    'Modality': 'epi',
                    'Folder': folder_name,
                    'Filename': context['file']['name']
                    }
                }
        # Call function
        meta_info = upload_bids.fill_in_properties(context, folder_name)
        # Assert equal
        self.assertEqual(meta_info_expected, meta_info)


if __name__ == "__main__":

    unittest.main()
    run_module_suite()

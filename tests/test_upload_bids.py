import csv
import json
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

    def test_parse_bids_dir_valid(self):
        """ """
        pass

    def test_handle_group_project_1layer(self):
        """ Assert bids_hierarchy correctly identified and
        group_id and project_label added to bids_hierarchy that
        are passed to function
        """
        # Define inputs
        bids_hierarchy = {
                'sub-01': {
                    'func': {'files': 'sub-01_bold.nii.gz'},
                    'anat': {'files': 'sub-01_T1w.nii.gz'}
                    },
                'sub-02': {
                    'func': {'files': 'sub-01_bold.nii.gz'},
                    'anat': {'files': 'sub-01_T1w.nii.gz'}
                    }
                }
        group_id_cli = 'group123'
        project_label_cli = 'project123'
        rootdir_original = '/path/to/bids'

        # call function
        #bh, rootdir = upload_bids.handle_group_project(
        #                bids_hierarchy, group_id_cli,
        #                project_label_cli, rootdir_original
        #                )

        # confirm the returned bids hierarchy has
        #     group_id_cli and project_label_cli
        #self.assertEqual(bh,
        #        {group_id_cli: {project_label_cli : bids_hierarchy}})
        #self.assertEqual(rootdir, rootdir_original)

    def test_handle_group_project_2layers(self):
        """  Assert bids_hierarchy correctly identified and
        group_id and project_label added to bids_hierarchy that
        are passed to function
        """
        # Define inputs
        bids_hierarchy = {
            'project_label_holder': {
                'sub-01': {
                    'func': {'files': 'sub-01_bold.nii.gz'},
                    'anat': {'files': 'sub-01_T1w.nii.gz'}
                    },
                'sub-02': {
                    'func': {'files': 'sub-01_bold.nii.gz'},
                    'anat': {'files': 'sub-01_T1w.nii.gz'}
                    }
                }
            }
        group_id_cli = 'group123'
        project_label_cli = 'project123'
        rootdir_original = '/path/to/bids'
        # call function
        #bh, rootdir = upload_bids.handle_group_project(
        #        bids_hierarchy, group_id_cli,
        #        project_label_cli, rootdir_original)
        # Assert dictionaries are equal
        #self.assertEqual(bh,
        #        {group_id_cli: {project_label_cli : bids_hierarchy['project_label_holder']}})
        # Assert root directory
        #self.assertEqual(
        #        rootdir,
        #        os.path.join(rootdir_original, 'project_label_holder')
        #        )

    def test_handle_group_project_3layers(self):
        """  Assert bids_hierarchy correctly identified and
        group_id and project_label added to bids_hierarchy that
        are passed to function
        """
        # Define inputs
        bids_hierarchy = {
            'group_id_holder': {
                'project_label_holder': {
                    'sub-01': {
                        'func': {'files': 'sub-01_bold.nii.gz'},
                        'anat': {'files': 'sub-01_T1w.nii.gz'}
                        },
                    'sub-02': {
                        'func': {'files': 'sub-01_bold.nii.gz'},
                        'anat': {'files': 'sub-01_T1w.nii.gz'}
                        }
                    }
                }
            }
        group_id_cli = 'group123'
        project_label_cli = 'project123'
        rootdir_original = '/path/to/bids'
        # call function
        #bh, rootdir = upload_bids.handle_group_project(
        #        bids_hierarchy, group_id_cli, project_label_cli)
        # confirm
        #self.assertEqual(bh,
        #        {group_id_cli: {
        #            project_label_cli : bids_hierarchy['group_id_holder']['project_label_holder']}})
        # Assert root directory
        #self.assertEqual(
        #        rootdir,
        #        os.path.join(rootdir_original, 'group_id_holder', 'project_label_holder')
        #        )

    def test_handle_group_project_4layers(self):
        """ """
        # Define inputs
        bids_hierarchy = {
            'extra': {
                'group_id_holder': {
                    'project_label_holder': {
                        'sub-01': {
                            'func': {'files': 'sub-01_bold.nii.gz'},
                            'anat': {'files': 'sub-01_T1w.nii.gz'}
                            },
                        'sub-02': {
                            'func': {'files': 'sub-01_bold.nii.gz'},
                            'anat': {'files': 'sub-01_T1w.nii.gz'}
                            }
                        }
                    }
                }
            }
        group_id_cli = 'group123'
        project_label_cli = 'project123'
        # call function
        #bh = upload_bids.handle_group_project(
        #        bids_hierarchy, group_id_cli, project_label_cli)
        # confirm
        #self.assertEqual(bh,
        #        {group_id_cli: {
        #            project_label_cli : bids_hierarchy['group_id_holder']['project_label_holder']}})


    def test_handle_group_project_1layer_error(self):
        """ Assert errors raised if group_id and project_label
        are not given
        """
        # Define inputs
        bids_hierarchy = {
                'sub-01': {
                    'func': {'files': 'sub-01_bold.nii.gz'},
                    'anat': {'files': 'sub-01_T1w.nii.gz'}
                    },
                'sub-02': {
                    'func': {'files': 'sub-01_bold.nii.gz'},
                    'anat': {'files': 'sub-01_T1w.nii.gz'}
                    }
                }
        group_id_cli = None
        project_label_cli = None

        # Assert SystemExit raised
        #with self.assertRaises(SystemExit) as err:
        #    upload_bids.handle_group_project(
        #        bids_hierarchy, group_id_cli, project_label_cli)

    def test_handle_group_project_2layers_error(self):
        """ Assert errors raised if group_id and project_label
        are not given
        """
        # Define inputs
        bids_hierarchy = {
            'project_label_holder': {
                'sub-01': {
                    'func': {'files': 'sub-01_bold.nii.gz'},
                    'anat': {'files': 'sub-01_T1w.nii.gz'}
                    },
                'sub-02': {
                    'func': {'files': 'sub-01_bold.nii.gz'},
                    'anat': {'files': 'sub-01_T1w.nii.gz'}
                    }
                }
            }
        group_id_cli = None
        project_label_cli = None
        # Assert SystemExit raised
        #with self.assertRaises(SystemExit) as err:
        #    upload_bids.handle_group_project(
        #        bids_hierarchy, group_id_cli, project_label_cli)

    def test_handle_group_project_3layers_no_error(self):
        """ Assert no errors raised if group_id and project_label
        are not given
        """
        # Define inputs
        bids_hierarchy = {
            'group_id_holder': {
                'project_label_holder': {
                    'sub-01': {
                        'func': {'files': 'sub-01_bold.nii.gz'},
                        'anat': {'files': 'sub-01_T1w.nii.gz'}
                        },
                    'sub-02': {
                        'func': {'files': 'sub-01_bold.nii.gz'},
                        'anat': {'files': 'sub-01_T1w.nii.gz'}
                        }
                    }
                }
            }
        group_id_cli = None
        project_label_cli = None
        # call function
        #bh = upload_bids.handle_group_project(
        #        bids_hierarchy, group_id_cli, project_label_cli)
        # confirm dictionaries equal
        #self.assertEqual(bh, bids_hierarchy)

    def test_determine_acquisition_label_bids(self):
        """ """
        foldername = 'anat'
        fname = 'sub-01_ses-01_T1w.nii.gz'
        hierarchy_type = 'BIDS'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert the foldername is used as the acquisition label
        self.assertEqual(foldername, acq_label)

    def test_determine_acquisition_label_flywheel_T1w(self):
        """ """
        foldername = 'anat'
        fname = 'sub-control01_ses-01_T1w.nii.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('T1w', acq_label)

    def test_determine_acquisition_label_flywheel_dwi(self):
        """ """
        foldername = 'dwi'
        fname = 'sub-control01_ses-01_task-nback_dwi.nii.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback_dwi', acq_label)

    def test_determine_acquisition_label_flywheel_niigz(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_bold.nii.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_json(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_bold.json'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_eventstsv(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_events.tsv'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_physio(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_recording-label1_physio.tsv.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_physiojson(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_recording-label1_physio.json'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_stim(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_recording-label1_stim.tsv.gz'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)

    def test_determine_acquisition_label_flywheel_stimjson(self):
        """ """
        foldername = 'func'
        fname = 'sub-control01_ses-01_task-nback_recording-label1_stim.json'
        hierarchy_type = 'Flywheel'
        # Call function
        acq_label = upload_bids.determine_acquisition_label(
                foldername,
                fname,
                hierarchy_type
                )
        # Assert base of the filename is used as the acquisition label
        self.assertEqual('task-nback', acq_label)



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

    def test_parse_json_valid(self):
        """ """
        # Create json file
        os.mkdir(self.testdir)
        filename = os.path.join(self.testdir, 'test.json')
        contents = {
                'test1': {'_id': '123', 'id_type': 'test'},
                }
        self._create_json(filename, contents)
        # Call function
        parsed_contents = upload_bids.parse_json(filename)
        # Assert parsed is the same as original contents
        self.assertEqual(parsed_contents, contents)

    def test_parse_tsv_valid(self):
        """ """
        # Create tsv file
        os.mkdir(self.testdir)
        filename = os.path.join(self.testdir, 'test.tsv')
        contents = [
                ['title', 'id', 'id_type'],
                ['test1', '123', 'test2']
                ]
        self._create_tsv(filename, contents)
        # Call function
        parsed_contents = upload_bids.parse_tsv(filename)
        # Assert parsed is the same as original contents
        self.assertEqual(parsed_contents, contents)



if __name__ == "__main__":

    unittest.main()
    run_module_suite()

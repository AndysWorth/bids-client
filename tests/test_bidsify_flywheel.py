import os
import shutil
import unittest
import jsonschema

import flywheel

from supporting_files import bidsify_flywheel

class BidsifyTestCases(unittest.TestCase):

    def setUp(self):
        # Define testdir
        self.testdir = 'testdir'
        self.maxDiff = None

    def tearDown(self):
        # Cleanup 'testdir', if present
        if os.path.exists(self.testdir):
            shutil.rmtree(self.testdir)

    def test_project_by_label_invalidproject(self):
        """ Get project that does not exist. Assert function returns None.

        NOTE: the environment variable $APIKEY needs to be defined with users API key
        """
        client = flywheel.Flywheel(os.environ['APIKEY'])
        label = 'doesnotexistdoesnotexistdoesnotexist89479587349'
        project = bidsify_flywheel.get_project_by_label(client, label)
        self.assertEqual(project, [])

    def test_project_by_label_validproject(self):
        """ Get project that DOES exist. Assert function returns the project.

        NOTE: the environment variable $APIKEY needs to be defined with users API key

        """
        client = flywheel.Flywheel(os.environ['APIKEY'])
        label = 'Project Name'
        project = bidsify_flywheel.get_project_by_label(client, label)
        project_expected = {u'group': u'adni', u'created': u'2016-10-31T14:53:07.378Z',
                u'modified': u'2017-06-30T16:26:45.731Z', u'label': u'Project Name',
                u'_id': u'58175ad3de26e00012c69306',
                u'permissions': [{u'access': u'admin',
                    u'_id': u'jenniferreiter@invenshure.com'}]}
        self.assertEqual(project[0], project_expected)

    def test_valid_namespace_valid(self):
        """ Assert function does not raise error when a VALID namespace passed """
        from supporting_files.templates import namespace
        bidsify_flywheel.valid_namespace(namespace)

    def test_valid_namespace_invalid1(self):
        """ Assert function returns False when a INVALID namespace passed.

        Namespace is invalid because 'namespace' key should have a string but it's value is 0

        """

        invalid_namespace = {
            "namespace": 0,
            "description": "Namespace for BIDS info objects in Flywheel",
            "datatypes": [
                {
                    "container_type": "file",
                    "description": "BIDS template for diffusion files",
                    "where": {
                        "type": "nifti",
                        },
                    "properties": {
                        "Task": {"type": "string", "label": "Task Label", "default": ""}
                        },
                    "required": ["Task"]
                    }
                ]
            }

        # Assert ValidationError raised
        with self.assertRaises(jsonschema.ValidationError) as err:
            bidsify_flywheel.valid_namespace(invalid_namespace)

    def test_valid_namespace_invalid2(self):
        """ Assert function returns False when a INVALID namespace passed.

        Namespace is invalid because it does not contain the property 'container_type'

        """
        invalid_namespace = {
            "namespace": "BIDS",
            "description": "Namespace for BIDS info objects in Flywheel",
            "datatypes": [
                {
                    "description": "BIDS template for diffusion files",
                    "where": {
                        "type": "nifti"
                        },
                    "properties": {
                        "Task": {"type": "string", "label": "Task Label", "default": ""}
                        }
                    }
                ]
            }

        # Assert ValidationError raised
        with self.assertRaises(jsonschema.ValidationError) as err:
            bidsify_flywheel.valid_namespace(invalid_namespace)

    def test_process_string_template_required(self):
        """  """
        # Define project template from the templates file
        auto_update_str = 'sub-<subject.code>_ses-<session.label>_bold.nii.gz'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': u'00123'},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = bidsify_flywheel.process_string_template(auto_update_str, context)

        self.assertEqual(updated_string,
                'sub-%s_ses-%s_bold.nii.gz' % (
                    context['subject']['code'],
                    context['session']['label'],
                    ))

    def test_process_string_template_bids1(self):
        """  """
        # Get project template from the templates file
        auto_update_str = 'sub-<subject.code>_ses-<session.label>_bold.nii.gz'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': u'sub-01'},
            'session': {u'label': u'ses-001'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = bidsify_flywheel.process_string_template(auto_update_str, context)

        self.assertEqual(updated_string,
                '%s_%s_bold.nii.gz' % (
                    context['subject']['code'],
                    context['session']['label']
                    ))

    def test_process_string_template_optional(self):
        """  """
        # Define string to auto update, subject code is optional
        auto_update_str = '[sub-<subject.code>]_ses-<session.label>_acq-<acquisition.label>_bold.nii.gz'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': None},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = bidsify_flywheel.process_string_template(auto_update_str, context)
        # Assert function honors the optional 'sub-<subject.code>'
        self.assertEqual(updated_string,
                '_ses-%s_acq-%s_bold.nii.gz' % (
                    context['session']['label'],
                    context['acquisition']['label']
                    ))

    def test_process_string_template_full_optional(self):
        """ """
        auto_update_str = 'sub-<subject.code>[_ses-<session.label>][_acq-{file.info.BIDS.Acq}][_ce-{file.info.BIDS.Ce}][_rec-{file.info.BIDS.Rec}][_run-{file.info.BIDS.Run}][_mod-{file.info.BIDS.Mod}]'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': u'123'},
            'session': {u'label': u'456'},
            'acquisition': {u'label': u'acq222'},
            'file': {u'measurements': [u'anatomy_t1w']},
            'ext': '.nii.gz'
        }

        # Call function
        updated_string = bidsify_flywheel.process_string_template(auto_update_str, context)
        # Assert function honors the optional labels
        self.assertEqual(updated_string,
                'sub-123_ses-456')

    def test_process_string_template_func_filename1(self):
        """  """
        # Define string to auto update, subject code is optional
        auto_update_str = 'sub-<subject.code>[_ses-<session.label>]_task-{file.info.BIDS.Task}_bold{ext}'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': '001'},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': {'name': 'bold.nii.gz',
                'info': {'BIDS': {'Task': 'test123', 'Modality': 'bold'}}},
            'ext': '.nii.gz'
        }

        # Call function
        updated_string = bidsify_flywheel.process_string_template(auto_update_str, context)
        # Assert string as expected
        self.assertEqual(updated_string,
                'sub-%s_ses-%s_task-%s_%s%s' % (
                    context['subject']['code'],
                    context['session']['label'],
                    context['file']['info']['BIDS']['Task'],
                    context['file']['info']['BIDS']['Modality'],
                    context['ext']
                    ))

    def test_process_string_template_required_notpresent(self):
        """ """
        # TODO: Determine the expected behavior of this...
        # Define string to auto update
        auto_update_str = 'sub-<subject.code>_ses-<session.label>'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = bidsify_flywheel.process_string_template(auto_update_str, context)
        # Assert function honors the optional 'sub-<subject.code>'
        self.assertEqual(updated_string,
                'sub-<subject.code>_ses-%s' % (
                    context['session']['label']
                    ))

    def test_process_string_template_required_None(self):
        """ """
        # TODO: Determine the expected behavior of this...
        # Define string to auto update
        auto_update_str = 'sub-<subject.code>_ses-<session.label>'
        # initialize context object
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': {u'label': u'project123'},
            'subject': {u'code': None},
            'session': {u'label': u'session444'},
            'acquisition': {u'label': u'acq222'},
            'file': None,
            'ext': None
        }

        # Call function
        updated_string = bidsify_flywheel.process_string_template(auto_update_str, context)
        # Assert function honors the optional 'sub-<subject.code>'
        self.assertEqual(updated_string,
                'sub-<subject.code>_ses-%s' % (
                    context['session']['label']
                    ))

    def test_add_properties_valid(self):
        """ """
        properties = {
                "Filename": {"type": "string", "label": "Filename", "default": "",
                    "auto_update": 'sub-<subject.code>_ses-<session.label>[_acq-<acquisition.label>]_T1w{ext}'},
                "Folder": {"type": "string", "label":"Folder", "default": "anat"},
                "Ce": {"type": "string", "label": "CE Label", "default": ""},
                "Rec": {"type": "string", "label": "Rec Label", "default": ""},
                "Run": {"type": "string", "label": "Run Index", "default": ""},
                "Mod": {"type": "string", "label": "Mod Label", "default": ""},
                "Modality": {"type": "string", "label": "Modality Label", "default": "T1w",
                    "enum": [
                        "T1w","T2w","T1rho","T1map","T2map","FLAIR","FLASH","PD","PDmap",
                        "PDT2","inplaneT1","inplaneT2","angio","defacemask","SWImagandphase"
                        ]
                    }
                }
        project_obj = {u'label': u'Project Name'}
        # Call function
        info_obj = bidsify_flywheel.add_properties(properties, project_obj, [u'anatomy_t1w'])
        # Expected info object
        for key in properties:
            project_obj[key] = properties[key]['default']
        self.assertEqual(info_obj, project_obj)

    def test_update_properties_valid(self):
        """ """
        # Define inputs
        properties = {
            "Filename": {"type": "string", "label": "Filename", "default": "",
                "auto_update": 'sub-<subject.code>_ses-<session.label>[_acq-<acquisition.label>]_T1w{ext}'},
            "Folder": {"type": "string", "label":"Folder", "default": "anat"},
            "Mod": {"type": "string", "label": "Mod Label", "default": ""},
            "Modality": {"type": "string", "label": "Modality Label", "default": "T1w"}
        }
        context = {
            'container_type': 'file', 'parent_container_type': 'acquisition',
            'project': None, 'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'}, 'acquisition': {u'label': u'acqTEST'},
            'file': {
                u'measurements': [u'anatomy_t1w'],
                u'type': u'nifti'
            },
            'ext': '.nii.gz'
        }
        project_obj = {u'test1': u'123', u'test2': u'456'}
        # Call function
        info_obj = bidsify_flywheel.update_properties(properties, context, project_obj)
        # Update project_obj, as expected
        project_obj['Filename'] = u'sub-%s_ses-%s_acq-%s_T1w%s' % (
                context['subject']['code'],
                context['session']['label'],
                context['acquisition']['label'],
                context['ext']
                )
        self.assertEqual(project_obj, info_obj)

    def test_process_matching_templates_anat_t1w(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'measurements': [u'anatomy_t1w'],
                    u'type': u'nifti'
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Filename': u'sub-001_ses-sestest_T1w.nii.gz',
                    'Path': u'sub-001/ses-sestest/anat', 'Folder': 'anat',
                    'Run': '', 'Acq': '', 'Ce': '', 'Rec': '',
                    'Modality': 'T1w', 'Mod': ''
                    }
                },
            u'measurements': [u'anatomy_t1w'], u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_anat_t2w(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'measurements': [u'anatomy_t2w'],
                    u'type': u'nifti'
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Filename': u'sub-001_ses-sestest_T2w.nii.gz',
                    'Path': u'sub-001/ses-sestest/anat', 'Folder': 'anat',
                    'Run': '', 'Acq': '', 'Ce': '', 'Rec': '',
                    'Modality': 'T2w', 'Mod': ''
                    }
                },
            u'measurements': [u'anatomy_t2w'], u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_func(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'measurements': [u'functional'],
                    u'type': u'nifti',
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Filename': u'sub-001_ses-sestest_task-{file.info.BIDS.Task}_bold.nii.gz',
                    'Folder': 'func', 'Path': u'sub-001/ses-sestest/func',
                    'Acq': '', 'Task': '', 'Modality': 'bold',
                    'Rec': '', 'Run': '', 'Echo': ''
                    }
                },
            u'measurements': [u'functional'], u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_dwi_nifti(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'measurements': [u'diffusion'],
                    u'type': u'nifti'
                        },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Filename': u'sub-001_ses-sestest_dwi.nii.gz',
                    'Path': u'sub-001/ses-sestest/dwi', 'Folder': 'dwi',
                     'Modality': 'dwi', 'Acq': '', 'Run': ''
                    }
                },
            u'measurements': [u'diffusion'], u'type': u'nifti'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_dwi_bval(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'measurements': [u'diffusion'],
                    u'type': u'bval'
                        },
            'ext': '.bval'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Filename': u'sub-001_ses-sestest_dwi.bval',
                    'Path': u'sub-001/ses-sestest/dwi', 'Folder': 'dwi',
                     'Modality': 'dwi', 'Acq': '', 'Run': ''
                    }
                },
            u'measurements': [u'diffusion'], u'type': u'bval'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_dwi_bvec(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'},
            'acquisition': {u'label': u'acqTEST'},
            'file': {u'measurements': [u'diffusion'],
                    u'type': u'bvec'
                        },
            'ext': '.bvec'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Filename': u'sub-001_ses-sestest_dwi.bvec',
                    'Path': u'sub-001/ses-sestest/dwi', 'Folder': 'dwi',
                     'Modality': 'dwi', 'Acq': '', 'Run': ''
                    }
                },
            u'measurements': [u'diffusion'], u'type': u'bvec'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_dicom(self):
        """ Asserts DICOM files are ignored """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': {u'label': 'hello'},
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'},
            'acquisition': {u'label': u'acqTEST'},
            'file': {
                u'measurements': [u'diffusion'],
                u'type': u'dicom'
                },
            'ext': '.dcm.zip'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            u'measurements': [u'diffusion'], u'type': u'dicom'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_session_file(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'session',
            'project': {'label': 'testproject'},
            'subject': {'code': '12345'},
            'session': {'label': 'haha'},
            'acquisition': None,
            'file': {u'type': u'tabular'},
            'ext': '.tsv'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Filename': '', 'Folder': 'ses-haha', 'Path': 'sub-12345/ses-haha'
                    }
                },
            u'type': u'tabular'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_project_file(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'project',
            'project': None,
            'subject': None,
            'session': None,
            'acquisition': None,
            'file': {u'measurements': [u'unknown'],
                    u'type': u'archive'},
            'ext': '.zip'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Filename': '', 'Folder': '', 'Path': ''
                    }
                },
            u'measurements': [u'unknown'], u'type': u'archive'}
        self.assertEqual(container, container_expected)

    def test_process_matching_templates_project_file_multiple_measurements(self):
        """ """
        # Define context
        context = {
            'container_type': 'file',
            'parent_container_type': 'acquisition',
            'project': None,
            'subject': {u'code': u'001'},
            'session': {u'label': u'sesTEST'},
            'acquisition': {u'label': u'acqTEST'},
            'file': {
                u'measurements': [u'anatomy_t1w', u'anatomy_t2w'],
                u'type': u'nifti'
            },
            'ext': '.nii.gz'
        }
        # Call function
        container = bidsify_flywheel.process_matching_templates(context)
        # Define expected container
        container_expected = {
            'info': {
                'BIDS': {
                    'Filename': u'sub-001_ses-sestest_T1w.nii.gz',
                    'Path': u'sub-001/ses-sestest/anat', 'Folder': 'anat',
                    'Run': '', 'Acq': '', 'Ce': '', 'Rec': '',
                    'Modality': 'T1w', 'Mod': ''
                    }
                },
            u'measurements': [u'anatomy_t1w', u'anatomy_t2w'], u'type': u'nifti'}
        print container
        self.assertEqual(container, container_expected)



if __name__ == "__main__":

    unittest.main()
    run_module_suite()

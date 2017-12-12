
project_template = {
    "container_type": "project",
    "description": "BIDS project template",
    "properties": {
        "Name": {"type": "string", "label": "Name", "default": ""},
        "BIDSVersion": {"type": "string", "label": "BIDS Version", "default": ""},
        "License": {"type": "string", "label": "License", "default": ""},
        "Authors": {"type": "string", "label": "Authors", "default": ""},
        "Ackowledgements": {"type": "string", "label": "Acknowledgements", "default": ""},
        "HowToAcknowledge": {"type": "string", "label": "How To Acknowledge", "default": ""},
        "Funding": {"type": "string", "label": "Funding Sources", "default": ""},
        "ReferencesAndLinks": {"type": "string", "label":"Reference and Links", "default": ""},
        "DatasetDOI": {"type": "string", "label": "Dataset DOI", "default": ""}
    }
}

file_template = {
    "container_type": "file",
    "description": "BIDS base file template",
    "not": {
        "type": [u"dicom"],
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": ""},
        "Folder": {"type": "string", "label": "Folder", "default": ""},
        "Path": {"type": "string", "label": "Path", "default": ""}
    },
    "required": ["Filename", "Folder", "Path"]
}

project_file_template = {
    "container_type": "file",
    "parent_container_type": "project",
    "description": "BIDS project file template",
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": ""},
        "Folder": {"type": "string", "label": "Folder", "default": ""},
        "Path": {"type": "string", "label": "Path", "default": ""}
    },
    "required": ["Filename", "Folder", "Path"]
}

session_file_template = {
    "container_type": "file",
    "parent_container_type": "session",
    "description": "BIDS session file template",
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": ""},
        "Folder": {"type": "string", "label": "Folder", "default": "",
            "auto_update": 'ses-<session.label>'},
        "Path": {"type": "string", "label": "Path", "default": "",
            "auto_update": 'sub-<subject.code>/ses-<session.label>'},
    },
    "required": ["Filename", "Folder", "Path"]
}

anat_file_template = {
    "container_type": "file",
    "parent_container_type": "acquisition",
    "description": "BIDS template for anat files",
    "where": {
        "type": [u"nifti"],
        "measurements": [u"anatomy_t1w", u"anatomy_t2w", u"anatomy_t1wrho",
            u"map_t1w", u"map_t2w", u"anatomy_t2star", u"anatomy_flair",
            u"anatomy_flash", u"anatomy_pd", u"map_pd", u"anatomy_pdt2",
            u"anatomy_t1w_inplane", u"anatomy_t2w_inplane", u"angio",
            u"defacemask", u"swi"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update": 'sub-<subject.code>[_ses-<session.label>]_{file.info.BIDS.Modality}{ext}'},
        "Folder": {"type": "string", "label": "Folder", "default": "anat"},
        "Path": {"type": "string", "label": "Path", "default": "",
            "auto_update": 'sub-<subject.code>[/ses-<session.label>]/{file.info.BIDS.Folder}'},
        "Acq": {"type": "string", "label": "Acq Label", "default": ""},
        "Ce": {"type": "string", "label": "Ce Label", "default": ""},
        "Rec": {"type": "string", "label": "Rec Label", "default": ""},
        "Run": {"type": "string", "label": "Run Index", "default": ""},
        "Mod": {"type": "string", "label": "Mod Label", "default": ""},
        "Modality": {"type": "string", "label": "Modality Label", "default": "",
            "enum": [
                "T1w",
                "T2w",
                "T1rho",
                "T1map",
                "T2map",
                "FLAIR",
                "FLASH",
                "PD",
                "PDmap",
                "PDT2",
                "inplaneT1",
                "inplaneT2",
                "angio",
                "defacemask",
                "SWImagandphase"
            ]
        }
    },
    "required": ["Filename", "Folder", "Modality"]
}

func_file_template = {
    "container_type": "file",
    "description": "BIDS template for func files",
    "where": {
        "type": [u"nifti"],
        "measurements": [u"functional"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update": 'sub-<subject.code>[_ses-<session.label>]_task-{file.info.BIDS.Task}_{file.info.BIDS.Modality}{ext}'},
        "Folder": {"type": "string", "label": "Folder", "default": "func"},
        "Path": {"type": "string", "label": "Path", "default": "",
            "auto_update": 'sub-<subject.code>[/ses-<session.label>]/{file.info.BIDS.Folder}'},
        "Acq": {"type": "string", "label": "Acq Label", "default": ""},
        "Task": {"type": "string", "label": "Task Label", "default": ""},
        "Rec": {"type": "string", "label": "Rec Label", "default": ""},
        "Run": {"type": "string", "label": "Run Index", "default": ""},
        "Echo": {"type": "string", "label": "Echo Index", "default": ""},
        "Modality": {"type": "string", "label": "Modality Label", "default": "bold",
            "enum": [
                "bold",
                "sbref",
                "stim",
                "physio"
            ]
        }
    },
    "required": ["Filename", "Folder", "Task", "Modality"]
}

# Matches to functional
task_events_file_template = {
    "container_type": "file",
    "description": "BIDS template for task files",
    "where": {
        "type": [u"tsv"],
        "measurements": [u"functional"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update": 'sub-<subject.code>[_ses-<session.label>]_events.tsv'},
        "Folder": {"type": "string", "label": "Folder", "default": "func"},
        "Path": {"type": "string", "label": "Path", "default": "",
            "auto_update": 'sub-<subject.code>[/ses-<session.label>]/{file.info.BIDS.Folder}'},
        "Task": {"type": "string", "label": "Task Label", "default": ""},
        "Acq": {"type": "string", "label": "Acq Label", "default": ""},
        "Rec": {"type": "string", "label": "Rec Label", "default": ""},
        "Run": {"type": "string", "label": "Run Index", "default": ""},
        "Echo": {"type": "string", "label": "Echo Index", "default": ""},
    },
    "required": ["Filename", "Folder", "Task"]
}

# Matches to functional
physio_events_file_template = {
    "container_type": "file",
    "description": "BIDS template for task files",
    "where": {
        "measurements": [u"physio"] # TODO: determine this... what is the measurement name of physio data?
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update": 'sub-<subject.code>[_ses-<session.label>]_{file.info.BIDS.Modality}{ext}'},
        "Folder": {"type": "string", "label": "Folder", "default": "func"},
        "Path": {"type": "string", "label": "Path", "default": "",
            "auto_update": 'sub-<subject.code>[/ses-<session.label>]/{file.info.BIDS.Folder}'},
        "Task": {"type": "string", "label": "Task Label", "default": ""},
        "Acq": {"type": "string", "label": "Acq Label", "default": ""},
        "Rec": {"type": "string", "label": "Rec Label", "default": ""},
        "Run": {"type": "string", "label": "Run Index", "default": ""},
        "Echo": {"type": "string", "label": "Echo Index", "default": ""},
        "Recording": {"type": "string", "label": "Recording Label", "default": ""},
        "Modality": {"type": "string", "label": "Modality Label", "default": "physio",
            "enum": [
                "physio",
                "stim"
            ]
        }

    },
    "required": ["Filename", "Folder", "Task"]
}

beh_events_file_template = {
    "container_type": "file",
    "description": "BIDS template for task files",
    "where": {
        "measurements": [""] # TODO: determine this... what is the measurement name of behavioral experiments?
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update": 'sub-<subject.code>[_ses-<session.label>]_{file.info.BIDS.Modality}{ext}'},
        "Folder": {"type": "string", "label": "Folder", "default": "beh"},
        "Path": {"type": "string", "label": "Path", "default": "",
            "auto_update": 'sub-<subject.code>[/ses-<session.label>]/{file.info.BIDS.Folder}'},
        "Task": {"type": "string", "label": "Task Label", "default": ""},
        "Acq": {"type": "string", "label": "Acq Label", "default": ""},
        "Modality": {"type": "string", "label": "Modality Label", "default": "beh",
            "enum": [
                "beh",
                "events",
                "physio",
                "stim"
            ]
        }

    },
    "required": ["Filename", "Folder", "Task"]
}


diffusion_file_template = {
    "container_type": "file",
    "description": "BIDS template for diffusion files",
    "where": {
        "type": [u"nifti", u"bvec", u"bval"],
        "measurements": [u"diffusion"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update":'sub-<subject.code>[_ses-<session.label>]_{file.info.BIDS.Modality}{ext}'},
        "Folder": {"type": "string", "label": "Folder", "default": "dwi"},
        "Path": {"type": "string", "label": "Path", "default": "",
            "auto_update": 'sub-<subject.code>[/ses-<session.label>]/{file.info.BIDS.Folder}'},
        "Acq": {"type": "string", "label": "Acq Label", "default": ""},
        "Run": {"type": "string", "label": "Run Index", "default": ""},
        "Modality": {"type": "string", "label": "Modality Label", "default": "dwi",
            "enum": [
                "dwi",
                "sbref"
            ]
        }
    },
    "required": []
}

fieldmap_file_template = {
    "container_type": "file",
    "description": "BIDS template for field map files",
    "where": {
        "type": [u"nifti"],
        "measurements": [u"field_map"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update":'sub-<subject.code>[_ses-<session.label>]_{file.info.BIDS.Modality}{ext}'},
        "Folder": {"type": "string", "label": "Folder", "default": "fmap"},
        "Path": {"type": "string", "label": "Path", "default": "",
            "auto_update": 'sub-<subject.code>[/ses-<session.label>]/{file.info.BIDS.Folder}'},
        "Acq": {"type": "string", "label": "Acq Label", "default": ""},
        "Run": {"type": "string", "label": "Run Index", "default": ""},
        "Dir": {"type": "string", "label": "Dir Label", "default": ""}, # TODO: This is only required for 'epi' fieldmap
        "Modality": {"type": "string", "label": "Modality Label", "default": "fieldmap",
            "enum": [
                "phasediff",
                "magnitude1",
                "magnitude2",
                "phase1",
                "phase2",
                "magnitude",
                "fieldmap",
                "epi"
                ]
        }
    },
    "required": ["Modality"]
}

namespace = {
    "namespace": "BIDS",
    "description": "Namespace for BIDS info objects in Flywheel",
    "datatypes": [
        project_template,
        file_template,
        project_file_template,
        session_file_template,
        anat_file_template,
        func_file_template,
        task_events_file_template,
        diffusion_file_template,
        fieldmap_file_template
    ]
}


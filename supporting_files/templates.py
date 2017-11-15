
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
        "ReferencesAndLinks": {"type": "string", "label":"Reference snd Links", "default": ""},
        "DatasetDOI": {"type": "string", "label": "Dataset DOI", "default": ""}
    }
}

file_template = {
    "container_type": "file",
    "description": "BIDS base file template",
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": ""},
        "Folder": {"type": "string", "label": "Folder", "default": ""}
    },
    "required": ["Filename", "Folder"]
}

anat_file_template = {
    "container_type": "file",
    "parent_container_type": "acquisition",
    "description": "BIDS template for anat files",
    "where": {
        "type": "nifti",
        "measurements": ["anatomy_t1w"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update": 'sub-<subject.code>[_ses-<session.label>][_acq-<acquisition.label>]_T1w{ext}'},
        "Folder": {"type": "string", "label":"Folder", "default": "anat"},
        "Ce": {"type": "string", "label": "CE Label", "default": ""},
        "Rec": {"type": "string", "label": "Rec Label", "default": ""},
        "Run": {"type": "string", "label": "Run Index", "default": ""},
        "Mod": {"type": "string", "label": "Mod Label", "default": ""},
        "Modality": {"type": "string", "label": "Modality Label", "default": "T1w",
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
    "required": ["Modality"]
}

func_file_template = {
    "container_type": "file",
    "description": "BIDS template for func files",
    "where": {
        "type": "nifti",
        "measurements": ["functional"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update": 'sub-<subject.code>[_ses-<session.label>][_acq-<acquisition.label>]_bold{ext}'},
        "Folder": {"type": "string", "label": "Folder", "default": "func"},
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
    "required": ["Task", "Modality"]
}

task_events_file_template = {
    "container_type": "file",
    "description": "BIDS template for task files",
    "where": {
        "type": "tsv",
        "measurements": ["functional"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update": 'sub-<subject.code>[_ses-<session.label>][_acq-<acquisition.label>]_events.tsv'},
        "Folder": {"type": "string", "label": "Folder", "default": "func"},
        "Task": {"type": "string", "label": "Task Label", "default": ""}
    },
    "required": ["Task"]
}


diffusion_file_template = {
    "container_type": "file",
    "description": "BIDS template for diffusion files",
    "where": {
        "type": "nifti",
        "measurements": ["diffusion"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update":'sub-<subject.code>[_ses-<session.label>][_acq-<acquisition.label>]_dwi{ext}'},
        "Folder": {"type": "string", "label": "Folder", "default": "dwi"},
        "Run": {"type": "string", "label": "Run Index", "default": ""}
    },
    "required": ["Task"]
}

fieldmap_file_template = {
    "container_type": "file",
    "description": "BIDS template for field map files",
    "where": {
        "type": "nifti",
        "measurements": ["field_map"]
    },
    "properties": {
        "Filename": {"type": "string", "label": "Filename", "default": "",
            "auto_update":'sub-<subject.code>[_ses-<session.label>][_acq-<acquisition.label>]_phase{ext}'},
        "Folder": {"type": "string", "label": "Folder", "default": "fmap"},
        "Run": {"type": "string", "label": "Run Index", "default": ""},
        "Dir": {"type": "string", "label": "Dir Label", "default": ""},
        "Modality": {"type": "string", "label": "Modality Label", "default": "",
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

    },
    "required": ["Modality"]
}
}



namespace = {
    "namespace": "BIDS",
    "description": "Namespace for BIDS info objects in Flywheel",
    "datatypes": [
        project_template,
        file_template,
        anat_file_template,
        func_file_template,
        task_events_file_template,
        diffusion_file_template,
        fieldmap_file_template
    ]
}




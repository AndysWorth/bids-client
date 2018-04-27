classifications = {
        'anat': {
            'T1w': {'Contrast': 'T1', 'Intent':'Structural'},
            'T2w': {'Contrast': 'T2', 'Intent':'Structural'},
            'T1rho': {'Custom': 'T1rho'},
            'T1map': {'Contrast': 'T1', 'Intent':'Structural', 'Features': 'Quantitative'},
            'T2map': {'Contrast': 'T2', 'Intent':'Structural', 'Features': 'Quantitative'},
            'T2star': {'Contrast': 'T2*', 'Intent':'Structural'},
            'FLAIR': {'Custom': 'FLAIR'},
            'FLASH': {'Custom': 'FLASH'},
            'PD': {'Contrast': 'PD', 'Intent':'Structural'},
            'PDmap': {'Custom': 'PD-Map'},
            'PDT2': {'Contrast': ['PD', 'T2'], 'Intent':'Structural'},
            'inplaneT1': {'Contrast': 'T1', 'Intent':'Structural', 'Features': 'In-Plane'},
            'inplaneT2': {'Contrast': 'T2', 'Intent':'Structural', 'Features': 'In-Plane'},
            'angio': {'Custom': 'Angio'},
            'defacemask': {'Custom': 'Defacemask'},
            'SWImagandphase': {'Custom': 'SWI'},
        },
        'func': {
            'bold': {'Intent': 'Functional'},
            'events': {'Intent': 'Functional'},
            'sbref': {'Intent': 'Functional'},
            'stim': {'Intent': 'Functional', 'Custom': 'Stim'},         # stimulus
            'physio': {'Intent': 'Functional', 'Custom': 'Physio'},     # physio
        },
        'beh' : {
            'events': {'Custom': 'Behavioral'},
            'stim': {'Custom': 'Stim'},    # stimulus
            'physio': {'Custom': 'Physio'}     # physio
        },
        'dwi' : {
            'dwi': {'Contrast': 'Diffusion', 'Intent':'Structural'},
            'sbref': {'Contrast': 'Diffusion', 'Intent':'Structural'}
        },
        'fmap': {
            'phasediff': {'Contrast': 'B0', 'Intent': 'Fieldmap'},
            'magnitude1': {'Contrast': 'B0', 'Intent': 'Fieldmap'},
            'magnitude2': {'Contrast': 'B0', 'Intent': 'Fieldmap'},
            'phase1': {'Contrast': 'B0', 'Intent': 'Fieldmap'},
            'phase2': {'Contrast': 'B0', 'Intent': 'Fieldmap'},
            'magnitude': {'Contrast': 'B0', 'Intent': 'Fieldmap'},
            'fieldmap': {'Contrast': 'B0', 'Intent': 'Fieldmap'},
            'epi': {'Contrast': 'B0', 'Intent': 'Fieldmap'},
        }
    }


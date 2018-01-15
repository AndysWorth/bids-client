classifications = {
        'anat': {
            'T1w': 'anatomy_t1w',
            'T2w': 'anatomy_t2w',
            'T1rho': 'anatomy_t1wrho',
            'T1map': 'map_t1w',
            'T2map': 'map_t2w',
            'T2star': 'anatomy_t2star',
            'FLAIR': 'anatomy_flair',
            'FLASH': 'anatomy_flash',
            'PD': 'anatomy_pd',
            'PDmap': 'map_pd',
            'PDT2': 'anatomy_pdt2',
            'inplaneT1': 'anatomy_t1w_inplane',
            'inplaneT2': 'anatomy_t2w_inplane',
            'angio': 'angio',
            'defacemask': 'defacemask',
            'SWImagandphase': 'swi'
        },
        'func': {
            'bold': 'functional',
            'events': 'functional',
            'sbref': 'functional',
            'stim': 'stimulus',    # stimulus
            'physio': 'physio'     # physio
        },
        'beh' : {
            'events': 'behavioral',
            'stim': 'stimulus',    # stimulus
            'physio': 'physio'     # physio
        },
        'dwi' : {
            'dwi': 'diffusion',
            'sbref': 'diffusion'
        },
        'fmap': {
            'phasediff': 'field_map',
            'magnitude1': 'field_map',
            'magnitude2': 'field_map',
            'phase1': 'field_map',
            'phase2': 'field_map',
            'magnitude': 'field_map',
            'fieldmap': 'field_map',
            'epi': 'field_map'
        }
    }


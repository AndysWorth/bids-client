import json, sys

functional_acq_format_options = {
	2 : {
		"id": "func_file",
		"template": "func_file",
		"where": {
			"container_type": "file",
			"file.type": {
				"$in": ["nifti", "NIfTI"]
			},
			"acquisition.label": {
				"$in": []
			}
		},
		"initialize" : {
			"Task": {
				"acquisition.label": {
					"$regex": "(^|_)(?P<value>[^-_]+)"
				}
			},
			"Run": {
				"acquisition.label": {
					"$regex": [
						"(^|_)run-(?P<value>\\d+)",
						"(^|_)run(?P<value>[=+])"
					]
				},
				"$run_counter": {
					"key": "functional.{file.info.BIDS.Task}"
				}
			}
		}
	}
}

topup_format_options = {
	'noPart' : {
		1 : {
			"id": "fieldmap_phase_encoded_file",
			"template": "fieldmap_phase_encoded_file",
			"where": {
				"container_type": "file",
				"file.type": {
					"$in": ["nifti", "NIfTI"]
				},
				"file.measurements": {
					"$in": ["field_map"]
				},
				"acquisition.label": {
					"$regex": "[Tt]opup"
				}
			},
			"initialize": {
				"Dir": {
					"$comment": "Currently matching bipedal orientations",
					"acquisition.label": {
						"$regex": "([^a-zA-Z0-9]|^)(?P<value>[aprlhfAPRLHF]{2})([^a-zA-Z0-9]|$)"
					}
				},
				"Run": {
					"acquisition.label": {
						"$regex": [
							"(^|_)run-(?P<value>\\d+)",
							"(^|_)run(?P<value>[=+])"
						]
					},
					"$run_counter": {
						"key": "field_map.{file.info.BIDS.Dir}"
					}
				}
			}
		},
		3 : {
			"id": "fieldmap_phase_encoded_file",
			"template": "fieldmap_phase_encoded_file",
			"where": {
				"container_type": "file",
				"file.type": {
					"$in": ["nifti", "NIfTI"]
				},
				"file.measurements": {
					"$in": ["field_map"]
				},
				"acquisition.label": {
					"$regex": "(^|_)dir-(?P<value>[aprlhfAPRLHF]{2})"
				}
			},
			"initialize": {
				"Dir": {
					"$comment": "Currently matching bipedal orientations",
					"acquisition.label": {
						"$regex": "([^a-zA-Z0-9]|^)(?P<value>[aprlhfAPRLHF]{2})([^a-zA-Z0-9]|$)"
					}
				},
				"Run": {
					"acquisition.label": {
						"$regex": [
							"(^|_)run-(?P<value>\\d+)",
							"(^|_)run(?P<value>[=+])"
						]
					},
					"$run_counter": {
						"key": "field_map.{file.info.BIDS.Dir}"
					}
				}
			}
		}
	},
	'part': {

	}
}





def interact(project):
	topup_format = None
	data = {
		"extends": "bids-v1",
		"description": "Additional rules for matching data",
		"exclude_rules": [],
		"definitions": {},
		"rules": [],
		"initializers": []
	}
	data['exclude_rules'].append('bids_fieldmap_phase_encoded_file')

	# Exclude session label if it is not a longitudinal study
	longitudinal = raw_input("Is the study longitudinal/would you like session folders? (y/n):\n") in 'yY'
	if not longitudinal:
		data['definitions']['session'] = {
			"description": "BIDS session template",
			"properties": {
				"Label": {"type": "string", "title": "Label", "default": ""}
			},
			"required": []
		}

	# Allows for more accurate matching of tasks and functional data types
	tasks = [task.strip() for task in raw_input('Please enter comma seperated list of tasks (Leave empty if you do not know):\n').split(',')]
	format_task = [task.strip() for task in raw_input('Please enter comma seperated list of any non-alphanumeric characters that are in any of the task names(Leave empty if you do not know):\n').split(',')]
	functional_acq_format = int(raw_input('How will the acquisition labels for functionals look like:\n\
			1. [func_]task-{TaskName}_run+ (Recommended)\n\
			2. [func_]{TaskName}_run+ \n\
			3. [func_]{TaskName}_{RunNumber}\n'))

	# Different ways t match topups
	# TODO: add in customization for part/modality: (phase|mag)/(bold|sbref)
	fieldmaps = raw_input('Will there be fieldmaps? (y/n):\n') in 'yY'
	if fieldmaps:
		fieldmaps = raw_input('Will there be topups? (y/n):\n') in 'yY'
		if fieldmaps:
			topup_format = int(raw_input('How will the acquisition labels for topups look like:\n\
						1. {Stuff}_topup_{Dir} (Recommended)\n\
						2. Topup_{Stuff}_{Dir} \n\
						3. {Stuff}_dir-{Dir} (Not Recommended)\n')
			)
			# part = raw_input('Will you be including both phase and magnitude fieldmaps')

	# Generate the template using predefined json objects per answer
	if tasks:
		data['exclude_rules'].append('bids_func_file')
		rule = functional_acq_format_options[2]
		rule["where"]["acquisition.label"]["$in"] = tasks
		rule['initialize']['Task']['acquisition.label']['$regex'] = ["(?P<value>{})".format(item) for item in tasks]
		data['rules'].append(rule)
	elif functional_acq_format > 1:
		data['initializers'].append[{
			'rule': 'bids_func_file',
			'initialize': functional_acq_format_options[2]['initialize']
		}]
	if topup_format:
		rule = topup_format_options[1 if topup_format <= 2 else 2]
		data['rules'].append(rule)

	# Remove unused keys
	for key in data.keys():
		if not data.get(key, True):
			data.pop(key)

	with open('{}-project-template.json'.format(project), 'w+') as fil:
		json.dump(data, fil, indent=4, sort_keys=True)

if __name__ == '__main__':
	try:
		interact(sys.argv[1])
	except IndexError:
		print "USAGE: python {} projectName".format(sys.argv[0])
		sys.exit(1)

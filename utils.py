import os
from shutil import copyfile

assets_dir = os.path.expanduser(
    "~/next_step_assets")
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)


def push_new_asset(filepath, filename,  delete_orig_file=False):
    # Find filenames matching the pattern
    file_numbers = []
    for f in os.listdir(assets_dir):
        file_numbers.append(int(f.split("-")[0]))

    # Print the maximum number, handling the empty list case
    if file_numbers:
        max_number = max(file_numbers)
    else:
        max_number = 0
    copyfile(filepath, os.path.join(
        assets_dir, f"{max_number + 1}-{filename}"))

    """ assets_json_filepath  = os.path.expanduser('~/next_step_assets.json')		
	if not os.path.exists(assets_json_filepath):
		with open(assets_json_filepath, "w") as f:
			json.dump({}, f)
	else:
		with open(assets_json_filepath, "r+") as f:  # Open for reading and writing
			data = json.load(f)  # Load the existing data
			data[max_number+ 1] = description
			f.seek(0)  # Reset file pointer to beginning
			json.dump(data, f, indent=4)  # Re-dump the data, potentially with formatting """
    if delete_orig_file:
        os.remove(filepath)
    return max_number + 1

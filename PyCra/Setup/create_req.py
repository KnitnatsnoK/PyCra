import os
import requests

def get_latest_pygame_ce_version():
    url = "https://pypi.org/pypi/pygame-ce/json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        latest_version = data['info']['version']
        return latest_version
    else:
        print("Failed to fetch version information.")
        return None

# Get the latest version of pygame-ce
latest_pygame_ce_version = get_latest_pygame_ce_version()
if latest_pygame_ce_version:
    print(f"The latest version of pygame-ce is: {latest_pygame_ce_version}")

# Generate requirements.txt
os.system('pipreqs "Scripts" --savepath "Setup\\requirements.txt" --force')

requirements_file_path = "Setup/requirements.txt"
# Read the existing requirements
with open(requirements_file_path, "r") as file:
    lines = file.readlines()

# Create a new list to hold modified lines
new_lines = []

for line in lines:
    if "pygame" in line:
        # Replace the whole line with pygame-ce
        new_lines.append(f"pygame-ce=={latest_pygame_ce_version}\n")  # Adjust this line if you want a specific version
    else:
        new_lines.append(line)

# Write the modified lines back to the requirements.txt
with open(requirements_file_path, "w") as file:
    file.writelines(new_lines)

print(f"Updated {requirements_file_path} to replace pygame with pygame-ce.")

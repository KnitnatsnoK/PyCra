import subprocess
import sys

def install_requirements(requirements_file="Setup\\requirements.txt"):
    try:
        # Run the command to install the packages
        #subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade-strategy", "only-if-needed", "-r", requirements_file])
        print(f"All modules from {requirements_file} are successfully installed!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the installation: {e}")
    except FileNotFoundError:
        print(f"File {requirements_file} not found!")

if __name__ == "__main__":
    install_requirements()  # or specify a different file, e.g. install_requirements("path/to/your/requirements.txt")

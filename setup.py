import os
from distutils.text_file import TextFile
from setuptools import setup, find_packages
from pathlib import Path
from importlib import import_module


def _parse_requirements(filename):
    """Return requirements from requirements file."""
    setup_path = Path(__file__).resolve().parent.joinpath(filename)
    requirements = TextFile(filename=str(setup_path)).readlines()
    return [p for p in requirements if "-r" not in p]


NAME = 'health_sensor_simulator'
SHORT_DESCRIPTION = "Health variables sensor simulator with rest API and anomaly detection model"
URL = "https://github.com/marcoom/health-sensor-simulator"
AUTHOR = 'Marco Mongi'
EMAIL = 'marco.mongi@example.com'

try:
    VERSION = import_module(NAME+".app.version").__version__
except Exception as e:
    print("Version information cannot be imported using "
          f"'importlib.import_module' due to {e}.")
    about = dict()
    version_path = Path(__file__).resolve().parent.joinpath(NAME, "app",
                                                            "version.py")
    exec(version_path.read_text(), about)
    VERSION = about["__version__"]

try:
    # Load README as description of package
    with open('README.md', encoding="utf-8") as readme_file:
        LONG_DESCRIPTION = readme_file.read()
except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION

# Requirements
INSTALL_REQUIRED = _parse_requirements(os.path.join("requirements", "base.txt"))
# Optional requirements
DEV_REQUIRED = _parse_requirements(os.path.join("requirements", "dev.txt"))
DOC_REQUIRED = _parse_requirements(os.path.join("requirements", "doc.txt"))

# What packages are optional?
EXTRAS = {"doc": DOC_REQUIRED}


setup(name=NAME,
      version=VERSION,
      author=AUTHOR,
      author_email=EMAIL,
      description=SHORT_DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      url=URL,
      packages=find_packages(include=["health_sensor_simulator*"],
                             exclude=["tests*", "scripts*", "docs*"]),
      package_data={NAME: ["data/*", ], },
      install_requires=INSTALL_REQUIRED,
      test_requires=DEV_REQUIRED,
      extras_require=EXTRAS,
      setup_requires=['wheel'])

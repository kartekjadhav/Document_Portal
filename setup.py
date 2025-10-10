from setuptools import setup, find_packages

setup(
    name="Document_Portal",
    packages=find_packages(),
    version="0.1.0",
    author="Kartek Jadhav"
)


# Without it: You'd need to manually copy files or manipulate sys.path to use your code across projects.
# With it: Your project becomes a proper Python package that can be installed and imported like any other library (e.g., import document_portal).
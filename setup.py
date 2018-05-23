from setuptools import setup, find_packages


setup(
    name='twnorm',
    version='0.1',
    description='Spanish Tweet Normalizer',
    author='Alan Bracco',
    author_email='alan.bracco@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['twnorm=twnorm.start_process:start_process',
                            'evalnorm=twnorm.eval:evaluate'],
    }
)

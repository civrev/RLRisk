from setuptools import setup, find_packages

setup(
    name = 'rlrisk',
    version = '1.0.1',
    description = 'A reinforcement learning environment based off the board game Risk',
    long_description = open('README.rst').read(),
    author = 'Christian Watts',
    author_email = 'civrev@gmail.com',
    license = '',
    url='https://github.com/civrev/rlrisk',
    packages = ['rlrisk',
                'rlrisk.agents',
                'rlrisk.minigames',
                'rlrisk.environment'],
    package_data={'rlrisk': ['environment/*.bmp','*.txt','*.rst']},
    python_requires='~=3.3',
    install_requires = [
        'numpy>=1.14.1',
        'pygame>=1.9.3']
)

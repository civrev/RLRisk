from setuptools import setup, find_packages

setup(
    name = 'rlrisk',
    version = '0.9.4',
    description = 'A reinforcement learning environment based off the board game Risk',
    author = 'Christian Watts',
    author_email = 'civrev@gmail.com',
    license = '',
    url='https://github.com/civrev/rlrisk',
    packages = find_packages(),
    package_data={'rlrisk': ['environment/*.bmp']},
    install_requires = [
        'numpy>=1.14.1',
        'pygame>=1.9.3']
)

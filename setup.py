#https://github.com/civrev/rlrisk

from setuptools import setup

setup(
    name = 'rlrisk',
    version = '0.3',
    description = 'A reinforcement learning environment based off the board game Risk',
    author = 'Christian Watts',
    author_email = 'civrev@gmail.com',
    license = '',
    url='https://github.com/civrev/rlrisk',
    packages = [
        'rlrisk',
        'rlrisk.environment',
        'rlrisk.agents',
        'rlrisk.minigames'
        ],
    install_requires = [
        'numpy>=1.14.1',
        'pygame>=1.9.3']
)

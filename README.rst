RLRisk
==============================

A reinforcement learning environment based off the board game Risk. Designed with reinforcement learning in mind, this project aims to streamline research for economy-based games.

Getting Started
------------------------------

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- numpy <= 1.14
- pygame <= 1.9

User installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install this package is through PyPi

::

    pip install rlrisk

Otherwise you can manually install this package by cloning
the repository to your local computer

::

    git clone https://github.com/civrev/RLRisk

Then navigate to that directory and run setup.py

::

    python setup.py install

Working with RLRisk
------------------------------

RLRisk was a project concieved to streamline research by coding an environment already friendly to reinforcement learning techniques. As such working with RLRisk is extremely easy.

The Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The environment is the standard Wolrd Domination game rules for Risk by Hasbro. You can find these rules here: https://www.hasbro.com/common/instruct/risk.pdf

The environment is located in the file risk.py and is implemented using the class Risk(). The class is flexible enough to be initiallized with extremely custom rules, but for the most common game of Risk you can create a Risk object using only a list of players

::

    from rlrisk.agents import *
    from rlrisk.environment import *
    
    players = [BaseAgent(), AggressiveAgent()]
    env = Risk(players)
    results = env.play()

Agents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RLRisk comes with 3 agents, the BaseAgent, Human, and AggressiveAgent classes. All new agents must be subclasses of the BaseAgent class, but looking at the BaseAgent will show you that the framework of agents for RLRisk is very straight forward. It takes in the information it need to make a decision, and then it outputs a decision.

Final Remarks
------------------------------
This is my Senoir Project for my B.S. in Computer Science at the University of North Georgia
(Graduating May, 2018)



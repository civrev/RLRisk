# RLRisk

A reinforcement learning environment based off the board game Risk. Designed with reinforcement learning in mind, this project aims to streamline research for economy-based games.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

This package requires numpy and pygame. To install them use pip

```
pip install numpy
pip install pygame
```

### Installing

To install this package, clone the repository to your local computer

```
git clone https://github.com/civrev/RLRisk
```

Then navigate to that directory and run setup.py
```
python setup.py install
```

## Working with RLRisk

RLRisk was a project concieved to streamline research by coding an environment already friendly to reinforcement learning techniques. As such working with RLRisk is extremely easy.

### The environment

The environment is the standard Wolrd Domination game rules for Risk by Hasbro. You can find these rules here: https://www.hasbro.com/common/instruct/risk.pdf

The environment is located in the file risk.py and is implemented using the class Risk(). The class is flexible enough to be initiallized with extremely custom rules, but for the most common game of Risk you can create a Risk object using only a list of players.

```
from rlrisk.agents.base_agent import BaseAgent
from rlrisk.environment.risk import Risk

p1 = BaseAgent()
p2 = BaseAgent()
p3 = BaseAgent()

env = Risk.standard_game([p1,p2,p3])
```

### Agents

RLRisk comes with 2 agents, the BaseAgent and Human classes. All new agents must be subclasses of the BaseAgent class, but looking at base_agent.py will show you that the framework of agents for RLRisk is very straight forward. It takes in the information it need to make a decision, and then it outputs a decision.

## Final Remarks
This is my Senoir Project for my B.S. in Computer Science at the University of North Georgia
(Graduating May, 2018)



# AI-Based Castle Defence

## 1. Project Overview

AI-Based Castle Defence is a medieval castle defence game developed using Python and Pygame.

The main purpose of the project is to demonstrate classical Artificial Intelligence techniques inside an interactive game environment.

The enemy commander does not use machine learning, neural networks, datasets, or external AI APIs.

Instead, the game uses classical AI techniques including:

- Search
- Heuristic functions
- A* pathfinding
- Rule-based reasoning
- Knowledge representation
- State-space reasoning
- Minimax
- Alpha-Beta pruning
- Dynamic path replanning

---

# 2. Objectives

The main objectives of the project are:

1. Develop an interactive castle defence game.
2. Implement classical AI techniques.
3. Create an AI-controlled enemy commander.
4. Allow enemies to navigate the battlefield using A*.
5. Allow the AI to react when the battlefield changes.
6. Demonstrate rule-based decision making.
7. Demonstrate state-space search.
8. Demonstrate Minimax and Alpha-Beta pruning.
9. Provide visual information about AI decisions.
10. Test the AI algorithms independently.

---

# 3. Technologies Used

## Programming Language

Python 3.13

## Game Framework

Pygame 2.6.1

## Development Environment

Visual Studio Code

## AI Approach

Classical / Symbolic AI

---

# 4. Game Features

The game contains:

- Medieval castle
- Enemy units
- Enemy waves
- Defensive towers
- Tower upgrades
- Player-built walls
- Gold/resource system
- Combat system
- Victory condition
- Game-over condition
- Restart system
- AI Commander
- AI information panel

---

# 5. Classical AI Techniques

## 5.1 Knowledge Representation

The AI stores information about the current game environment.

The knowledge base can contain facts such as:

- Castle position
- Castle health
- Castle status
- Enemy positions
- Enemy count
- Spawn points
- Blocked cells

This information is used by the AI commander when making decisions.

Implementation:

```text
ai/knowledge.py
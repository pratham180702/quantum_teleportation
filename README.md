# Quantum Teleportation Project

This project implements the foundational quantum teleportation protocol using Qiskit. The protocol transfers an unknown qubit state from Alice to Bob using entanglement (a Bell pair) and classical communication.

## Table of Contents
- [Visual Demonstration (Quirk)](#visual-demonstration-quirk)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Simulations](#running-the-simulations)
- [Running on Real IBM Hardware](#running-on-real-ibm-hardware)
- [Fidelity Analysis](#fidelity-analysis)

## Visual Demonstration (Quirk)
Before diving into the code, you can visualize the teleportation circuit in Quirk, an interactive quantum circuit simulator:

[**Open Quantum Teleportation in Quirk**](https://algassert.com/quirk#circuit=%7B%22cols%22%3A%5B%5B%22H%22%5D%2C%5B%22%E2%80%A2%22%2C%22X%22%5D%2C%5B%22%E2%80%A6%22%2C%22%E2%80%A6%22%5D%2C%5B%22X%22%2C%22%E2%80%A2%22%5D%2C%5B%22H%22%5D%2C%5B%22Measure%22%2C%22Measure%22%5D%2C%5B%22%E2%80%A2%22%2C%22%22%2C%22X%22%5D%2C%5B%22%22%2C%22%E2%80%A2%22%2C%22Z%22%5D%5D%7D)

*(This Quirk circuit prepares a Bell state, performs the Bell measurement on Alice's side, and applies the conditional Pauli operations on Bob's side.)*

## Project Structure
```text
qubit_state_teleportation/
├── requirements.txt            # Python dependencies
├── src/
│   ├── teleportation.py        # Core function to build the teleportation circuit
│   └── utils.py                # Utilities for state preparation and fidelity calculation
├── scripts/
│   ├── 1_ideal_simulation.py   # Simulates teleportation perfectly without noise
│   ├── 2_noisy_simulation.py   # Simulates teleportation with fake hardware noise
│   ├── 3_hardware_execution.py # Submits the circuit to a real IBM Quantum computer
│   └── 4_fidelity_analysis.py  # Tests multiple initial states and plots fidelities
└── outputs/                    # Directory where generated plots and circuit images are saved
```

## Setup Instructions

1. **Create a Python Virtual Environment (Optional but Recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   .\\venv\\Scripts\\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulations

1. **Ideal Simulation**
   Run the ideal, noise-free simulation. It will output a histogram and a circuit diagram in the `outputs/` folder.
   ```bash
   python scripts/1_ideal_simulation.py
   ```

2. **Noisy Simulation**
   Run the simulation using `FakeManilaV2` to see how realistic quantum noise affects the outcome.
   ```bash
   python scripts/2_noisy_simulation.py
   ```

## Running on Real IBM Hardware

To run the circuit on a real quantum computer, you need an IBM Quantum account.

1. **Get your API Token**: Sign up at [quantum.ibm.com](https://quantum.ibm.com/) and copy your API token from the dashboard.
2. **Save your token**: Open a Python terminal and run:
   ```python
   from qiskit_ibm_runtime import QiskitRuntimeService
   QiskitRuntimeService.save_account(channel="ibm_quantum", token="YOUR_TOKEN_HERE")
   ```
3. **Execute the script**:
   ```bash
   python scripts/3_hardware_execution.py
   ```
   *Note: Jobs submitted to real hardware are placed in a queue and may take some time to complete.*

## Fidelity Analysis

To compare how well the teleportation protocol preserves the quantum state under ideal vs. noisy conditions across different states (e.g., $|0\\rangle$, $|1\\rangle$, $|+\\rangle$, $|-\\rangle$, $|i\\rangle$, $|-i\\rangle$, and random states), run:

```bash
python scripts/4_fidelity_analysis.py
```
This will generate a bar chart (`outputs/fidelity_comparison.png`) showing the calculated fidelities.

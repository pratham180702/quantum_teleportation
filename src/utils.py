import numpy as np
from qiskit import QuantumCircuit

def prepare_state_circuit(state_name="0"):
    """
    Returns a 1-qubit QuantumCircuit that prepares a specific state.
    
    Args:
        state_name (str): One of "0", "1", "+", "-", "i", "-i", or "random".
        
    Returns:
        QuantumCircuit: 1-qubit circuit preparing the state.
    """
    qc = QuantumCircuit(1)
    
    # ground state
    if state_name == "0":
        pass # Already in |0>

    # excited state
    elif state_name == "1":
        qc.x(0)

    # superposition phase states + and - basis
    elif state_name == "+":
        qc.h(0)
    elif state_name == "-":
        qc.x(0)
        qc.h(0)

    # Left and Right hand states 
    # Y-basis
    # H . S state
    # elif state_name == "i":
    #     qc.h(0)
    #     qc.s(0)
    # elif state_name == "-i":
    #     qc.x(0)
    #     qc.h(0)
    #     qc.s(0)

    # elif state_name == "random":
    #     # Random angles for U gate
    #     theta = np.random.uniform(0, np.pi)
    #     phi = np.random.uniform(0, 2*np.pi)
    #     lam = np.random.uniform(0, 2*np.pi)
    #     qc.u(theta, phi, lam, 0)
    else:
        raise ValueError("Unknown state name. Use '0', '1', '+', '-', 'i', '-i', or 'random'.")
        
    return qc

import os
import sys

# Add parent directory to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

from src.teleportation import create_teleportation_circuit
from src.utils import prepare_state_circuit

def main():
    print("--- Ideal Quantum Teleportation Simulation ---")
    
    # We will teleport the state |1>
    # In the ideal case, no matter what Alice measures, Bob's qubit should ALWAYS be 1.
    print("Preparing initial state: |1>")
    state_prep = prepare_state_circuit("1")
    
    # Create the teleportation circuit
    qc = create_teleportation_circuit(state_prep)
    
    # We need to measure Bob's qubit (q2) to verify it is |1>.
    # It will be stored in the 'result' classical register.
    qc.measure(2, 2) # Measure qubit 2 into the 3rd classical bit (result)
    
    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)
    
    # Save the circuit diagram
    print("Saving circuit diagram to outputs/ideal_circuit.png...")
    qc.draw(output="mpl", filename="outputs/ideal_circuit.png")
    
    # Use AerSimulator
    simulator = AerSimulator()
    
    # Transpile the circuit for the simulator
    compiled_circuit = transpile(qc, simulator)
    
    # Run the simulation
    print("Running simulation...")
    job = simulator.run(compiled_circuit, shots=1024)
    result = job.result()
    counts = result.get_counts(compiled_circuit)
    
    print("\\nMeasurement Counts:")
    print(counts)
    
    # Note on Qiskit bit ordering:
    # Qiskit orders classical bits right-to-left: c_result, c_rx, c_rz
    # For teleporting |1>, the leftmost bit (c_result) should ALWAYS be 1.
    success = all(state.startswith('1') for state in counts.keys())
    
    if success:
        print("\\nSuccess! Bob's qubit was always measured as 1, regardless of Alice's measurements.")
    else:
        print("\\nError: Bob's qubit was not always 1. Something went wrong!")
        
    # Plot histogram
    print("Saving histogram to outputs/ideal_histogram.png...")
    plot_histogram(counts, filename="outputs/ideal_histogram.png")

if __name__ == "__main__":
    main()

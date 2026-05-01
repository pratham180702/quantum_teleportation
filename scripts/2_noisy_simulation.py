import os
import sys

# Add parent directory to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# Using a Fake backend from the new runtime module
from qiskit_ibm_runtime.fake_provider import FakeManilaV2

from src.teleportation import create_teleportation_circuit
from src.utils import prepare_state_circuit

def main():
    print("--- Noisy Quantum Teleportation Simulation ---")
    
    # We will teleport the state |1> again to see the impact of noise
    print("Preparing initial state: |1>")
    state_prep = prepare_state_circuit("1")
    
    # Create the teleportation circuit
    qc = create_teleportation_circuit(state_prep)
    
    # Measure Bob's qubit
    qc.measure(2, 2)
    
    os.makedirs("outputs", exist_ok=True)
    
    print("Loading FakeManilaV2 backend...")
    fake_backend = FakeManilaV2()
    
    # Create an AerSimulator from the fake backend's noise model
    simulator = AerSimulator.from_backend(fake_backend)
    
    # Transpile the circuit for the fake backend (this adapts it to the hardware's topology and basis gates)
    print("Transpiling circuit for the noisy backend...")
    compiled_circuit = transpile(qc, fake_backend)
    
    # Save the transpiled circuit diagram (it will look much more complex due to basis gate decomposition and routing)
    compiled_circuit.draw(output="mpl", filename="outputs/noisy_transpiled_circuit.png", idle_wires=False)
    
    # Run the simulation
    print("Running noisy simulation...")
    job = simulator.run(compiled_circuit, shots=1024)
    result = job.result()
    counts = result.get_counts(compiled_circuit)
    
    print("\\nMeasurement Counts:")
    print(counts)
    
    # Analyze results
    # In ideal scenario, left-most bit is ALWAYS 1. In noisy scenario, it might sometimes be 0.
    correct_shots = sum(count for state, count in counts.items() if state.startswith('1'))
    total_shots = sum(counts.values())
    accuracy = correct_shots / total_shots * 100
    
    print(f"\\nAccuracy of teleporting |1> under noise: {accuracy:.2f}%")
    if accuracy < 100.0:
        print("The noise model successfully introduced errors!")
        
    # Plot histogram
    print("Saving histogram to outputs/noisy_histogram.png...")
    plot_histogram(counts, filename="outputs/noisy_histogram.png")

if __name__ == "__main__":
    main()

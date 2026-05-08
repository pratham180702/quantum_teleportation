import os
import sys
import numpy as np

# Add parent directory to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import transpile, QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity, DensityMatrix, partial_trace
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
import matplotlib.pyplot as plt

from src.teleportation import create_teleportation_circuit
from src.utils import prepare_state_circuit

def main():
    print("--- Teleportation Fidelity Analysis ---")
    
    # We will test multiple states
    # states_to_test = ["0", "1", "+", "-", "i", "-i", "random"]
    states_to_test = ["0", "1", "+", "-"]
    
    ideal_fidelities = []
    noisy_fidelities = []
    
    # Simulators
    # For fidelity calculation, we need the statevector. 
    # Qiskit Aer allows saving the statevector before measurement if we want,
    # or we can just simulate the circuit without the final measurements 
    # to get the exact density matrix/statevector.
    
    ideal_sim = AerSimulator(method="statevector")
    
    # For noisy simulation with density matrices
    fake_backend = FakeManilaV2()
    noisy_sim = AerSimulator.from_backend(fake_backend, method="density_matrix")
    
    os.makedirs("outputs", exist_ok=True)
    
    for state_name in states_to_test:
        print(f"\\nAnalyzing state: {state_name}")
        
        # 1. Get the ideal target statevector
        prep_qc = prepare_state_circuit(state_name)
        ideal_state = Statevector.from_instruction(prep_qc)
        
        # 2. Create the teleportation circuit (WITHOUT final measurements on Bob's qubit)
        # We need the full quantum state to calculate fidelity.
        tele_qc = create_teleportation_circuit(prep_qc)
        
        # We must remove the measure instructions to get the statevector/density matrix 
        # of the system. Wait, if we remove Alice's measurements, we can't apply the 
        # conditional X and Z gates!
        # In simulation, we can use a special Aer instruction `save_density_matrix` 
        # at the end of the circuit to capture the state.
        
        # Let's create a specific circuit for fidelity simulation
        sim_qc = tele_qc.copy()
        sim_qc.save_density_matrix()
        
        # Ideal Simulation
        compiled_ideal = transpile(sim_qc, ideal_sim)
        job_ideal = ideal_sim.run(compiled_ideal, shots=1)
        res_ideal = job_ideal.result()
        rho_ideal_full = res_ideal.data(0)['density_matrix']
        
        # Trace out qubits 0 and 1 (Alice's qubits) to get Bob's state (qubit 2)
        rho_bob_ideal = partial_trace(rho_ideal_full, [0, 1])
        fid_ideal = state_fidelity(ideal_state, rho_bob_ideal)
        ideal_fidelities.append(fid_ideal)
        print(f"  Ideal Fidelity: {fid_ideal:.4f}")
        
        # Noisy Simulation
        # Transpile the base teleportation circuit first to avoid basis errors
        compiled_tele = transpile(tele_qc, noisy_sim)
        compiled_noisy = compiled_tele.copy()
        compiled_noisy.save_density_matrix()
        job_noisy = noisy_sim.run(compiled_noisy, shots=1)
        res_noisy = job_noisy.result()
        rho_noisy_full = res_noisy.data(0)['density_matrix']
        
        # compiled_noisy might have more than 3 qubits (e.g. 5 for Manila)
        # Find which physical qubit Bob's virtual qubit (index 2) was mapped to
        layout = compiled_tele.layout.initial_layout
        if layout is not None:
            # Get the physical index for the 3rd virtual qubit (Bob's qubit)
            # The virtual register is usually the first one in tele_qc
            virt_q = tele_qc.qubits[2]
            physical_bob_q = layout[virt_q]
        else:
            physical_bob_q = 2
            
        qubits_to_trace = [i for i in range(compiled_noisy.num_qubits) if i != physical_bob_q]
        rho_bob_noisy = partial_trace(rho_noisy_full, qubits_to_trace)
        
        fid_noisy = state_fidelity(ideal_state, rho_bob_noisy)
        noisy_fidelities.append(fid_noisy)
        print(f"  Noisy Fidelity: {fid_noisy:.4f}")

    # Plot the results
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(states_to_test))
    width = 0.35
    
    ax.bar(x - width/2, ideal_fidelities, width, label='Ideal Simulation', color='skyblue')
    ax.bar(x + width/2, noisy_fidelities, width, label='Noisy Simulation (FakeManilaV2)', color='salmon')
    
    ax.set_ylabel('State Fidelity')
    ax.set_title('Quantum Teleportation Fidelity Across Different Initial States')
    ax.set_xticks(x)
    ax.set_xticklabels(states_to_test)
    ax.legend()
    ax.set_ylim([0, 1.1])
    
    # Add value labels on top of bars
    for i, (fid_i, fid_n) in enumerate(zip(ideal_fidelities, noisy_fidelities)):
        ax.text(i - width/2, fid_i + 0.02, f"{fid_i:.2f}", ha='center', va='bottom', fontsize=9)
        ax.text(i + width/2, fid_n + 0.02, f"{fid_n:.2f}", ha='center', va='bottom', fontsize=9)
        
    plt.tight_layout()
    plt.savefig("outputs/fidelity_comparison.png")
    print("\\nSaved fidelity comparison plot to outputs/fidelity_comparison.png")

if __name__ == "__main__":
    main()

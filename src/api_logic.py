import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt

from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, state_fidelity, partial_trace
from qiskit.visualization import plot_histogram
from qiskit_ibm_runtime.fake_provider import FakeManilaV2   
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

from src.teleportation import create_teleportation_circuit
from src.utils import prepare_state_circuit

os.makedirs("outputs", exist_ok=True)

def run_ideal_simulation(state_name: str):
    """Run ideal simulation for a given state."""
    state_prep = prepare_state_circuit(state_name)
    qc = create_teleportation_circuit(state_prep)
    qc.measure(2, 2)
    
    timestamp = int(time.time())
    circuit_filename = f"outputs/ideal_circuit_{timestamp}.png"
    hist_filename = f"outputs/ideal_histogram_{timestamp}.png"
    
    qc.draw(output="mpl", filename=circuit_filename)
    
    simulator = AerSimulator()
    compiled_circuit = transpile(qc, simulator)
    job = simulator.run(compiled_circuit, shots=1024)
    result = job.result()
    counts = result.get_counts(compiled_circuit)
    
    plot_histogram(counts, filename=hist_filename)
    plt.close('all')
    
    return {
        "counts": counts,
        "circuit_url": f"/{circuit_filename}",
        "histogram_url": f"/{hist_filename}"
    }

def run_noisy_simulation(state_name: str):
    """Run noisy simulation using FakeManilaV2."""
    state_prep = prepare_state_circuit(state_name)
    qc = create_teleportation_circuit(state_prep)
    qc.measure(2, 2)
    
    timestamp = int(time.time())
    circuit_filename = f"outputs/noisy_circuit_{timestamp}.png"
    hist_filename = f"outputs/noisy_histogram_{timestamp}.png"
    
    fake_backend = FakeManilaV2()
    simulator = AerSimulator.from_backend(fake_backend)
    compiled_circuit = transpile(qc, fake_backend)
    
    compiled_circuit.draw(output="mpl", filename=circuit_filename, idle_wires=False)
    
    job = simulator.run(compiled_circuit, shots=1024)
    result = job.result()
    counts = result.get_counts(compiled_circuit)
    
    plot_histogram(counts, filename=hist_filename)
    plt.close('all')
    
    return {
        "counts": counts,
        "circuit_url": f"/{circuit_filename}",
        "histogram_url": f"/{hist_filename}"
    }

def run_hardware_execution(state_name: str):
    """Submit the circuit to real IBM Quantum hardware."""
    try:
        service = QiskitRuntimeService()
    except Exception as e:
        return {"error": f"Failed to connect to IBM Quantum. Ensure token is saved. {str(e)}"}
        
    backend = service.least_busy(simulator=False, operational=True, min_num_qubits=3)
    
    state_prep = prepare_state_circuit(state_name)
    qc = create_teleportation_circuit(state_prep)
    qc.measure(2, 2)
    
    compiled_circuit = transpile(qc, backend)
    sampler = SamplerV2(mode=backend)
    
    job = sampler.run([(compiled_circuit,)])
    
    return {
        "message": "Job submitted successfully!",
        "job_id": job.job_id(),
        "backend": backend.name,
        "status": "QUEUED - Check IBM Quantum Dashboard for results."
    }

def run_fidelity_analysis():
    """Run fidelity analysis across all states."""
    states_to_test = ["0", "1", "+", "-", "i", "-i", "random"]
    ideal_fidelities = []
    noisy_fidelities = []
    
    ideal_sim = AerSimulator(method="statevector")
    fake_backend = FakeManilaV2()
    noisy_sim = AerSimulator.from_backend(fake_backend, method="density_matrix")
    
    for state_name in states_to_test:
        prep_qc = prepare_state_circuit(state_name)
        ideal_state = Statevector.from_instruction(prep_qc)
        
        tele_qc = create_teleportation_circuit(prep_qc)
        sim_qc = tele_qc.copy()
        sim_qc.save_density_matrix()
        
        # Ideal
        compiled_ideal = transpile(sim_qc, ideal_sim)
        job_ideal = ideal_sim.run(compiled_ideal, shots=1)
        res_ideal = job_ideal.result()
        rho_ideal_full = res_ideal.data(0)['density_matrix']
        rho_bob_ideal = partial_trace(rho_ideal_full, [0, 1])
        fid_ideal = state_fidelity(ideal_state, rho_bob_ideal)
        ideal_fidelities.append(float(fid_ideal))
        
        # Noisy
        compiled_tele = transpile(tele_qc, noisy_sim)
        compiled_noisy = compiled_tele.copy()
        compiled_noisy.save_density_matrix()
        job_noisy = noisy_sim.run(compiled_noisy, shots=1)
        res_noisy = job_noisy.result()
        rho_noisy_full = res_noisy.data(0)['density_matrix']
        
        layout = compiled_tele.layout.initial_layout
        if layout is not None:
            virt_q = tele_qc.qubits[2]
            physical_bob_q = layout[virt_q]
        else:
            physical_bob_q = 2
            
        qubits_to_trace = [i for i in range(compiled_noisy.num_qubits) if i != physical_bob_q]
        rho_bob_noisy = partial_trace(rho_noisy_full, qubits_to_trace)
        fid_noisy = state_fidelity(ideal_state, rho_bob_noisy)
        noisy_fidelities.append(float(fid_noisy))

    timestamp = int(time.time())
    chart_filename = f"outputs/fidelity_chart_{timestamp}.png"
    
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
    
    for i, (fid_i, fid_n) in enumerate(zip(ideal_fidelities, noisy_fidelities)):
        ax.text(i - width/2, fid_i + 0.02, f"{fid_i:.2f}", ha='center', va='bottom', fontsize=9)
        ax.text(i + width/2, fid_n + 0.02, f"{fid_n:.2f}", ha='center', va='bottom', fontsize=9)
        
    plt.tight_layout()
    plt.savefig(chart_filename)
    plt.close('all')
    
    return {
        "states": states_to_test,
        "ideal_fidelities": ideal_fidelities,
        "noisy_fidelities": noisy_fidelities,
        "chart_url": f"/{chart_filename}"
    }

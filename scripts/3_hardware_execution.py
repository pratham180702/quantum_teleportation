import os
import sys
import logging

# 1. Setup Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("quantum_teleportation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# Ensure these modules exist in your src directory
from src.teleportation import create_teleportation_circuit
from src.utils import prepare_state_circuit

def main():
    logger.info("--- Real Hardware Quantum Teleportation Execution ---")
    
    # 2. Initialize the Qiskit Runtime Service
    try:
        # Use the updated channel name 'ibm_quantum_platform'
        service = QiskitRuntimeService()
        logger.info("Successfully connected to IBM Quantum.")
    except Exception as e:
        logger.error(f"Failed to connect to IBM Quantum: {e}")
        logger.info("Tip: Run QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='YOUR_TOKEN')")
        return

    # 3. Select Backend
    try:
        backend = service.least_busy(simulator=False, operational=True, min_num_qubits=3)
        logger.info(f"Selected backend: {backend.name}")
    except Exception as e:
        logger.error(f"No suitable real hardware found: {e}")
        return
    
    # 4. Create the circuit
    logger.info("Preparing initial state: |1>")
    state_prep = prepare_state_circuit("1")
    qc = create_teleportation_circuit(state_prep)
    
    # Ensure measurement is mapped correctly
    # qc.measure(2, 2) # Only uncomment if your create_teleportation_circuit doesn't handle it
    
    # 5. Transpile the circuit
    logger.info(f"Transpiling circuit for {backend.name}...")
    compiled_circuit = transpile(qc, backend, optimization_level=1)
    
    # 6. Initialize SamplerV2
    # FIX: Pass backend to the 'mode' parameter
    sampler = SamplerV2(mode=backend)
    
    # 7. Run the job
    logger.info("Submitting job to IBM Quantum. Monitoring queue...")
    try:
        # SamplerV2 expects a list of pubs (Primitive Unified Blocs)
        job = sampler.run([(compiled_circuit,)])
        logger.info(f"Job ID: {job.job_id()}")
    except Exception as e:
        logger.error(f"Job submission failed: {e}")
        return
    
    # 8. Process results
    try:
        result = job.result()
        logger.info("Job complete! Processing results...")
        
        pub_result = result[0]
        meas_data = pub_result.data
        
        # Accessing data in V2 depends on the register names in your circuit
        # If your classical register was named 'result':
        if hasattr(meas_data, 'result'):
            counts = meas_data.result.get_counts()
            logger.info(f"Counts for Bob's qubit: {counts}")
            
            # Ensure output directory exists
            os.makedirs("outputs", exist_ok=True)
            plot_histogram(counts).savefig("outputs/hardware_histogram.png")
            logger.info("Histogram saved to outputs/hardware_histogram.png")
        else:
            # Fallback: log available registers to help debugging
            available_regs = [attr for attr in dir(meas_data) if not attr.startswith('_')]
            logger.warning(f"Register 'result' not found. Available registers: {available_regs}")
            
    except Exception as e:
        logger.error(f"Error extracting results: {e}")

if __name__ == "__main__":
    main()
from qiskit_ibm_runtime import QiskitRuntimeService

# go to the main site:
# https://quantum.cloud.ibm.com/


QiskitRuntimeService.save_account(
    channel="ibm_quantum", 
    token="YOUR_IBM_QUANTUM_TOKEN_HERE",
    overwrite=True
)
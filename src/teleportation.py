from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import UGate

def create_teleportation_circuit(state_preparation_circuit=None):
    """
    Creates a quantum teleportation circuit.
    
    Args:
        state_preparation_circuit (QuantumCircuit, optional): A 1-qubit circuit 
            that prepares the initial state to be teleported. If None, the default 
            state |0> is used.
            
    Returns:
        QuantumCircuit: The complete teleportation circuit.
    """
    # 3 qubits: 
    # q0: Alice's qubit (state to teleport)
    # q1: Alice's half of the Bell pair
    # q2: Bob's half of the Bell pair
    qr = QuantumRegister(3, name="q")
    
    # 2 classical bits to store Alice's measurements
    crz = ClassicalRegister(1, name="crz")
    crx = ClassicalRegister(1, name="crx")
    
    # Optional classical register for measuring Bob's final state for verification
    cr_result = ClassicalRegister(1, name="result")
    
    qc = QuantumCircuit(qr, crz, crx, cr_result)
    
    # 1. Prepare initial state on qubit 0
    if state_preparation_circuit is not None:
        qc.compose(state_preparation_circuit, [0], inplace=True)
        
    qc.barrier()
    
    # 2. Create entangled Bell pair between Alice's qubit 1 and Bob's qubit 2
    qc.h(1)
    qc.cx(1, 2)
    
    qc.barrier()
    
    # 3. Alice performs Bell-basis measurement
    qc.cx(0, 1)
    qc.h(0)
    
    qc.barrier()
    
    # Alice measures her qubits
    qc.measure(0, crz)
    qc.measure(1, crx)
    
    qc.barrier()
    
    # 4. Bob applies conditional operations based on Alice's measurements
    # Using if_test to apply X and Z gates conditionally based on classical register values
    with qc.if_test((crx, 1)):
        qc.x(2)
    with qc.if_test((crz, 1)):
        qc.z(2)
    
    return qc

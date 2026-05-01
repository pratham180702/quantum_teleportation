document.addEventListener('DOMContentLoaded', () => {
    const btnIdeal = document.getElementById('btn-ideal');
    const btnNoisy = document.getElementById('btn-noisy');
    const btnHardware = document.getElementById('btn-hardware');
    const btnFidelity = document.getElementById('btn-fidelity');
    const stateSelect = document.getElementById('state-select');
    
    const loader = document.getElementById('loader');
    const loaderText = document.getElementById('loader-text');
    const resultsContent = document.getElementById('results-content');
    
    const circuitPanel = document.getElementById('circuit-panel');
    const histogramPanel = document.getElementById('histogram-panel');
    const fidelityPanel = document.getElementById('fidelity-panel');
    const hardwarePanel = document.getElementById('hardware-panel');

    function showLoader(text) {
        resultsContent.classList.add('hidden');
        loaderText.innerText = text;
        loader.classList.remove('hidden');
    }

    function hideLoader() {
        loader.classList.add('hidden');
        resultsContent.classList.remove('hidden');
    }

    function hideAllPanels() {
        circuitPanel.classList.add('hidden');
        histogramPanel.classList.add('hidden');
        fidelityPanel.classList.add('hidden');
        hardwarePanel.classList.add('hidden');
    }

    async function runSimulation(endpoint, loadingText, isHardware = false) {
        showLoader(loadingText);
        hideAllPanels();
        
        const state = stateSelect.value;
        
        try {
            const response = await fetch(`/api/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ state })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                if (isHardware) {
                    hardwarePanel.classList.remove('hidden');
                    if (data.error) {
                        document.getElementById('hardware-status').innerHTML = `<span style="color: #ef4444;">Error: ${data.error}</span>`;
                    } else {
                        document.getElementById('hardware-status').innerHTML = `
                            <strong>Message:</strong> ${data.message} <br>
                            <strong>Job ID:</strong> ${data.job_id} <br>
                            <strong>Backend:</strong> ${data.backend} <br>
                            <strong>Status:</strong> ${data.status}
                        `;
                    }
                } else {
                    circuitPanel.classList.remove('hidden');
                    histogramPanel.classList.remove('hidden');
                    
                    // Force cache bypass by appending timestamp
                    const ts = new Date().getTime();
                    document.getElementById('circuit-img').src = data.circuit_url + '?t=' + ts;
                    document.getElementById('histogram-img').src = data.histogram_url + '?t=' + ts;
                    
                    document.getElementById('counts-data').innerText = "Measurement Counts:\n" + JSON.stringify(data.counts, null, 2);
                }
            } else {
                alert("Error: " + data.detail);
            }
        } catch (err) {
            alert("Network Error: " + err.message);
        }
        
        hideLoader();
    }

    async function runFidelity() {
        showLoader("Running Comprehensive Fidelity Analysis across all states...");
        hideAllPanels();
        
        try {
            const response = await fetch(`/api/fidelity`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                fidelityPanel.classList.remove('hidden');
                const ts = new Date().getTime();
                document.getElementById('fidelity-img').src = data.chart_url + '?t=' + ts;
            } else {
                alert("Error: " + data.detail);
            }
        } catch (err) {
            alert("Network Error: " + err.message);
        }
        
        hideLoader();
    }

    btnIdeal.addEventListener('click', () => runSimulation('ideal', 'Running Ideal Noise-Free Simulation...'));
    btnNoisy.addEventListener('click', () => runSimulation('noisy', 'Running Noisy Simulation on FakeManilaV2 topology...'));
    btnHardware.addEventListener('click', () => runSimulation('hardware', 'Submitting Job to IBM Quantum Hardware...', true));
    btnFidelity.addEventListener('click', () => runFidelity());

    // Image Modal Logic
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-img');
    const closeModal = document.querySelector('.close-modal');

    document.querySelectorAll('.img-wrapper img').forEach(img => {
        img.addEventListener('click', function() {
            if (this.src && this.src !== window.location.href) {
                modal.classList.remove('hidden');
                modalImg.src = this.src;
            }
        });
    });

    closeModal.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });
});

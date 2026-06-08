document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('patient-form');
    const tableBody = document.getElementById('patients-tbody');
    const notification = document.getElementById('notification');
    const notifMessage = document.getElementById('notification-message');
    const cancelBtn = document.getElementById('cancel-btn');
    const submitBtn = document.getElementById('submit-btn');
    const dobInput = document.getElementById('dob');

    // Restrict DOB to today and past dates
    const today = new Date().toISOString().split('T')[0];
    dobInput.setAttribute('max', today);

    let isEditing = false;

    // Load initial data
    fetchPatients();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = document.getElementById('patient-id').value;
        const patientData = {
            full_name: document.getElementById('full-name').value,
            dob: document.getElementById('dob').value,
            email: document.getElementById('email').value,
            glucose: parseFloat(document.getElementById('glucose').value),
            haemoglobin: parseFloat(document.getElementById('haemoglobin').value),
            cholesterol: parseFloat(document.getElementById('cholesterol').value)
        };

        try {
            if (isEditing) {
                await updatePatient(id, patientData);
                showNotification('Patient updated successfully', 'success');
            } else {
                await createPatient(patientData);
                showNotification('Patient added successfully', 'success');
            }
            resetForm();
            fetchPatients();
        } catch (error) {
            showNotification(error.message, 'error');
        }
    });

    cancelBtn.addEventListener('click', resetForm);

    async function fetchPatients() {
        try {
            const response = await fetch('/api/patients');
            if (!response.ok) throw new Error('Failed to fetch patients');
            const data = await response.json();
            renderTable(data);
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }

    async function createPatient(data) {
        const response = await fetch('/api/patients', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to create patient');
        }
    }

    async function updatePatient(id, data) {
        const response = await fetch(`/api/patients/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Failed to update patient');
        }
    }

    window.deletePatient = async (id) => {
        try {
            const response = await fetch(`/api/patients/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Failed to delete patient');
            
            showNotification('Patient deleted successfully', 'success');
            fetchPatients();
        } catch (error) {
            showNotification(error.message, 'error');
        }
    };

    window.editPatient = (id, patientStr) => {
        const patient = JSON.parse(decodeURIComponent(patientStr));
        
        document.getElementById('patient-id').value = patient.id;
        document.getElementById('full-name').value = patient.full_name;
        document.getElementById('dob').value = patient.dob;
        document.getElementById('email').value = patient.email;
        document.getElementById('glucose').value = patient.glucose;
        document.getElementById('haemoglobin').value = patient.haemoglobin;
        document.getElementById('cholesterol').value = patient.cholesterol;
        
        isEditing = true;
        submitBtn.textContent = 'Update Patient';
        cancelBtn.style.display = 'inline-block';
        
        // Scroll to form
        document.querySelector('.form-card').scrollIntoView({ behavior: 'smooth' });
    };

    function renderTable(patients) {
        tableBody.innerHTML = '';
        
        if (patients.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-secondary);">No patients found</td></tr>`;
            return;
        }

        patients.forEach(p => {
            const tr = document.createElement('tr');
            
            const remarksBadge = p.remarks === 'Normal' 
                ? '<span class="badge badge-normal">Normal</span>'
                : `<span class="badge badge-warning">${p.remarks}</span>`;

            // Encode patient object for edit button
            const patientStr = encodeURIComponent(JSON.stringify(p));

            tr.innerHTML = `
                <td>${p.full_name}</td>
                <td>${p.email}</td>
                <td>${p.dob}</td>
                <td><small>G: ${p.glucose} | H: ${p.haemoglobin} | C: ${p.cholesterol}</small></td>
                <td>${remarksBadge}</td>
                <td>
                    <button class="edit-btn" onclick="editPatient(${p.id}, '${patientStr}')">Edit</button>
                    <button class="danger-btn" onclick="deletePatient(${p.id})">Delete</button>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }

    function resetForm() {
        form.reset();
        document.getElementById('patient-id').value = '';
        isEditing = false;
        submitBtn.textContent = 'Save Patient';
        cancelBtn.style.display = 'none';
    }

    function showNotification(message, type) {
        notifMessage.textContent = message;
        notification.className = `notification show ${type}`;
        
        setTimeout(() => {
            notification.className = 'notification hidden';
        }, 3000);
    }
});

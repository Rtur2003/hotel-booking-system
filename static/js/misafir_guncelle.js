document.addEventListener('DOMContentLoaded', () => {
    // Misafir bilgilerini güncelle
    const misafirFields = document.querySelectorAll('.misafir-field');
    misafirFields.forEach(field => {
        field.addEventListener('input', (e) => {
            const misafirID = e.target.dataset.id;
            const fieldValue = e.target.value;
            const fieldType = e.target.id.split('-')[0];

            // Form validation
            validateField(fieldType, fieldValue, misafirID);

            // Güncelleme işlemini backend'e gönder
            updateMisafir(misafirID, fieldType, fieldValue);
        });
    });

    // Misafir silme işlemi
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const misafirID = e.target.dataset.id;
            deleteMisafir(misafirID);
        });
    });
});

// Form validation function
function validateField(fieldType, fieldValue, misafirID) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.style.display = 'none';

    if (fieldType === 'kimlik' && fieldValue.length > 50) {
        errorMessage.style.display = 'block';
        errorMessage.innerText = 'Kimlik numarası 50 karakterden fazla olamaz.';
        return;
    }

    // Add other validation rules for fields if needed
}

// Misafir güncelleme işlemi
function updateMisafir(misafirID, fieldType, fieldValue) {
    fetch(`/misafir-guncelle/${misafirID}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fieldType, fieldValue })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Misafir bilgisi başarıyla güncellendi.');
        }
    })
    .catch(error => {
        console.error('Güncelleme hatası:', error);
    });
}

// Misafir silme işlemi
function deleteMisafir(misafirID) {
    fetch(`/misafir-sil/${misafirID}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById(`misafir-${misafirID}`).remove();
        }
    })
    .catch(error => {
        console.error('Silme hatası:', error);
    });
}

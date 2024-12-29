document.addEventListener("DOMContentLoaded", function() {
    const selectElements = document.querySelectorAll('.payment-status');

    selectElements.forEach(select => {
        select.addEventListener('change', function() {
            const paymentId = this.getAttribute('data-payment-id');
            const newStatus = this.value;

            // Güncellemeyi veritabanına gönder
            fetch(`/update_payment_status/${paymentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: newStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Durum başarıyla güncellendi.');
                } else {
                    alert('Güncelleme başarısız oldu.');
                }
            })
            .catch(error => {
                console.error('Hata:', error);
                alert('Bir hata oluştu.');
            });
        });
    });
});

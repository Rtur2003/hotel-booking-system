document.getElementById('reservation-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Formun sayfayı yenilemesini engeller

    let formData = {
        checkIn: document.getElementById('checkIn').value,
        checkOut: document.getElementById('checkOut').value,
        roomType: document.getElementById('roomType').value,
        guestsCount: document.getElementById('guestsCount').value,
        guests: [] // Misafir bilgileri
    };

    for (let i = 1; i <= formData.guestsCount; i++) {
        let guestName = document.getElementById('adultName' + i).value;
        let guestTc = document.getElementById('adultTc' + i).value;

        formData.guests.push({
            name: guestName,
            tc: guestTc
        });
    }

    fetch('/rezervasyon', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.message === 'Rezervasyon başarıyla alındı!') {
            // Başarıyla rezervasyon yapıldığında başka bir sayfaya yönlendirme yapılabilir
        }
    })
    .catch(error => {
        console.error('Hata:', error);
        alert('Bir hata oluştu!');
    });
});

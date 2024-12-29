// Sayfa yüklendiğinde verileri alalım
document.addEventListener("DOMContentLoaded", function () {
    fetchMisafirler();
});

// Misafir verilerini çekmek ve listelemek için AJAX çağrısı
function fetchMisafirler() {
    fetch('/get_aktif_misafirler')  // Flask'tan aktif misafirler verisini alacağız
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('misafirler-tbody');
            tbody.innerHTML = ''; // Önceki verileri temizle
            data.forEach(misafir => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${misafir.MisafirID}</td>
                    <td>${misafir.Isim}</td>
                    <td>${misafir.Soyisim}</td>
                    <td>${misafir.Yas}</td>
                    <td>${misafir.Kimlik}</td>
                    <td>${misafir.GirisTarihi}</td>
                    <td>${misafir.CikisTarihi || 'Devam Ediyor'}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => console.error('Hata:', error));
}

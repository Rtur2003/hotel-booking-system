async function loadUsers() {
    const response = await fetch('/get_users');
    const users = await response.json();
    const tableBody = document.querySelector('#userTable tbody');
    tableBody.innerHTML = ''; // Eski verileri temizle

    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.tel}</td>
            <td>${user.role}</td>
            <td>
                <div class="dropdown">
                    <span>Ayarlar ⚙️</span>
                    <div class="dropdown-content">
                        <button onclick="updateRole(${user.id}, 'üye')">Üye</button>
                        <button onclick="updateRole(${user.id}, 'personel')">Personel</button>
                        <button onclick="updateRole(${user.id}, 'admin')">Admin</button>
                    </div>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

async function updateRole(userId, newRole) {
    const response = await fetch('/update_role', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id: userId, role: newRole })
    });

    if (response.ok) {
        alert('Rol başarıyla güncellendi.');
        loadUsers(); // Tabloyu güncelle
    } else {
        alert('Rol güncellenemedi.');
    }
}

window.onload = function() {
    fetch('/get_users')
        .then(response => response.json())
        .then(users => {
            const tableBody = document.getElementById('userTable').getElementsByTagName('tbody')[0];
            users.forEach(user => {
                const row = tableBody.insertRow();
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                    <td>${user.email}</td>
                    <td>${user.tel}</td>
                    <td>${user.role}</td>
                    <td><button onclick="updateRole(${user.id})">Rol Güncelle</button></td>
                `;
            });
        });
}

function updateRole(userId) {
    const newRole = prompt("Yeni rolü girin:");
    if (newRole) {
        fetch('/update_role', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: userId, role: newRole })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Rol başarıyla güncellendi!');
                window.location.reload();
            } else {
                alert('Rol güncelleme hatası');
            }
        });
    }
}


function askiyaAl(rezervasyonID) {
    fetch(`/askiya_al/${rezervasyonID}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Rezervasyon askıya alındı!');
            window.location.reload(); // Sayfayı yeniden yükle
        } else {
            alert('Bir hata oluştu, tekrar deneyin.');
        }
    });
}

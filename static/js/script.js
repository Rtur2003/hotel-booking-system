// Kayıt işlemini dinleyen event listener
document.getElementById('register').addEventListener('submit', function (event) {
    event.preventDefault(); // Sayfanın yeniden yüklenmesini engeller

    // Form alanlarındaki değerleri al
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    const password2 = document.getElementById('reg-password2').value;
    const email = document.getElementById('email').value.trim();
    const tel = document.getElementById('reg-tel').value.trim();

    // Form alanlarının doluluğunu kontrol et
    if (!username || !password || !password2 || !email || !tel) {
        alert('Tüm alanları doldurmanız gerekiyor!');
        return;
    }

    // Şifrelerin eşleşip eşleşmediğini kontrol et
    if (password !== password2) {
        alert('Şifreler uyuşmuyor!');
        return;
    }

    // Kayıt isteği gönder
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password, password2, email, tel })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Sunucudan gelen mesajı göster
        if (data.message === "Kayıt başarılı!") {
            toggleForms(); // Giriş formuna geçiş yap
        }
    })
    .catch(error => {
        console.error('Hata:', error);
        alert(error.message || 'Sunucuyla bağlantı kurarken hata oluştu!');
    });
});

// Giriş işlemi
document.getElementById('login').addEventListener('submit', function (event) {
    event.preventDefault(); // Sayfanın yeniden yüklenmesini engeller

    // Form alanlarındaki değerleri al
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    // Kullanıcı adı ve şifrenin doluluğunu kontrol et
    if (!username || !password) {
        alert('Kullanıcı adı ve şifre gerekli!');
        return;
    }

    // Giriş isteği gönder
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Sunucudan gelen mesajı göster
        if (data.redirect) {
            // Flask yönlendirmesini kullanarak sayfayı yönlendir
            window.location.href = data.redirect;  // Ana sayfaya yönlendir
        }
    })
    .catch(error => {
        console.error('Hata:', error);
        alert('Sunucuyla bağlantı kurarken hata oluştu!');
    });
});

// Şifre Gösterme Butonu
function togglePasswordVisibility() {
    const passwordField = document.getElementById('password');
    const toggleButton = document.getElementById('show-password');
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';  // Şifreyi metin olarak göster
        toggleButton.textContent = '🙈';  // Kapalı göz simgesi
    } else {
        passwordField.type = 'password';  // Şifreyi gizle
        toggleButton.textContent = '👁️';  // Açık göz simgesi
    }
}

// Kayıt ve giriş formu geçişi
function toggleForms() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    loginForm.style.display = loginForm.style.display === 'none' ? 'block' : 'none';
    registerForm.style.display = registerForm.style.display === 'none' ? 'block' : 'none';
}

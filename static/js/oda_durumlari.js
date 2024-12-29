$(document).ready(function () {
    $('.durum-select').change(function () {
        const odaID = $(this).data('oda-id');
        const yeniDurum = $(this).val();

        $.ajax({
            url: '/guncelle_durum',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ oda_id: odaID, yeni_durum: yeniDurum }),
            success: function (response) {
                if (response.success) {
                    alert(response.message);
                }
            },
            error: function () {
                alert('Durum güncellenirken bir hata oluştu.');
            }
        });
    });
});

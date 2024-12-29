CREATE PROCEDURE sp_OdaDurumGuncelle
AS
BEGIN
    -- Oda Durumunu 'Dolu' Olarak Güncelle
    UPDATE Oda
    SET Durum = 'Dolu', 
        MisafirID = (
            SELECT TOP 1 MisafirID
            FROM (
                SELECT MisafirID 
                FROM GeçiciRezervasyon 
                WHERE GeçiciRezervasyon.OdaID = Oda.OdaID
                  AND GeçiciRezervasyon.BaslangicTarihi <= GETDATE()
                  AND GeçiciRezervasyon.BitisTarihi > GETDATE()
                UNION ALL
                SELECT MisafirID 
                FROM Rezervasyon 
                WHERE Rezervasyon.OdaID = Oda.OdaID
                  AND Rezervasyon.BaslangicTarihi <= GETDATE()
                  AND Rezervasyon.BitisTarihi > GETDATE()
            ) AS CombinedMisafir
        )
    WHERE EXISTS (
        SELECT 1
        FROM GeçiciRezervasyon gr
        WHERE gr.OdaID = Oda.OdaID
          AND gr.BaslangicTarihi <= GETDATE()
          AND gr.BitisTarihi > GETDATE()
    )
    OR EXISTS (
        SELECT 1
        FROM Rezervasyon r
        WHERE r.OdaID = Oda.OdaID
          AND r.BaslangicTarihi <= GETDATE()
          AND r.BitisTarihi > GETDATE()
    );

    -- Oda Durumunu 'Boþ' Olarak Güncelle
    UPDATE Oda
    SET Durum = 'Boþ',
        MisafirID = NULL
    WHERE NOT EXISTS (
        SELECT 1
        FROM GeçiciRezervasyon gr
        WHERE gr.OdaID = Oda.OdaID
          AND gr.BaslangicTarihi <= GETDATE()
          AND gr.BitisTarihi > GETDATE()
    )
    AND NOT EXISTS (
        SELECT 1
        FROM Rezervasyon r
        WHERE r.OdaID = Oda.OdaID
          AND r.BaslangicTarihi <= GETDATE()
          AND r.BitisTarihi > GETDATE()
    );
END;

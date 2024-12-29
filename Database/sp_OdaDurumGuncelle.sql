CREATE PROCEDURE sp_OdaDurumGuncelle
AS
BEGIN
    -- Oda Durumunu 'Dolu' Olarak G�ncelle
    UPDATE Oda
    SET Durum = 'Dolu', 
        MisafirID = (
            SELECT TOP 1 MisafirID
            FROM (
                SELECT MisafirID 
                FROM Ge�iciRezervasyon 
                WHERE Ge�iciRezervasyon.OdaID = Oda.OdaID
                  AND Ge�iciRezervasyon.BaslangicTarihi <= GETDATE()
                  AND Ge�iciRezervasyon.BitisTarihi > GETDATE()
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
        FROM Ge�iciRezervasyon gr
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

    -- Oda Durumunu 'Bo�' Olarak G�ncelle
    UPDATE Oda
    SET Durum = 'Bo�',
        MisafirID = NULL
    WHERE NOT EXISTS (
        SELECT 1
        FROM Ge�iciRezervasyon gr
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

USE FlaskCMS;
GO

-- last_login sütununu ekle
IF NOT EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'[dbo].[user]') 
    AND name = 'last_login'
)
BEGIN
    ALTER TABLE [dbo].[user]
    ADD last_login DATETIME NULL;
END
GO 
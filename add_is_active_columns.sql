-- Widget tablosuna is_active kolonu ekle
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[widget]') AND name = 'is_active')
BEGIN
    ALTER TABLE [dbo].[widget] ADD is_active BIT NOT NULL DEFAULT 1
END

-- Product tablosuna is_active kolonu ekle
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[product]') AND name = 'is_active')
BEGIN
    ALTER TABLE [dbo].[product] ADD is_active BIT NOT NULL DEFAULT 1
END

-- Service tablosuna is_active kolonu ekle
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[service]') AND name = 'is_active')
BEGIN
    ALTER TABLE [dbo].[service] ADD is_active BIT NOT NULL DEFAULT 1
END

-- BlogPost tablosuna is_active kolonu ekle
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[blog_post]') AND name = 'is_active')
BEGIN
    ALTER TABLE [dbo].[blog_post] ADD is_active BIT NOT NULL DEFAULT 1
END

-- Slide tablosuna is_active kolonu ekle
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID(N'[dbo].[slide]') AND name = 'is_active')
BEGIN
    ALTER TABLE [dbo].[slide] ADD is_active BIT NOT NULL DEFAULT 1
END 
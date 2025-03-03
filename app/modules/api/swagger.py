from flask import Blueprint, render_template, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

# Swagger UI Blueprint
SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "KolayCMS API"
    }
)

# Swagger JSON Blueprint
swagger_json_bp = Blueprint('swagger_json', __name__)

@swagger_json_bp.route('/api/swagger.json')
def swagger_json():
    swagger_doc = {
        "swagger": "2.0",
        "info": {
            "title": "KolayCMS API",
            "description": "KolayCMS için WordPress REST API uyumlu API",
            "version": "1.0.0"
        },
        "basePath": "/wp-json/api/v1",
        "schemes": [
            "http",
            "https"
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "paths": {
            "/token": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "API token al",
                    "description": "API erişimi için JWT token alır",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "Authorization",
                            "in": "header",
                            "description": "Basic auth credentials",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "token": {
                                        "type": "string"
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "Kimlik doğrulama başarısız"
                        }
                    }
                }
            },
            "/team": {
                "get": {
                    "tags": ["Ekip Üyeleri"],
                    "summary": "Tüm ekip üyelerini getir",
                    "description": "Aktif ekip üyelerinin listesini döndürür",
                    "produces": ["application/json"],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/TeamMember"
                                }
                            }
                        }
                    }
                }
            },
            "/team/{member_id}": {
                "get": {
                    "tags": ["Ekip Üyeleri"],
                    "summary": "Belirli bir ekip üyesini getir",
                    "description": "ID'ye göre ekip üyesi bilgilerini döndürür",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "member_id",
                            "in": "path",
                            "description": "Ekip üyesi ID",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "$ref": "#/definitions/TeamMember"
                            }
                        },
                        "404": {
                            "description": "Ekip üyesi bulunamadı"
                        }
                    }
                }
            },
            "/sliders": {
                "get": {
                    "tags": ["Sliderlar"],
                    "summary": "Tüm sliderları getir",
                    "description": "Aktif sliderların listesini döndürür",
                    "produces": ["application/json"],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/Slider"
                                }
                            }
                        }
                    }
                }
            },
            "/sliders/{slider_id}": {
                "get": {
                    "tags": ["Sliderlar"],
                    "summary": "Belirli bir sliderı getir",
                    "description": "ID'ye göre slider bilgilerini döndürür",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "slider_id",
                            "in": "path",
                            "description": "Slider ID",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "$ref": "#/definitions/Slider"
                            }
                        },
                        "404": {
                            "description": "Slider bulunamadı"
                        }
                    }
                }
            },
            "/corporate": {
                "get": {
                    "tags": ["Kurumsal İçerik"],
                    "summary": "Tüm kurumsal içerikleri getir",
                    "description": "Yayınlanmış kurumsal içeriklerin listesini döndürür",
                    "produces": ["application/json"],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/CorporateContent"
                                }
                            }
                        }
                    }
                }
            },
            "/corporate/{content_id}": {
                "get": {
                    "tags": ["Kurumsal İçerik"],
                    "summary": "Belirli bir kurumsal içeriği getir",
                    "description": "ID'ye göre kurumsal içerik bilgilerini döndürür",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "content_id",
                            "in": "path",
                            "description": "İçerik ID",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "$ref": "#/definitions/CorporateContent"
                            }
                        },
                        "404": {
                            "description": "İçerik bulunamadı"
                        }
                    }
                }
            },
            "/corporate/slug/{slug}": {
                "get": {
                    "tags": ["Kurumsal İçerik"],
                    "summary": "Slug'a göre kurumsal içeriği getir",
                    "description": "Slug'a göre kurumsal içerik bilgilerini döndürür",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "slug",
                            "in": "path",
                            "description": "İçerik Slug",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "$ref": "#/definitions/CorporateContent"
                            }
                        },
                        "404": {
                            "description": "İçerik bulunamadı"
                        }
                    }
                }
            },
            "/reports": {
                "get": {
                    "tags": ["Raporlar"],
                    "summary": "Tüm raporları getir",
                    "description": "Yayınlanmış raporların listesini döndürür",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "category",
                            "in": "query",
                            "description": "Kategori filtresi",
                            "required": False,
                            "type": "string"
                        },
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Sayfa numarası",
                            "required": False,
                            "type": "integer",
                            "default": 1
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "description": "Sayfa başına öğe sayısı",
                            "required": False,
                            "type": "integer",
                            "default": 10
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/Report"
                                }
                            },
                            "headers": {
                                "X-WP-Total": {
                                    "type": "integer",
                                    "description": "Toplam öğe sayısı"
                                },
                                "X-WP-TotalPages": {
                                    "type": "integer",
                                    "description": "Toplam sayfa sayısı"
                                }
                            }
                        }
                    }
                }
            },
            "/reports/{report_id}": {
                "get": {
                    "tags": ["Raporlar"],
                    "summary": "Belirli bir raporu getir",
                    "description": "ID'ye göre rapor bilgilerini döndürür",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "report_id",
                            "in": "path",
                            "description": "Rapor ID",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "$ref": "#/definitions/Report"
                            }
                        },
                        "404": {
                            "description": "Rapor bulunamadı"
                        }
                    }
                }
            },
            "/reports/categories": {
                "get": {
                    "tags": ["Raporlar"],
                    "summary": "Rapor kategorilerini getir",
                    "description": "Tüm rapor kategorilerini döndürür",
                    "produces": ["application/json"],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/definitions/Category"
                                }
                            }
                        }
                    }
                }
            },
            "/search": {
                "get": {
                    "tags": ["Arama"],
                    "summary": "Genel arama yap",
                    "description": "Tüm içeriklerde arama yapar",
                    "produces": ["application/json"],
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "description": "Arama sorgusu",
                            "required": True,
                            "type": "string"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Başarılı işlem",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "team": {
                                        "type": "array",
                                        "items": {
                                            "type": "object"
                                        }
                                    },
                                    "corporate": {
                                        "type": "array",
                                        "items": {
                                            "type": "object"
                                        }
                                    },
                                    "reports": {
                                        "type": "array",
                                        "items": {
                                            "type": "object"
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Geçersiz istek"
                        }
                    }
                }
            }
        },
        "definitions": {
            "TeamMember": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    },
                    "position": {
                        "type": "string"
                    },
                    "bio": {
                        "type": "string"
                    },
                    "email": {
                        "type": "string"
                    },
                    "phone": {
                        "type": "string"
                    },
                    "photo_url": {
                        "type": "string"
                    },
                    "social_media": {
                        "type": "object",
                        "properties": {
                            "facebook": {
                                "type": "string"
                            },
                            "twitter": {
                                "type": "string"
                            },
                            "instagram": {
                                "type": "string"
                            },
                            "linkedin": {
                                "type": "string"
                            }
                        }
                    },
                    "order": {
                        "type": "integer"
                    },
                    "date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "modified": {
                        "type": "string",
                        "format": "date-time"
                    }
                }
            },
            "Slider": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "title": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "image_url": {
                        "type": "string"
                    },
                    "link": {
                        "type": "string"
                    },
                    "order": {
                        "type": "integer"
                    },
                    "date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "modified": {
                        "type": "string",
                        "format": "date-time"
                    }
                }
            },
            "CorporateContent": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "title": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    },
                    "slug": {
                        "type": "string"
                    },
                    "meta": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string"
                            },
                            "keywords": {
                                "type": "string"
                            }
                        }
                    },
                    "date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "modified": {
                        "type": "string",
                        "format": "date-time"
                    }
                }
            },
            "Report": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "title": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    },
                    "category": {
                        "type": "string"
                    },
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "file_url": {
                        "type": "string"
                    },
                    "view_count": {
                        "type": "integer"
                    },
                    "date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "modified": {
                        "type": "string",
                        "format": "date-time"
                    }
                }
            },
            "Category": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "slug": {
                        "type": "string"
                    },
                    "count": {
                        "type": "integer"
                    }
                }
            }
        }
    }
    return jsonify(swagger_doc) 
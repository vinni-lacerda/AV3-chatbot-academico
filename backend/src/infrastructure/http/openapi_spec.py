"""Especificação OpenAPI 3.0.3 da API Passa o Bastão em Python puro (sem bibliotecas externas)."""

from typing import Any


def build_openapi_spec() -> dict[str, Any]:
    """Constrói o documento OpenAPI 3.0.3 completo com todos os endpoints e schemas atuais."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Passa o Bastão API",
            "version": "0.1.0",
            "description": (
                "API do chatbot Passa o Bastão para transferência de conhecimento em "
                "projetos universitários (Clean Architecture Agnóstica + SOLID + Flask + MongoDB)."
            ),
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Servidor de Desenvolvimento Local / Docker",
            }
        ],
        "tags": [
            {
                "name": "Infraestrutura",
                "description": "Monitoramento e disponibilidade do serviço.",
            },
            {
                "name": "Autenticação e Perfis (RF01)",
                "description": (
                    "Identificação de integrantes, emissão de token JWT e controle de "
                    "acesso baseado nos perfis: integrante, novo_integrante e responsavel."
                ),
            },
        ],
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Informe o access_token JWT retornado no endpoint /api/v1/auth/login.",
                }
            },
            "schemas": {
                "UserRole": {
                    "type": "string",
                    "enum": ["integrante", "novo_integrante", "responsavel"],
                    "description": "Perfil de acesso do integrante no projeto (RF01).",
                },
                "RegisterUserRequest": {
                    "type": "object",
                    "required": ["name", "email", "password"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "minLength": 2,
                            "example": "Rafael Stolf Silva",
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "example": "rafael.novo@universidade.edu.br",
                        },
                        "password": {
                            "type": "string",
                            "minLength": 8,
                            "example": "PassaOBastao123!",
                        },
                        "roles": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/UserRole"},
                            "description": "Opcional. O cadastro público atribui sempre novo_integrante.",
                            "example": ["novo_integrante"],
                        },
                        "academic_id": {
                            "type": "string",
                            "nullable": True,
                            "example": "122515186",
                        },
                    },
                },
                "LoginUserRequest": {
                    "type": "object",
                    "required": ["email", "password"],
                    "properties": {
                        "email": {
                            "type": "string",
                            "format": "email",
                            "example": "leoni@universidade.edu.br",
                        },
                        "password": {
                            "type": "string",
                            "example": "PassaOBastao123!",
                        },
                    },
                },
                "PermissionsResponse": {
                    "type": "object",
                    "required": [
                        "can_record_knowledge",
                        "can_review_knowledge",
                        "can_query_knowledge",
                    ],
                    "properties": {
                        "can_record_knowledge": {"type": "boolean", "example": True},
                        "can_review_knowledge": {"type": "boolean", "example": True},
                        "can_query_knowledge": {"type": "boolean", "example": True},
                    },
                },
                "UserResponse": {
                    "type": "object",
                    "required": [
                        "id",
                        "name",
                        "email",
                        "roles",
                        "is_active",
                        "permissions",
                        "created_at",
                    ],
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "example": "00000000-0000-4000-8000-000000000003",
                        },
                        "name": {
                            "type": "string",
                            "example": "Leoni Lucas Mascarenhas Silva",
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "example": "leoni@universidade.edu.br",
                        },
                        "roles": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/UserRole"},
                            "example": ["integrante", "responsavel"],
                        },
                        "academic_id": {
                            "type": "string",
                            "nullable": True,
                            "example": "12725156424",
                        },
                        "is_active": {"type": "boolean", "example": True},
                        "permissions": {
                            "$ref": "#/components/schemas/PermissionsResponse"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2026-11-08T16:00:00+00:00",
                        },
                    },
                },
                "AuthTokenResponse": {
                    "type": "object",
                    "required": ["access_token", "token_type", "user"],
                    "properties": {
                        "access_token": {
                            "type": "string",
                            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        },
                        "token_type": {"type": "string", "example": "bearer"},
                        "user": {"$ref": "#/components/schemas/UserResponse"},
                    },
                },
                "HealthResponse": {
                    "type": "object",
                    "required": ["status", "service"],
                    "properties": {
                        "status": {"type": "string", "example": "ok"},
                        "service": {
                            "type": "string",
                            "example": "passa-o-bastao-backend",
                        },
                    },
                },
                "ReviewCheckResponse": {
                    "type": "object",
                    "required": ["status", "user_id", "message"],
                    "properties": {
                        "status": {"type": "string", "example": "authorized"},
                        "user_id": {
                            "type": "string",
                            "example": "00000000-0000-4000-8000-000000000003",
                        },
                        "message": {
                            "type": "string",
                            "example": "Usuário possui permissão de revisão de conhecimentos.",
                        },
                    },
                },
                "ErrorResponse": {
                    "type": "object",
                    "required": ["detail", "error_code"],
                    "properties": {
                        "detail": {
                            "type": "string",
                            "example": "Descrição detalhada do erro de negócio.",
                        },
                        "error_code": {
                            "type": "string",
                            "example": "VALIDATION_ERROR",
                        },
                    },
                },
            },
        },
        "paths": {
            "/api/v1/health": {
                "get": {
                    "tags": ["Infraestrutura"],
                    "summary": "Healthcheck da API",
                    "description": "Verifica se o serviço backend está ativo e respondendo.",
                    "responses": {
                        "200": {
                            "description": "Serviço operacional",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HealthResponse"
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/v1/auth/register": {
                "post": {
                    "tags": ["Autenticação e Perfis (RF01)"],
                    "summary": "Cadastrar novo integrante no projeto (RF01)",
                    "description": (
                        "Registra um novo integrante no projeto. No cadastro público, o perfil "
                        "atribuído é sempre novo_integrante por segurança."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/RegisterUserRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Integrante cadastrado com sucesso com perfil novo_integrante",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/UserResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Erro de validação nos dados de entrada",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "409": {
                            "description": "E-mail já cadastrado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                    },
                }
            },
            "/api/v1/auth/login": {
                "post": {
                    "tags": ["Autenticação e Perfis (RF01)"],
                    "summary": "Autenticar integrante e obter token JWT (RF01)",
                    "description": (
                        "Valida e-mail e senha e retorna um Bearer Token JWT contendo os "
                        "perfis e permissões calculadas do integrante."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/LoginUserRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Autenticação realizada com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AuthTokenResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Campos obrigatórios ausentes",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "401": {
                            "description": "Credenciais inválidas ou conta inativa",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                    },
                }
            },
            "/api/v1/auth/me": {
                "get": {
                    "tags": ["Autenticação e Perfis (RF01)"],
                    "summary": "Obter dados e permissões do usuário autenticado (RF01)",
                    "description": "Retorna os dados cadastrais, perfis e permissões do portador do token JWT.",
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Dados do usuário autenticado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/UserResponse"
                                    }
                                }
                            },
                        },
                        "401": {
                            "description": "Token ausente, inválido ou expirado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                    },
                }
            },
            "/api/v1/auth/permissions/review-check": {
                "get": {
                    "tags": ["Autenticação e Perfis (RF01)"],
                    "summary": "Verificar permissão exclusiva de Responsável (RF01 / RF04)",
                    "description": (
                        "Valida o critério de aceite de controle de acesso: permite apenas "
                        "usuários com o perfil `responsavel` e retorna 403 para os demais."
                    ),
                    "security": [{"BearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "Usuário autorizado para revisão",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ReviewCheckResponse"
                                    }
                                }
                            },
                        },
                        "401": {
                            "description": "Token ausente, inválido ou expirado",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                        "403": {
                            "description": "Usuário autenticado não possui o perfil responsavel",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    }
                                }
                            },
                        },
                    },
                }
            },
        },
    }

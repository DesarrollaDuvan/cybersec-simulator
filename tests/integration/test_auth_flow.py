# tests/integration/test_auth_flow.py
import pytest


class TestAuthFlow:
    """Tests de integración para flujo de autenticación."""

    def test_register_then_login(self, client):
        """Test registro y login de usuario nuevo."""
        # Registrar
        response = client.post("/auth/register", data={
            "email": "newuser@test.com",
            "password": "testpass123",
            "name": "New User",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Cuenta creada correctamente" in response.data

        # Login
        response = client.post("/auth/login", data={
            "email": "newuser@test.com",
            "password": "testpass123",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Dashboard" in response.data or b"Bienvenido" in response.data

    def test_login_wrong_password(self, client, authenticated_user):
        """Test login con contraseña incorrecta."""
        response = client.post("/auth/login", data={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 200
        assert b"incorrectos" in response.data

    def test_login_nonexistent_user(self, client):
        """Test login con usuario inexistente."""
        response = client.post("/auth/login", data={
            "email": "nonexistent@test.com",
            "password": "testpass123",
        })
        assert response.status_code == 200
        assert b"incorrectos" in response.data

    def test_logout(self, client, authenticated_user):
        """Test logout."""
        response = client.get("/auth/logout", follow_redirects=True)
        assert response.status_code == 200
        assert b"login" in response.data.lower() or b"iniciar" in response.data.lower()

    def test_duplicate_registration(self, client, authenticated_user):
        """Test registro con email duplicado."""
        response = client.post("/auth/register", data={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Another User",
        })
        assert response.status_code == 200
        assert b"Ya existe" in response.data or b"existe" in response.data

    def test_short_password_rejected(self, client):
        """Test que rechaza contraseñas muy cortas."""
        response = client.post("/auth/register", data={
            "email": "short@test.com",
            "password": "123",
            "name": "Short Pass",
        })
        assert response.status_code == 200
        assert b"6 caracteres" in response.data or b"cort" in response.data.lower()


class TestAuthRedirects:
    """Tests de redirecciones de autenticación."""

    def test_login_page_accessible(self, client):
        """Test que página de login es accesible."""
        response = client.get("/auth/login")
        assert response.status_code == 200

    def test_register_page_accessible(self, client):
        """Test que página de registro es accesible."""
        response = client.get("/auth/register")
        assert response.status_code == 200

    def test_protected_route_redirects_to_login(self, client):
        """Test que rutas protegidas redirigen a login."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert b"login" in response.data.lower()
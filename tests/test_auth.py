import pytest
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from datetime import timedelta
import time

from fast_jwt import FastJWT

# --- Configuration de Test ---
SECRET_KEY = "JdblILESn3zwpSB8D0Yfv5y1Ff0gBTw44Weo2NQW2k0="
ALGORITHM = "HS256"
jwt_auth = FastJWT(secret_key=SECRET_KEY, algorithm=ALGORITHM)

# --- Application FastAPI de Test ---
app = FastAPI()

@app.post("/login")
def login():
    """Génère un token pour les tests."""
    user_data = {"id": 1, "role": "tester"}
    access_token = jwt_auth.create_access_token(user_id=user_data["id"], expires_delta=timedelta(minutes=5))
    return {"access_token": access_token}

@app.post("/refresh")
def refresh(new_tokens: dict = Depends(jwt_auth.refresh_token)):
    """Rafraîchit un token."""
    print(new_tokens)
    return new_tokens

@app.get("/protected-route")
def protected_route(user_id: int = Depends(jwt_auth.get_current_user)):
    """Une route protégée qui retourne le payload de l'utilisateur."""
    return {"user_payload": user_id}

@app.get("/dependency-protected")
def dependency_protected_route(payload: dict = Depends(jwt_auth.auth_required)):
    """Une route protégée par la dépendance auth_required."""
    return {"status": "ok", "payload": payload}

client = TestClient(app)

# --- Tests Unitaires ---

def test_create_and_decode_token():
    """Teste si un token est créé et décodé correctement."""
    user_id = "12345"
    token = jwt_auth.create_access_token(user_id=user_id)
    
    decoded_payload = jwt_auth._decode_token(token)
    
    assert decoded_payload["sub"] == user_id
    assert "exp" in decoded_payload

def test_token_expiration():
    """Teste si un token expire correctement."""
    user_id = "test"
    # Crée un token qui expire dans 1 seconde
    token = jwt_auth.create_access_token(user_id=user_id, expires_delta=timedelta(seconds=1))
    
    # Attendre 2 secondes pour que le token expire
    time.sleep(2)
    
    with pytest.raises(HTTPException) as excinfo:
        jwt_auth._decode_token(token)
    
    assert excinfo.value.status_code == 401
    assert "Token has expired" in excinfo.value.detail

def test_invalid_signature():
    """Teste la validation d'un token avec une signature invalide."""
    user_id = "test"
    token = jwt_auth.create_access_token(user_id=user_id)
    
    # Essayer de décoder avec une mauvaise clé secrète
    wrong_key_auth = FastJWT(secret_key="wrong-secret")
    
    with pytest.raises(HTTPException) as excinfo:
        wrong_key_auth._decode_token(token)
        
    assert excinfo.value.status_code == 401
    assert "Could not validate credentials" in excinfo.value.detail

def test_create_refresh_token():
    """Teste la création d'un refresh token."""
    user_id = "refresh_test"
    token = jwt_auth.create_refresh_token(user_id=user_id)
    
    decoded_payload = jwt_auth._decode_token(token)
    
    assert decoded_payload["sub"] == user_id
    assert decoded_payload["jwt_type"] == "refresh_token"
    assert "exp" in decoded_payload

# --- Tests d'Intégration avec FastAPI ---

def test_get_protected_route_with_valid_token():
    """Teste l'accès à une route protégée avec un token valide."""
    user_id = "testuser"
    token = jwt_auth.create_access_token(user_id=user_id)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected-route", headers=headers)
    
    assert response.status_code == 200
    response_data = response.json()["user_payload"]
    assert response_data == user_id

def test_get_protected_route_without_token():
    """Teste l'accès à une route protégée sans token."""
    response = client.get("/protected-route")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_protected_route_with_expired_token():
    """Teste l'accès à une route protégée avec un token expiré."""
    token = jwt_auth.create_access_token(user_id="test", expires_delta=timedelta(seconds=-1))
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected-route", headers=headers)
    
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]

def test_dependency_protected_route():
    """Teste la protection via la dépendance `auth_required`."""
    user_id = "dependency_test"
    token = jwt_auth.create_access_token(user_id=user_id)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/dependency-protected", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["payload"]["sub"] == user_id

def test_refresh_token_flow():
    """Teste le flux de rafraîchissement de token."""
    user_id = "test_refresh_flow"
    
    # 1. Créer un refresh token
    refresh_token = jwt_auth.create_refresh_token(user_id=user_id, expires_delta=timedelta(minutes=10))
    print(refresh_token)
    # 2. Appeler l'endpoint de refresh
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = client.post("/refresh", headers=headers)
    
    # 3. Vérifier la réponse
    assert response.status_code == 200
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    
    # 4. Vérifier que le nouveau access token est valide
    new_access_token = new_tokens["access_token"]
    decoded_payload = jwt_auth._decode_token(new_access_token)
    assert decoded_payload["sub"] == user_id
    assert decoded_payload["jwt_type"] == "access_token"

def test_refresh_with_access_token():
    """Teste l'échec du rafraîchissement avec un access token."""
    user_id = "test_fail_refresh"
    access_token = jwt_auth.create_access_token(user_id=user_id)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/refresh", headers=headers)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token type"

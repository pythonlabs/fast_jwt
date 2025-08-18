# Fast JWT

Fast JWT est une bibliothèque d'authentification JWT simple et légère pour FastAPI. Elle fournit des dépendances faciles à utiliser pour protéger vos routes et gérer les tokens d'accès et de rafraîchissement.

## Fonctionnalités

- Création de tokens d'accès et de rafraîchissement.
- Dépendances FastAPI pour la protection des routes.
- Décodage et validation automatiques des tokens.
- Gestion de l'expiration des tokens.
- Facile à intégrer et à utiliser.

## Installation

```bash
pip install fast-jwt-auth
```

## Utilisation de base

Voici un exemple simple de la façon d'utiliser Fast JWT dans une application FastAPI.

### 1. Initialisation

Tout d'abord, créez une instance de `FastJWT` avec votre clé secrète.

```python
from fastapi import FastAPI, Depends, HTTPException
from fast_jwt import FastJWT
from datetime import timedelta

app = FastAPI()

# Initialisez FastJWT avec votre clé secrète
secret_key = "votre_cle_secrete_super_securisee"
fast_jwt = FastJWT(secret_key=secret_key)
```

### 2. Création de Tokens

Vous pouvez générer des tokens d'accès et de rafraîchissement pour un utilisateur.

```python
@app.post("/login")
def login(user_id: str):
    # Créez un token d'accès avec une expiration de 30 minutes
    access_token = fast_jwt.create_access_token(
        user_id=user_id, expires_delta=timedelta(minutes=30)
    )
    # Créez un token de rafraîchissement avec une expiration de 7 jours
    refresh_token = fast_jwt.create_refresh_token(
        user_id=user_id, expires_delta=timedelta(days=7)
    )
    return {"access_token": access_token, "refresh_token": refresh_token}
```

### 3. Protection des Routes

Utilisez la dépendance `auth_required` pour protéger vos routes. Seuls les utilisateurs avec un token d'accès valide pourront y accéder.

```python
@app.get("/protected")
def protected_route(user_id: str = Depends(fast_jwt.get_current_user)):
    return {"message": f"Bonjour, utilisateur {user_id} ! Vous avez accès à cette route."}
```

### 4. Rafraîchissement de Token

Créez une route pour permettre aux utilisateurs de rafraîchir leurs tokens d'accès en utilisant un token de rafraîchissement.

```python
@app.post("/refresh")
def refresh(new_tokens: dict = Depends(fast_jwt.refresh_token)):
    return new_tokens
```

### 5. Obtenir les informations de l'utilisateur

La dépendance `get_current_user` décode le token et retourne le `sub` (sujet), qui est généralement l'ID de l'utilisateur.

```python
@app.get("/user/me")
def read_users_me(user_id: str = Depends(fast_jwt.get_current_user)):
    return {"user_id": user_id}
```

## API de `FastJWT`

- `FastJWT(secret_key: str, algorithm: str = "HS256")`: Initialise l'instance.
- `create_access_token(user_id: str | int, expires_delta: timedelta = None) -> str`: Crée un token d'accès.
- `create_refresh_token(user_id: str | int, expires_delta: timedelta = None) -> str`: Crée un token de rafraîchissement.
- `refresh_token(...)`: Dépendance pour rafraîchir un token.
- `auth_required(...)`: Dépendance pour exiger une authentification.
- `get_current_user(...)`: Dépendance qui retourne le sujet du token.
- `get_jwt_subject(...)`: Dépendance qui retourne le sujet du token.
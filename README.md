# 🚀 Fast JWT Auth 🔒

[![PyPI version](https://badge.fury.io/py/fast-jwt-auth.svg)](https://badge.fury.io/py/fast-jwt-auth)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Fast JWT Auth  est une bibliothèque d'authentification JWT simple et légère pour FastAPI. Elle fournit des dépendances faciles à utiliser pour protéger vos routes et gérer les tokens d'accès et de rafraîchissement.

## ✨ Fonctionnalités

-   **Création de Tokens** : Générez des tokens d'accès et de rafraîchissement en une seule ligne de code.
-   **Protection de Routes** : Utilisez des dépendances FastAPI pour sécuriser vos points de terminaison.
-   **Validation Automatique** : Décodage et validation automatiques des tokens, y compris la gestion de l'expiration.
-   **Facile à Utiliser** : Conçu pour être simple et intuitif, vous permettant de sécuriser votre API en quelques minutes.

## 📦 Installation

```bash
pip install fast-jwt-auth
```
```bash
uv add fast-jwt-auth
```

## 🚀 Utilisation de base

Voici un exemple simple de la façon d'utiliser Fast JWT dans une application FastAPI.

### 1. Initialisation ⚙️

Créez une instance de `FastJWT` avec votre clé secrète.

```python
from fastapi import FastAPI, Depends
from fast_jwt import FastJWT
from datetime import timedelta

app = FastAPI()

# Initialisez FastJWT avec votre clé secrète
# ATTENTION : Ne codez jamais la clé en dur, utilisez des variables d'environnement !
secret_key = "votre_cle_secrete_super_securisee"
fast_jwt = FastJWT(secret_key=secret_key)
```

### 2. Création de Tokens 🎟️

Générez des tokens d'accès et de rafraîchissement pour un utilisateur, par exemple dans une route de connexion.

```python
@app.post("/login")
def login(LoginRequest: LoginRequest):
    # votre logique ici
    # Créez un token d'accès avec une expiration de 30 minutes
    access_token = fast_jwt.create_access_token(
        user_id=user_id, expires_delta=timedelta(minutes=30) # par defaut: 15 min
    )
    # Créez un token de rafraîchissement avec une expiration de 7 jours
    refresh_token = fast_jwt.create_refresh_token(
        user_id=user_id, expires_delta=timedelta(days=7) # par default: 3 jours
    )
    return {"access_token": access_token, "refresh_token": refresh_token}
```

### 3. Protection des Routes 🛡️

Utilisez la dépendance `auth_required` pour protéger vos routes.

```python
@app.get("/protected", dependencies=[Depends(fast_jwt.auth_required)])
def protected_route():
    return {"message": "Vous avez accès à cette route sécurisée !"}
```

### 4. Obtenir les informations de l'utilisateur 👤

La dépendance `get_current_user` décode le token et retourne le `sub` (sujet), qui est généralement l'ID de l'utilisateur.

```python
@app.get("/user/me")
def read_users_me(user_id: str = Depends(fast_jwt.get_current_user)):
    # votre logique ici
    return {"user_id": user_id}
```

### 5. Rafraîchissement de Token 🔄

Créez une route pour permettre aux utilisateurs de rafraîchir leurs tokens d'accès en utilisant un token de rafraîchissement.

```python
@app.post("/refresh")
def refresh(new_tokens: dict = Depends(fast_jwt.refresh_token)):
    return new_tokens # {"access_token": new_access_token, "refresh_token": new_refresh_token}
```

## ⚠️ Considérations de Sécurité

-   **Gestion de la `secret_key`** : La sécurité de vos tokens JWT dépend entièrement de la `secret_key`. **Ne la codez jamais en dur dans votre application !** Chargez-la depuis des variables d'environnement ou un gestionnaire de secrets.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une *issue* ou une *pull request*.

## ⚖️ Licence

Ce projet est sous licence MIT.

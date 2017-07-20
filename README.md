Configuration
=============

Tous les modules sont configuré à l'aide d'un fichier unique, ```$HOME/.pymendo.json```.

Exemple :
```json
{
  "locale": "fr_CH.utf8",
  "publish": {
    "wordpress": "http://localhost/wp",
    "auth_token": "ssWubmljazp2dUVMTsJsZ2Zas3YwOTZdZjNnV2FFVDM="
  }
}
```

|Clé|Oblig.|Description|
|---|------|-----------|
|```locale```|Non|Locale à utiliser. Par défaut, utilise la locale du système.|
|```publish```|Oui|Regroupe les éléments de configuration pour le module ```pymendopublish```.|

pymendopublish
--------------

Permet de publier le classement hebdomadaire. Tous les éléments de configuration sont regroupés sous la clé principale
```publish``` du fichier de configuration. 

|Clé|Oblig.|Description|
|---|------|-----------|
|```wordpress```|Oui|L'adresse du site WordPress|
|```auth_token```|Oui|Jeton d'identification pour l'application.|

Authentification
================

* Installer le plugin ```Application Passwords``` : https://wordpress.org/plugins/application-passwords
* Dans l'interface d'administration, créer un mot de passe d'application en se rendant sur la page de profil de 
l'utilisateur qui sera utilisé pour permettre à l'application d'accéder au contenu privé.
* Créer le jeton d'authentification avec la commande ```echo -n "USERNAME:PASSWORD" | base64```

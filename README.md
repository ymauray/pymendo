Configuration
=============

Tous les modules sont configuré à l'aide d'un fichier unique, ```$HOME/.pymendo.json```.

Exemple :
```json
{
  "locale": "fr_CH.utf8",
  "publish": {
    "wordpress_token": "ssWubmljazp2dUVMTsJsZ2Zas3YwOTZdZjNnV2FFVDM="
  }
}
```

* ```locale``` : par défaut c'est la locale du système qui est utilisé.
* ```publish``` : regroupe les éléments de configuration pour le module ```pymendopublish```.

pymendopublish
--------------

Permet de publier le classement hebdomadaire. Tous les éléments de configuration sont regroupés sous la clé principale
```publish``` du fichier de configuration. 

* ```wordpress_token``` : Jeton d'identification pour l'application.

Authentification
================

* Installer le plugin ```Application Passwords``` (https://wordpress.org/plugins/application-passwords/)
* Dans l'interface d'administration, créer un mot de passe d'application en se rendant sur la page de profil de 
l'utilisateur qui sera utilisé pour permettre à l'aopplication d'accéder au contenu privé.
* Créer le jeton d'authentification avec la commande ```echo -n "USERNAME:PASSWORD" | base64```

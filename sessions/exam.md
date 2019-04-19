# Source de données

Le *fichier de données* est [là](https://tinyurl.com/y4pflefj) (c'est un CSV).

La *description des données* (fichier TXT) est [là](https://tinyurl.com/yx92j478)

# De quoi ça parle ?

**Les bases de données est un ensemble de mesures d'activité de systèmes informatiques.**

Les données ont été collectées sur une station de stockage Sun Sparcstation 20/712 disposant de 128 Mo de mémoire s'exécutant dans un département universitaire multi-utilisateurs. Les utilisateurs effectuent généralement une grande variété de tâches, allant d’accéder à Internet, d’éditer des fichiers ou d’exécuter des programmes très liés à un processeur. Les données ont été collectées de manière continue à deux reprises. À ces deux occasions, l'activité du système était collectée toutes les 5 secondes. L'ensemble de données final est tiré des deux occasions avec un nombre égal d'observations provenant de chaque époque de collecte dans un ordre aléatoire.

# Objectif

**Prévoir la colonne *usr* en vous basant sur les colonnes 0 à 20.**

La colonne *usr* représente la portion du temps où les processeurs fonctionnent pour l'utilisateur (et pas juste pour le système).

# Etapes

1. Lire les données
2. Les vérifier et les nettoyer au besoin
3. Tester différents régresseurs pour prévoir *usr* (y compris un régresseur "idiot"). On utilisera le score R2.
4. Comprendre pourquoi si on utilise la colonne *sys* c'est trop facile.
5. Prévoir au mieux la colonne *usr* en n'utilisant que les colonnes 0 à 20 (time à freeswap).
6. Trouver les colonnes qui influencent le plus la colonne *usr*.
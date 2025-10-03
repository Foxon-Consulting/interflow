# Configuration S3 pour les Rapatriements

## Vue d'ensemble

Les rappatriements sont maintenant stockés sur Amazon S3 au lieu d'un fichier local SQLite. Cette configuration permet une meilleure scalabilité et une sauvegarde centralisée.

## Variables d'environnement obligatoires

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```bash
# Configuration de stockage
STORAGE_STRATEGY=sqlite

# Configuration AWS S3 pour les rappatriements (OBLIGATOIRES)
AWS_REGION=eu-west-1
S3_RAPPATRIMENT_FILE_PATH=s3://foxon-mane-interflow/rappatriments.db
```

⚠️ **Attention** : Les variables `AWS_REGION` et `S3_RAPPATRIMENT_FILE_PATH` sont obligatoires. L'application lèvera une erreur `ValueError` si l'une d'entre elles n'est pas définie.

### Format de S3_RAPPATRIMENT_FILE_PATH

Vous pouvez utiliser deux formats :

1. **Chemin S3 complet** (recommandé) :
   ```bash
   S3_RAPPATRIMENT_FILE_PATH=s3://foxon-mane-interflow/rappatriments.db
   ```
   Le bucket sera automatiquement extrait du chemin.

2. **Chemin relatif** (nécessite S3_BUCKET_NAME) :
   ```bash
   S3_BUCKET_NAME=interflow-rappatriements
   S3_RAPPATRIMENT_FILE_PATH=rappatriements/rappatriements.json
   ```

### Variables S3

- **`AWS_REGION`** : Région AWS où se trouve le bucket S3 (obligatoire)
- **`S3_RAPPATRIMENT_FILE_PATH`** : Chemin complet ou relatif du fichier S3 (obligatoire)
- **`S3_BUCKET_NAME`** : Nom du bucket S3 (optionnel si chemin S3 complet utilisé)

### Credentials AWS

Les credentials AWS sont gérés automatiquement par boto3 selon l'ordre de priorité suivant :
1. Variables d'environnement `AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY`
2. Fichier de credentials AWS (`~/.aws/credentials`)
3. Rôles IAM (si exécuté sur EC2/ECS/Lambda)
4. Profils AWS CLI

## Configuration AWS

### 1. Créer un bucket S3

Le bucket sera créé automatiquement lors du premier accès si les permissions le permettent. Sinon, créez-le manuellement :

```bash
aws s3 mb s3://interflow-rappatriements --region eu-west-1
```

### 2. Configuration des permissions

L'utilisateur AWS doit avoir les permissions suivantes :

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::interflow-rappatriements",
                "arn:aws:s3:::interflow-rappatriements/*"
            ]
        }
    ]
}
```

### 3. Chiffrement

Les données sont automatiquement chiffrées avec AES-256 lors du stockage.

## Structure des données S3

Les rappatriements sont stockés dans le bucket avec la structure suivante :

```
s3://interflow-rappatriements/
└── rappatriements/
    └── rappatriements.json
```

## Dépannage

### Erreur de configuration manquante
```
ValueError: S3_BUCKET_NAME est obligatoire
ValueError: AWS_REGION est obligatoire
ValueError: S3_RAPPATRIMENT_FILE_PATH est obligatoire
```
Vérifiez que les variables d'environnement `S3_BUCKET_NAME`, `AWS_REGION` et `S3_RAPPATRIMENT_FILE_PATH` sont définies dans votre fichier `.env`.

### Erreur de credentials
```
NoCredentialsError: Unable to locate credentials
```
Vérifiez que les variables d'environnement `AWS_ACCESS_KEY_ID` et `AWS_SECRET_ACCESS_KEY` sont définies et correctes.

### Erreur de permissions
```
AccessDenied: Access Denied
```
Vérifiez que l'utilisateur AWS a les permissions nécessaires pour le bucket S3.

### Erreur de région
```
IllegalLocationConstraintException
```
Vérifiez que la région AWS est correcte et que le bucket existe dans cette région.

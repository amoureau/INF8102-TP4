# INF8102-TP4 : Sécurité Infrastructure as Code

Ce dépôt implémente une approche **Infrastructure as Code (IaC)** pour mettre en place et sécuriser une architecture AWS complète.

Nous avons implémenté notre VPC, nos instances EC2, nos buckets S3 et les différents mécanismes de sécurité associés (KMS, CloudTrail, Flow Logs, CloudWatch) à l’aide de **CloudFormation** et **Troposphere** (un générateur de templates Python).

## Services et technologies

* **Outil IaC :** Troposphere (Python) pour générer les templates.
* **Orchestration :** AWS CloudFormation.
* **Services AWS implémentés :**
    * VPC (avec sous-réseaux, tables de routage, NAT Gateways)
    * EC2 (Instances)
    * S3 (Stockage)
    * KMS (Chiffrement)
    * CloudTrail (Journalisation des appels d'API)
    * VPC Flow Logs (Journalisation du trafic réseau)
    * CloudWatch (Surveillance et alertes)

## Structure du dépôt

* `./scripts/` : Contient les scripts Python (utilisant Troposphere) qui génèrent les fichiers de configuration IaC.
* `./iacconfig/` : Contient les deux fichiers de configuration complets qui reprennent toute l'infrastructure. **Ce sont ces fichiers qui ont servi au scan de sécurité.**
* `./json/` et `./yaml/` :
    * Résultats des scans (ex: `scan.json`, `cve.json`).
    * Versions antérieures ou partielles de l'architecture (ex: `vpc.yaml`, `vpc1.yaml`).

## ⚠️ Important : Configuration avant exécution

Ce projet a été réalisé en binôme. Par conséquent, les ressources AWS (clés KMS et noms de buckets S3) sont codées en dur avec nos identifiants de compte.

**Pour lancer le code sur votre propre compte AWS, vous devrez impérativement modifier ces valeurs dans les fichiers de configuration.**

### 1. Noms des Buckets S3

Les noms des buckets S3 doivent être **uniques au niveau mondial**. Vous devrez remplacer nos noms par des noms uniques de votre choix.

* `polystudents3-moureau-armbruster`
* `polystudents3-moureau-armbruster2`

### 2. ARN des clés KMS

Les ARN des clés KMS sont spécifiques à un compte AWS. Vous devrez les remplacer par l'ARN d'une clé KMS existante **dans votre propre compte AWS**.

* **Moureau :**
    ```
    arn:aws:kms:ca-central-1:871826697362:key/ff40098e-800a-4a78-af23-178809defbc8
    ```
* **Armbruster :**
    ```
    arn:aws:kms:ca-central-1:398045401924:key/39e59cc2-2bd7-45e7-87d7-439f0c62b49b
    ```

## 👥 Auteurs

* Moureau Alexandre 2486981
* Armbruster Alexandre 2484101
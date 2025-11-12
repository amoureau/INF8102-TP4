# INF8102-TP4
Ce dossier utilise une approche Infrastructure As Code (IAC) pour mettre en place et sécuriser une architecture AWS.
Nous avons implémenter notre VPC, nos instances EC2, nos buckets S3 et les différents mécanismes de sécurité associés (KMS, CloudTrail, Flow Logs, CloudWatch) à l’aide de CloudFormation et Troposphere.

Les fichiers scripts qui génèrent les fichiers de config sont dans le dossier scripts.
Le dossier iacconfig contient les deux fichiers de config complets qui reprennent toute l'infrastructure et ont servi au scan.
D'autres fichiers de config peuvent se trouver dans les dossiers json et yaml, ils correspondent soit aux résultats du scan (scan.json, cve.json), soit à des versions antérieures de l'architecture (vpc.yaml, vpc1.yaml).



Ayant travaillés à deux sur ce tp, chacun à utiliser ses ressources.
Voici les ressources que nous avons chacun utilisées et que vous devrez sûrement modifiés pour lancer le code :

Fichier json key id
Moureau: arn:aws:kms:ca-central-1:871826697362:key/ff40098e-800a-4a78-af23-178809defbc8
Armbruster: arn:aws:kms:ca-central-1:398045401924:key/39e59cc2-2bd7-45e7-87d7-439f0c62b49b

Bucket name:
Moureau: polystudents3-moureau-armbruster
Armbruster: polystudents3-moureau-armbruster2

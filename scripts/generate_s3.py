from troposphere import Template, Ref, Output
from troposphere.s3 import (
    Bucket,
    PublicAccessBlockConfiguration,
    BucketEncryption,
    ServerSideEncryptionRule,
    VersioningConfiguration,
    ServerSideEncryptionByDefault
)

t = Template()
t.set_description("TP4 - Question 2 - S3 Bucket")

kms_key_arn = "arn:aws:kms:ca-central-1:871826697362:key/ff40098e-800a-4a78-af23-178809defbc8" 

# Ajoute une ressource S3 Bucket avec les propriétés demandées
s3_bucket = t.add_resource(
    Bucket(
        "S3Bucket",

        #Propriété DeletionPolicy 
        DeletionPolicy="Retain", 

        #Propriété BucketName
        BucketName="polystudents3-moureau-armbruster",

        #Propriété AccessControl 
        AccessControl="Private",

        #Propriété VersioningConfiguration
        VersioningConfiguration=VersioningConfiguration(
            Status="Enabled"
        ),

        #Propriété PublicAccessBlockConfiguration 
        PublicAccessBlockConfiguration=PublicAccessBlockConfiguration(
            BlockPublicAcls=True,
            BlockPublicPolicy=True,
            IgnorePublicAcls=True,
            RestrictPublicBuckets=True
        ),

        #Propriété BucketEncryption 
        BucketEncryption=BucketEncryption(
            ServerSideEncryptionConfiguration=[
                ServerSideEncryptionRule(
                    ServerSideEncryptionByDefault=ServerSideEncryptionByDefault(
                        SSEAlgorithm="aws:kms",
                        KMSMasterKeyID=kms_key_arn
                    )
                )
            ]
        )
    )
)

# Ajouter une sortie
t.add_output(
    Output(
        "S3Bucket",
        Description="Bucket Created! :)",
        Value=Ref(s3_bucket)
    )
)

with open("./json/s3.json", "w") as f:
    f.write(t.to_json())

print("Fichier généré : ./json/s3.json")
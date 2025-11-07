from troposphere import Template, Ref, Output, GetAtt, Join
from troposphere.s3 import (
    Bucket,
    PublicAccessBlockConfiguration,
    BucketEncryption,
    ServerSideEncryptionRule,
    VersioningConfiguration,
    ServerSideEncryptionByDefault,
    ReplicationConfiguration,
    ReplicationConfigurationRules,
    ReplicationRuleFilter, 
    ReplicationConfigurationRulesDestination,
    DeleteMarkerReplication,
    BucketPolicy
)
from troposphere.iam import Role, Policy
from troposphere.cloudtrail import Trail, EventSelector, DataResource


t = Template()
t.set_description("TP4 - Question 2 et 3.3 - S3 Bucket")

kms_key_arn = "arn:aws:kms:ca-central-1:871826697362:key/ff40098e-800a-4a78-af23-178809defbc8" 
account_id = "871826697362"

# Bucket pour les logs d'accès
log_bucket = t.add_resource(
    Bucket(
        "S3BucketLogs",
        BucketName="polystudents3-moureau-armbruster-logs",
        AccessControl="Private",
        PublicAccessBlockConfiguration=PublicAccessBlockConfiguration(
            BlockPublicAcls=True, BlockPublicPolicy=True,
            IgnorePublicAcls=True, RestrictPublicBuckets=True
        )
    )
)

# Politique pour permettre à CloudTrail d'écrire dans le bucket de logs
log_bucket_policy = t.add_resource(
    BucketPolicy(
        "LogBucketPolicy",
        Bucket=Ref(log_bucket),
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AWSCloudTrailAclCheck",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:GetBucketAcl",
                    "Resource": GetAtt(log_bucket, "Arn")
                },
                {
                    "Sid": "AWSCloudTrailWrite",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:PutObject",
                    "Resource": Join("", [
                        GetAtt(log_bucket, "Arn"),
                        f"/AWSLogs/{account_id}/*"
                    ]),
                    "Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
                }
            ]
        }
    )
)

# Bucket destination de la réplication
backup_bucket = t.add_resource(
    Bucket(
        "S3BucketBackup",
        BucketName="polystudents3-moureau-armbruster-back",
        VersioningConfiguration=VersioningConfiguration(Status="Enabled"),
        AccessControl="Private",
        PublicAccessBlockConfiguration=PublicAccessBlockConfiguration(
            BlockPublicAcls=True, BlockPublicPolicy=True,
            IgnorePublicAcls=True, RestrictPublicBuckets=True
        ),
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

#Role IAM pour la réplication
replication_role = t.add_resource(
    Role(
        "ReplicationRole",
        AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "s3.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        },
        Policies=[
            Policy(
                PolicyName="S3ReplicationPolicy",
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:GetObjectVersion",
                                "s3:GetObjectVersionAcl"
                            ],
                            "Resource": "arn:aws:s3:::polystudents3-moureau-armbruster/*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:ReplicateObject",
                                "s3:ReplicateDelete",
                                "s3:ReplicateTags"
                            ],
                            "Resource": "arn:aws:s3:::polystudents3-moureau-armbruster-back/*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "kms:Decrypt",
                                "kms:Encrypt",
                                "kms:ReEncrypt*",
                                "kms:GenerateDataKey*",
                                "kms:DescribeKey"
                            ],
                            "Resource": kms_key_arn
                        }
                    ]
                }
            )
        ]
    )
)

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
        ),

        #Configuration de la réplication
        ReplicationConfiguration=ReplicationConfiguration(
            Role=GetAtt(replication_role, "Arn"),
            Rules=[
                ReplicationConfigurationRules(
                    Status="Enabled",
                    Priority=1,
                    Filter=ReplicationRuleFilter(
                        Prefix=""
                    ),
                    Destination=ReplicationConfigurationRulesDestination(
                        Bucket=GetAtt(backup_bucket, "Arn")
                    ),
                    DeleteMarkerReplication=DeleteMarkerReplication(Status="Disabled")
                )
            ]
        )
    )
)

# Ajout d'une ressource CloudTrail pour logger les actions sur le bucket S3
cloudtrail = t.add_resource(
    Trail(
        "S3ActivityTrail",
        TrailName="polystudents3-trail",
        S3BucketName=Ref(log_bucket),
        IsLogging=True,
        IncludeGlobalServiceEvents=False,
        IsMultiRegionTrail=False,
        EventSelectors=[
            EventSelector(
                ReadWriteType="WriteOnly", 
                IncludeManagementEvents=False,
                DataResources=[
                    DataResource(
                        Type="AWS::S3::Object",
                        Values=[Join("", [GetAtt(s3_bucket, "Arn"), "/"])]
                    )
                ]
            )
        ],
        DependsOn=log_bucket_policy.title
    )
)

# Ajout des outputs
t.add_output(
    Output(
        "S3Bucket",
        Description="Bucket Created! :)",
        Value=Ref(s3_bucket)
    )
)

t.add_output(
    Output(
        "S3BucketBackup", 
        Description="Bucket de backup pour la réplication",
        Value=Ref(backup_bucket)
    )
)

with open("./json/s3.json", "w") as f:
    f.write(t.to_json())

print("Fichier généré : ./json/s3.json")
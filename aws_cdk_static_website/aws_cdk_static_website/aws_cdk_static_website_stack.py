Here is the code with the identified issues fixed:


from aws_cdk import core


from aws_cdk import (
    aws_s3,
    aws_s3_deployment,
    aws_cloudfront
)


class AwsCdkStaticWebsiteStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create s3 bucket
        hui_static_website = aws_s3.Bucket(
            self, 
            "huibucketdemo",
            versioned=True,  
            public_read_access=True,
            website_index_document="index.html",
            website_error_document="404.html",
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # zip static webpage folder and add to bucket 
        add_assets_to_site = aws_s3_deployment.BucketDeployment(
            self,
            "deploystaticwebpage", 
            sources=[
                aws_s3_deployment.Source.asset(
                    "/Users/huiyeeleong/Desktop/hui-static-webpage/aws_cdk_static_website/static_webpage"
                )
            ],
            destination_bucket=hui_static_website
        )

        # Create Origin access identity for cloudfront
        cloudfront_oai = aws_cloudfront.OriginAccessIdentity(
            self,
            "staticsiteOAI",
            comment=f"OAI for static site from stack:{core.Aws.STACK_NAME}"
        )

        # Deploy cloudfront configuration
        cloudfront_config = aws_cloudfront.SourceConfiguration(
            s3_origin_source=aws_cloudfront.S3OriginConfig(
                s3_bucket_source=hui_static_website,
                origin_access_identity=cloudfront_oai

            ),
            behaviors=[
                aws_cloudfront.Behavior(
                    is_default_behavior=True,
                    compress=True,
                    allowed_methods=aws_cloudfront.CloudFrontAllowedMethods.ALL,
                    cached_methods=aws_cloudfront.CloudFrontAllowedCachedMethods.GET_HEAD 
                )
            ]
        )

        # Create Cloudfront Distribution 
        static_distribution = aws_cloudfront.CloudFrontWebDistribution(
            self,
            "siteDistribution",
            origin_configs=[cloudfront_config],
            price_class=aws_cloudfront.PriceClass.PRICE_CLASS_100  
        )

        # Output cloudfront url on cloudformation
        core.CfnOutput(
            self,
            "Cloudfront_URL",
            value=f"{static_distribution.domain_name}",
            description="The domain name of my static website"
        )
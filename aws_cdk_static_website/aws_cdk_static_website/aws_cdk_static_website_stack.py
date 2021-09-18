from aws_cdk import core as cdk

from aws_cdk import (
    core,
    aws_s3 as _s3,
    aws_s3_deployment as _s3_deployment,
    aws_cloudfront as _cloudfront
)


class AwsCdkStaticWebsiteStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Create s3 bucket
        hui_static_website = _s3.Bucket(
            self,
            "huibucketdemo",
            versioned=True,
            public_read_access=True,
            website_index_document="index.html",
            website_error_document="404.html",
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # zip static webpage folder and add to bucket
        # this will automatically create lambda to do it by using this _s3_deployment
        add_assets_to_site = _s3_deployment.BucketDeployment(
            self,
            "deploystaticwebpage",
            sources=[
                _s3_deployment.Source.asset(
                    "/Users/huiyeeleong/Desktop/hui-static-webpage/aws_cdk_static_website/static_webpage"
                )
            ],
            destination_bucket=hui_static_website
        )

        # create cloudfront for my webpage
        # Create Origin access identity for cloudfront
        cloudfront_oai = _cloudfront.OriginAccessIdentity(
            self,
            "staticsiteOAI",
            comment= f"OAI for static site from stack:{core.Aws.STACK_NAME}"
        )

        #Deploy cloudfront configuration 
        #Use S3 bucket as origin
        #policy for user only can access through cloudfront to access the bucket
        cloudfront_config = _cloudfront.SourceConfiguration(
            s3_origin_source = _cloudfront.S3OriginConfig(
                s3_bucket_source=hui_static_website,
                origin_access_identity=cloudfront_oai

            ),
            behaviors=[
                _cloudfront.Behavior(
                    is_default_behavior=True,
                    compress=True,
                    allowed_methods=_cloudfront.CloudFrontAllowedMethods.ALL,
                    cached_methods=_cloudfront.CloudFrontAllowedCachedMethods.GET_HEAD
                )
            ]
        )

        #Create Cloudfront Distribution
        static_distribution = _cloudfront.CloudFrontWebDistribution(
            self,
            "siteDistribution",
            comment= "CDN for static website",
            origin_configs = [cloudfront_config],
            #price class to choose 
            price_class = _cloudfront.PriceClass.PRICE_CLASS_100
        )

        #output cloudfront url on cloudformation
        output_cf = core.CfnOutput(
            self,
            "Cloudfront_URL",
            value=f"{static_distribution.domain_name}",
            description = "The domain name of my static website"
        )




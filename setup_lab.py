import boto3
import botocore
import os

def color(text: str,color: str='cyan') -> str:
    """
    colors the output to terminal -- nicer aesthetic!
    """
    
    if color =='cyan':
        r,g,b = 0,255,255
    elif color =='orange':
        r,g,b = 255,179,71
    elif color == 'green':
        r,g,b = 57,255,20
    
    return f"\033[38;2;{r};{g};{b}m{text}\033[38;2;255;255;255m"


bucket_name_parameter = 'MacieDevlabBucketName'
sensitive_data_folder = 'test-data'

ssm_client = boto3.client('ssm')
s3_client = boto3.client('s3')
macie_client = boto3.client('macie2')


bucket_name = ssm_client.get_parameter(
    Name=bucket_name_parameter
)['Parameter']['Value']
bucket_location = s3_client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
if bucket_location is None:
    bucket_location = 'us-east-1'
print(f"Bucket with test data is {color(bucket_name)} in the {color(bucket_location,color='orange')} region")
macie_console_link = f"https://{bucket_location}.console.aws.amazon.com/macie/home?region={bucket_location}"


list_files = os.listdir(sensitive_data_folder)
for file_name in list_files:
    response = s3_client.upload_file(f"./{sensitive_data_folder}/{file_name}", bucket_name, file_name)
print(f"Uploaded test data to {color(bucket_name)} bucket")


try:
    macie_client.disable_macie()
    print("Disabled installation of Macie from previous Lab Participant")
except macie_client.exceptions.from_code('AccessDeniedException') as e:
    print(e.response['Error']['Message'])
macie_client.enable_macie()
response = macie_client.get_macie_session()
macie_client.create_custom_data_identifier(
    description='Passport number of Gotham Citizens',
    keywords=[
        'passport',
    ],
    maximumMatchDistance=50,
    name='Gotham Passport',
    regex='[ABCDEF]\\d{7}[A-Z]',
    severityLevels=[
        {
            'occurrencesThreshold': 1,
            'severity': 'HIGH'
        },
    ]
)


if response['status'] == 'ENABLED':
    print("Macie enabled!\n\n")
    print(f"🚀 {color('You are ready to go',color='green')} 🚀")
    print(f"Click this link, and then click open to continue to Macie: {color(macie_console_link, color='cyan')}")
    print("\n\n")
else:
    print("Error enabling Macie, please check with the lab organizer")
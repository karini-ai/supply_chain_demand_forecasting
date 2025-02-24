# Use AWS-provided Python 3.12 Lambda base image
FROM public.ecr.aws/lambda/python:3.12

# Install required dependencies
RUN pip install --upgrade pip \
    && pip install boto3 pandas nixtla --no-cache-dir

# Copy Lambda function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/

# Set the command to the Lambda handler
CMD ["lambda_function.lambda_handler"]

# Use AWS Lambda Python 3.12 base image
FROM public.ecr.aws/lambda/python:3.12

# Install dependencies
RUN pip install psycopg2-binary boto3 python-docx

# Copy function code into container
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the handler
CMD ["lambda_function.lambda_handler"]

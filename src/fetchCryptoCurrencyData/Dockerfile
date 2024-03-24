FROM public.ecr.aws/lambda/python:3.11

# To copy into the docker container the list of projects deps
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# To install the list of deps into the container
RUN pip install -r requirements.txt

# To copy all the source code needed to execute the lambda function
COPY . ${LAMBDA_TASK_ROOT}

# set the CMD to default execute the lambda function
CMD [ "main.handler" ]
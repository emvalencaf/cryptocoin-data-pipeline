# CryptoCoin Data Pipeline

## Summary

- [Documentation (Brazilian Portuguese)](/README.md#documentação)
    - [Sumário da Documentação](/README.md#sumário-da-documentação)
    - [Sobre o Projeto](/README.md#sobre-o-projeto)
    - [A Arquitetura do Projeto](/README.md#a-arquitetura-do-projeto)
    - [Como Usar](/README.md#como-usar)
    - [Fontes](/README.md#fontes)
- [Documentation (USA English)](/README.md#documentation)
    - [Documentation Summary](/README.md#documentation-summary)
    - [About the Project](/README.md#about-the-project)
    - [Project Architecture](/README.md#project-architecture)
    - [How to use](/README.md#how-to-use)
    - [Sources](/README.md#sources)

## Documentation

### Documentation Summary

- [Source Code: Fetch Crypto Currency Data](/src/fetchCryptoCurrencyData/README.md)
    - [About the Source Code](/src/fetchCryptoCurrencyData/README.md#about-the-source-code)
    - [About the Source Code Architecture](/src//fetchCryptoCurrencyData/README.md#about-the-source-code-architecture)
        - [AWS Lambda Function and AWS Infrastructure](/src/fetchCryptoCurrencyData/README.md#aws-lambda-function-and-aws-infrastructure)
        - [AWS IAM Policy](/src/fetchCryptoCurrencyData/README.md#aws-iam-policy)
        - [Environment Variables](/src/fetchCryptoCurrencyData/README.md#environment-variables)
        - [Code Operation](/src/fetchCryptoCurrencyData/README.md#code-operation)
- [Source Code: Glueing Crypto Currency Data](/src/glueingCryptoCurrencyData/README.md)
    - [About the Source Code](/src/glueingCryptoCurrencyData/README.md#about-the-source-code)
    - [About the Source Code Architecture](/src//glueingCryptoCurrencyData/README.md#about-the-source-code-architecture)
        - [AWS Glue Jobs and AWS Infrastructure](/src/glueingCryptoCurrencyData/README.md#aws-lambda-function-and-aws-infrastructure)
        - [AWS IAM Policy](/src/glueingCryptoCurrencyData/README.md#aws-iam-policy)
        - [Code Operation](/src/glueingCryptoCurrencyData/README.md#code-operation)
            - [Processing CryptoCurrency Data](/src/glueingCryptoCurrencyData/README.md#processing-cryptocurrency-data)
            - [Refining CryptoCurrency Data](/src/glueingCryptoCurrencyData/README.md#refining-cryptocurrency-data)
- [Source Code: Handle AWS Infrastructure](/src/handleAWSInfrastructure/README.md)
    - [About the Source Code](/src/fetchCryptoCurrencyData/README.md#about-the-source-code)
    - [About the Source Code Architecture](/src//fetchCryptoCurrencyData/README.md#about-the-source-code-architecture)


### About the Project

The `CryptoCoin Data Pipeline` project carries out an automated process of extraction, loading, and transformation (ELT - *Extract Load and Transform*) of data from the [CoinCap v. 2](https://docs.coincap.io/) API.

The main objective of the project is for educational purposes in using AWS services for data engineering projects. This data can be consumed to create a dashboard or assist *tradebots* operating with cryptocurrency assets.

### Project Architecture

The AWS architecture used prioritizes serverless services, including AWS Lambda, Amazon S3, AWS Glue Job, AWS Glue Data Catalog, AWS Lakeformation, Amazon EventBridge, AWS Step Functions, and Amazon Elastic Container Registry.

As illustrated in the diagram below:
![Project AWS Architecture Diagram](/docs/AWSDiagram.jpg)

1. AWS Step Functions are triggered periodically through `Amazon EventBridge Schedule`.

2. AWS Step Functions have 4 stages:

    1. It invokes the AWS Lambda [fetchCryptoCurrencyData](/src/fetchCryptoCurrencyData/README.md) to ingest data from the [CoinCap v. 2]() API and pass to the next AWS Lambda ([glueingCryptoCurrencyData](/src/glueingCryptoCurrencyData/README.md)) a `payload` with the following structure:

    ```
    {
        "bucket_name": "project_bucket", # name of the bucket where the data will be ingested
        "zone": "Raw", # names of the zones where the data will be stored, they are: Raw, Trusted, and Refined
        "objects_uploaded": "/Assets/2024/02/20/{timestamp}-batch_1.json,/Rates/2024/02/20/{timestamp}-batch_1.json" # list with the name of the objects that were uploaded in the structure {endpoint}/{year}/{month}/{day}/{timestamp}-batch_{nº batch}.{fileType}
    }
    ```

    2. It invokes the AWS Lambda [glueingCryptoCurrencyData](/src/glueingCryptoCurrencyData/README.md) and, based on the *payload*, processes and stores the data differently.

    3. If the `zone` attribute corresponds to the value `Raw`, the AWS Glue Job [processingData](/src/glueingCryptoCurrencyData/glueJobs/treatingCryptoCurrencyData/) is invoked to process the data and store it in the `Trusted` zone, updating the `payload`.

    4. It invokes the AWS Lambda [glueingCryptoCurrencyData](/src/glueingCryptoCurrencyData/README.md) and, if the `zone` attribute corresponds to the value `Trusted`, the AWS Glue Job [refiningData](/src/glueingCryptoCurrencyData/glueJobs/refiningCryptoCurrencyData/) is invoked.

![AWS Diagram: Step Function](/docs/handleAWSInfrastructure/AWSDiagram!StepFunction.png)

3. The AWS Lambda functions (source code and dependencies - *layer*) are stored in a Docker image in `Amazon S3` and `Amazon Elastic Container Registry`.

4. The AWS Glue Job functions are stored in a `code/glue_job/` zone of the bucket.

5. The AWS Glue Crawler is triggered when an Amazon S3 Event Notification is emitted upon uploading data in the `/Refined` zone.

6. The database permissions are managed by AWS LakeFormation and the metadata is managed by AWS Glue Data Catalog.

7. The data is accessed through Amazon Athena.

### How to Use

1. Before deploying the infrastructure, it is necessary to configure access credentials in the [AWS CLI](https://aws.amazon.com/cli/) using the command: `aws configure`

2. With the terminal open in the project root, navigate to the root of the `handleAWSInfrastructure` module.

3. Then, perform bootstrapping in the region where the infrastructure will be implemented using the following command `cdk bootstrap --region <region>`

3. To implement, simply type the command `cdk deploy`

4. When it is necessary to delete the infrastructure, type the command: `cdk destroy` and `aws cloudformation delete-stack --stack-name CDKToolkit --region us-east-1`.

5. As a precaution, go to the console and delete all resources, both if it is successful and unsuccessful.

### Sources

- How to use Docker to build and deploy AWS infrastructure via source code: [click here](https://dev.to/aws-builders/how-to-make-a-docker-build-image-for-the-python-flavor-of-aws-cdk-for-people-who-dont-like-npm-4nfk)

- How to deploy AWS Glue resources:

    1. AWS CDK — Deploy Managed ETL using AWS Glue job - [click here](https://medium.com/@kargawal.abhishek/aws-cdk-deploy-managed-etl-using-aws-glue-job-1925098ec40f)

    2. Serverless Data Pipeline Using AWS Glue and AWS CDK (Python) - [click here](https://medium.com/codex/data-pipeline-using-aws-glue-with-aws-cdk-python-ff2cd4ea18a1)

## Documentação

### Sumário da Documentação

- [Código Fonte: Fetch Crypto Currency Data](/src/fetchCryptoCurrencyData/README.md)
    - [Sobre o Código Fonte](/src/fetchCryptoCurrencyData/README.md#sobre-o-código-fonte)
    - [Sobre a Arquitetura do Código Fonte](/src//fetchCryptoCurrencyData/README.md#sobre-a-arquitetura-do-código-fonte)
        - [Função do AWS Lambda e a Infraestrutura da AWS](/src/fetchCryptoCurrencyData/README.md#função-do-aws-lambda-e-a-infraestrutura-da-aws)
        - [AWS IAM Policy](/src/fetchCryptoCurrencyData/README.md#aws-iam-policy)
        - [As variáveis de ambiente](/src/fetchCryptoCurrencyData/README.md#as-variáveis-de-ambiente)
        - [Operação do código](/src/fetchCryptoCurrencyData/README.md#operação-do-código)
- [Código Fonte: Glueing Crypto Currency Data](/src/glueingCryptoCurrencyData/README.md)
    - [Sobre o Código Fonte](/src/glueingCryptoCurrencyData/README.md#sobre-o-código-fonte)
    - [Sobre a Arquitetura do Código Fonte](/src//glueingCryptoCurrencyData/README.md#sobre-a-arquitetura-do-código-fonte)
        - [Função do AWS Lambda e a Infraestrutura da AWS](/src/glueingCryptoCurrencyData/README.md#função-do-aws-lambda-e-a-infraestrutura-da-aws)
        - [AWS IAM Policy](/src/glueingCryptoCurrencyData/README.md#aws-iam-policy)
        - [As variáveis de ambiente](/src/glueingCryptoCurrencyData/README.md#as-variáveis-de-ambiente)
        - [Operação do código](/src/glueingCryptoCurrencyData/README.md#operação-do-código)
- [Código Fonte: Handle AWS Infrastructure](/src/handleAWSInfrastructure/README.md)
    - [Sobre o Código Fonte](/src/fetchCryptoCurrencyData/README.md#sobre-o-código-fonte)
    - [Sobre a Arquitetura do Código Fonte](/src//fetchCryptoCurrencyData/README.md#sobre-a-arquitetura-do-código-fonte)

### Sobre o Projeto

O projeto `CryptoCoin Data Pipeline` realiza um processo automatizado de extração, carregamento e transformação (ELT - *Extract Load and Transform*) de dados provenientes da API [CoinCap v. 2](https://docs.coincap.io/).

O objetivo principal do projeto é proporcionar aprendizado no uso dos serviços da AWS para projetos de engenharia de dados. Esses dados podem ser utilizados para criar um *dashboard* ou auxiliar um *tradebot* que opera com ativos de criptomoedas.

### Arquitetura do Projeto

A arquitetura da AWS utilizada prioriza serviços *serverless*, tais como: AWS Lambda, Amazon S3, AWS Glue Job, AWS Glue Data Catalog, AWS Lakeformation, Amazon EventBridge, AWS Step Functions e Amazon Elastic Container Registry.

Conforme ilustrado no diagrama abaixo:
![Diagrama da Arquitetura da AWS do Projeto](/docs/AWSDiagram.jpg)

1. O AWS Step Functions é disparado periodicamente por meio do `Amazon EventBridge Schedule`.

2. O AWS Step Functions possui 4 etapas:

    1. Invoca a AWS Lambda [fetchCryptoCurrencyData](/src/fetchCryptoCurrencyData/README.md) para ingerir os dados da API [CoinCap v. 2](https://docs.coincap.io/) e passar para a próxima AWS Lambda ([glueingCryptoCurrencyData](/src/glueingCryptoCurrencyData/README.md)) um `payload` com a seguinte estrutura:

    ```
    {
        "bucket_name": "project_bucket", # nome do bucket onde os dados serão ingeridos
        "zone": "Raw", # nome das zonas onde os dados serão armazenados, sendo: Raw, Trusted e Refined
        "objects_uploaded": "/Assets/2024/02/20/{timestamp}-batch_1.json,/Rates/2024/02/20/{timestamp}-batch_1.json" # lista com o nome dos objetos que foram carregados na estrutura {endpoint}/{year}/{month}/{day}/{timestamp}-batch_{nº batch}.{fileType}
    }
    ```

    2. Invoca a AWS Lambda [glueingCryptoCurrencyData](/src/glueingCryptoCurrencyData/README.md) que, a partir do *payload*, processará e armazenará os dados de forma diferente.

    3. Se o atributo `zone` corresponder ao valor `Raw`, será invocado o AWS Glue Job [processingData](/src/glueingCryptoCurrencyData/glueJobs/treatingCryptoCurrencyData/) que processará os dados e os armazenará na zona `Trusted`, atualizando o `payload`.

    4. Invoca a AWS Lambda [glueingCryptoCurrencyData](/src/glueingCryptoCurrencyData/README.md) e, se o atributo `zone` corresponder ao valor `Trusted`, será invocado o AWS Glue Job [refiningData](/src/glueingCryptoCurrencyData/glueJobs/refiningCryptoCurrencyData/).

![AWS Diagram: Step Function](/docs/handleAWSInfrastructure/AWSDiagram!StepFunction.png)

3. As funções da AWS Lambda (seu código-fonte e dependências - *layer*) são armazenadas em uma imagem Docker no `Amazon S3` e no `Amazon Elastic Container Registry`.

4. As funções do AWS Glue Job estão armazenadas na zona `code/glue_job/` do *bucket*.

5. O AWS Glue Crawler é disparado quando uma Notificação de Evento do Amazon S3 é emitida ao fazer *upload* de dados na zona `/Refined`.

6. O banco de dados tem as permissões gerenciadas pelo AWS LakeFormation, e os metadados são gerenciados pelo AWS Glue Data Catalog.

7. Os dados podem ser acessados pelo Amazon Athena. 

### Como Usar

1. Antes de fazer o *deploy* da infraestrutura, é necessário configurar as credenciais de acesso no [AWS CLI](https://aws.amazon.com/pt/cli/) por meio do comando: `aws configure`.

2. Com o terminal aberto na raiz do projeto, é necessário navegar até a raiz do módulo `handleAWSInfrastructure`.

3. Em seguida, é necessário realizar o `bootstrapping` na região em que a infraestrutura será implementada por meio do seguinte comando: `cdk bootstrap --region <região>`.

3. Para realizar a implementação, basta digitar o comando `cdk deploy`.

4. Quando for necessário excluir a infraestrutura, deve-se digitar o comando: `cdk destroy` e `aws cloudformation delete-stack --stack-name CDKToolkit --region us-east-1`.

5. Por precaução, vá ao console e exclua todos os recursos tanto se for bem-sucedido quanto mal-sucedido. 

### Fontes

- Como usar o Docker para construir e fazer o *deploy* de estrutura AWS via código-fonte: [clique aqui](https://dev.to/aws-builders/how-to-make-a-docker-build-image-for-the-python-flavor-of-aws-cdk-for-people-who-dont-like-npm-4nfk)

- Como fazer o *deploy* de um recurso do AWS Glue:

    1. AWS CDK — Deploy Managed ETL using AWS Glue job - [clique aqui](https://medium.com/@kargawal.abhishek/aws-cdk-deploy-managed-etl-using-aws-glue-job-1925098ec40f)

    2. Serverless Data Pipeline Using AWS Glue and AWS CDK (Python) - [clique aqui](https://medium.com/codex/data-pipeline-using-aws-glue-with-aws-cdk-python-ff2cd4ea18a1)
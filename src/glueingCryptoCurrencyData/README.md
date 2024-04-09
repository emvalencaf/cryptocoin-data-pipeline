# Glueing Crypto Currency Data

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


### About the Source Code

The `Glueing Crypto Currency Data` component is responsible for integrating data within the `/Raw` zone by processing and refining ingested data from [CoinBase v. 2](https://docs.coincap.io/).

### About the Source Code Architecture

The `Glueing Crypto Currency Data` component is composed of two `AWS Glue Jobs`: [Processing Crypto Currency Data](/src/glueingCryptoCurrencyData/glueJobs/processingCryptoCurrencyData/main.py) and [Refining Crypto Currency Data](/src/glueingCryptoCurrencyData/glueJobs/refiningCryptoCurrencyData/main.py).

The `Processing Crypto Currency Data` script performs an ETL targeting the `/Raw` zone from a specified *bucket*, transforming the data, and then loading it into the `/Trusted` zone within that same *bucket*.

The `Refining Crypto Currency Data` script performs an ETL targeting the `/Trusted` zone from a specified *bucket*, transforming the data, and then loading it into the `/Refined` zone within that same *bucket*.

#### AWS Glue Jobs and AWS Infrastructure

The `Glueing Crypto Currency Data` component is integrated into the AWS infrastructure as illustrated in the following diagram:

![AWS Diagram](/docs/glueingCryptoCurrencyData/AWSDiagram!ETLJobs.jpg)

1. The AWS Jobs are dispatched within a Step Functions routine.

2. Once the Step Functions workflow is dispatched, the AWS Lambda [Fetch Crypto Currency Data](/src/fetchCryptoCurrencyData/README.md) will execute and pass the following job parameters as arguments:

```
# @params: [JOB_NAME,
#           S3_BUCKET_NAME        || the S3 bucket where the objects were uploaded
#           S3_INPUT_ZONE         || the S3 bucket zone where the objects were uploaded
#           S3_TARGET_ZONE        || the S3 bucket zone where the processed data wil be uploaded
#           S3_ZONE_ENDPOINTS_DIR || The directories in bucket zone where the object were uploaded, ex.: ENDPOINT1, ENDPOINT2
#           OBJECTS_KEY           || The objects_key_prefix are a list of objects, ex: Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}, Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}, Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}
#           ]
```

3. The first AWS Glue Job will be `Processing Crypto Currency Data`, which will:
   - Extract data from `/Raw`
   - Rename columns
   - Convert string types into decimal types
   - Load data into `/Trusted`

4. The last AWS Glue Job, `Refining CryptoCurrency Data`, will be dispatched once the `Processing CryptoCurrency Data` has been successfully completed. `Refining Crypto Currency Data` will:
   - Extract data from `Trusted`
   - Create `Currency` Entity
   - Create `Crypto_Data` Entity
   - Create `Currency_Value` Entity
   - Load data into `/Refined`

##### AWS IAM Policy

- The required AWS IAM Policy for `Processing Crypto Currency Data` is:

```
{
"sid": "{aws glue role}"
"Effect": "Allow",
"Action": ["s3:ReadObject"],
"Resource": "arn:aws:s3:::{bucket_name}/Raw/*"
}
```

```
{
"sid": "{aws glue role}"
"Effect": "Allow",
"Action": ["s3:PutObject"],
"Resource": ["arn:aws:s3:::{bucket_name}/Trusted/*"]
}
```

- The required AWS IAM Policy for `Refining Crypto Currency Data` is:

```
{
"sid": "{aws glue role}"
"Effect": "Allow",
"Action": ["s3:ReadObject"],
"Resource": ["arn:aws:s3:::{bucket_name}/Trusted/*",
             "arn:aws:s3:::{bucket_name}/Refined/*"]
}
```

```
{
"sid": "{aws glue role}"
"Effect": "Allow",
"Action": ["s3:PutObject"],
"Resource": ["arn:aws:s3:::{bucket_name}/Refined/*"]
}
```

#### Code Operation

##### Processing CryptoCurrency Data

The operation of the `Processing CryptoCurrency Data` AWS Glue job can be illustrated with the following activity diagram:

![Activity Diagram: Processing CrytoCurrency Data](/docs/glueingCryptoCurrencyData/ActivityDiagram!Processing%20Data.jpg)

1. The ``/Raw``zone follows this structure:

```
Bucket
├── Raw
│   └──── JSON
│           └── {Endpoint}
│                   └── {Year} (ex. 2024)
│                         └── {Month} (ex. 04)
│                               └── {Day} (ex. 04)
```

2. The ``Processing CryptoCurrency Data`` job will scrape the ``subdirs`` within ``/Raw/JSON`` according to the ``subdir date`` and ``endpoint``.

3. The extracted data will have its columns renamed, and the decimal strings will be converted into decimals.

4. The processed data will be loaded into the ``/Trusted`` zone following this structure:

```
Bucket
├── Trusted
│   └── {Endpoint}
│           └── {Year}
│                 └── {Month}
│                       └── {Day}
│                            └── {Timestamp}
```

The code operates as illustrated below:
![Diagram Sequence: Processing CryptoCurrency Data](/docs/glueingCryptoCurrencyData/SequenceDiagram!ProcessingData.jpg)

#### Refining CryptoCurrency Data

The operation of the ``Refining CryptoCurrency Data`` AWS Glue job can be illustrated with the following activity diagram:

![Activity Diagram: Refining CrytoCurrency Data](/docs/glueingCryptoCurrencyData/ActivityDiagram!RefiningData.jpg)

1. The ``/Trusted`` zone follows this structure:

```
Bucket
├── Trusted
│   └── {Endpoint}
│           └── {Year}
│                 └── {Month}
│                       └── {Day}
│                            └── {Timestamp}
```

2. The ``Refining Crypto Currency Data`` job will scrape data in ``/Trusted`` according to the ``subdir date``, ``subdir timestamp``, and ``endpoint``.

3. The extracted data will be shaped into ``Currency``, ``Currency_Value``, and ``Crypto_Data`` entities. 

4. When dealing with the ``Currency`` entity data, the job will extract the data that already exists within the ``/Refined`` zone and compare it to the current one. If there is no new data, the ``Currency`` entity's data will not be updated.
    - Note: The ``Currency`` entity contains data about the ``fiat`` and ``crypto`` currencies, so there is no need to load more data more frequently.

4. The processed data will be loaded into the ``/Refined`` zone following this structure:

```
Bucket
├── Refined
│   └── {Endpoint}
│           └── {Year}
│                 └── {Month}
│                       └── {Day}
│                            └── {Timestamp}
```

The code operates as illustrated below:
![Diagram Sequence: Processing CryptoCurrency Data](/docs/glueingCryptoCurrencyData/SequenceDiagram!ProcessingData.jpg)

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
        - [AWS Glue Jobs e Infraestrutura AWS](/src/glueingCryptoCurrencyData/README.md#aws-glue-jobs-e-infraestrutura-aws)
        - [AWS IAM Policy](/src/glueingCryptoCurrencyData/README.md#aws-iam-policy-1)
        - [Operação de Código](/src/glueingCryptoCurrencyData/README.md#operação-de-código)
            - [Processing CryptoCurrency Data](/src/glueingCryptoCurrencyData/README.md#processing-cryptocurrency-data-1)
            - [Refining CryptoCurrency Data](/src/glueingCryptoCurrencyData/README.md#refining-cryptocurrency-data-1)
- [Código Fonte: Handle AWS Infrastructure](/src/handleAWSInfrastructure/README.md)
    - [Sobre o Código Fonte](/src/fetchCryptoCurrencyData/README.md#sobre-o-código-fonte)
    - [Sobre a Arquitetura do Código Fonte](/src//fetchCryptoCurrencyData/README.md#sobre-a-arquitetura-do-código-fonte)


### Sobre o Código Fonte

O componente `Glueing Crypto Currency Data` é responsável por integrar dados na zona `/Raw` ao processar e refinar dados ingestados do [CoinBase v. 2](https://docs.coincap.io/).

### Sobre a Arquitetura do Código Fonte

O componente `Glueing Crypto Currency Data` é composto por dois `AWS Glue Jobs`: [Processing Crypto Currency Data](/src/glueingCryptoCurrencyData/glueJobs/processingCryptoCurrencyData/main.py) e [Refining Crypto Currency Data](/src/glueingCryptoCurrencyData/glueJobs/refiningCryptoCurrencyData/main.py).

O script `Processing Crypto Currency Data` executa um ETL visando a zona `/Raw` de um *bucket* especificado, transformando os dados e então carregando-os na zona `/Trusted` dentro do mesmo *bucket*.

O script `Refining Crypto Currency Data` executa um ETL visando a zona `/Trusted` de um *bucket* especificado, transformando os dados e então carregando-os na zona `/Refined` dentro do mesmo *bucket*.

#### AWS Glue Jobs e Infraestrutura AWS

O componente `Glueing Crypto Currency Data` está integrado na infraestrutura AWS conforme ilustrado no seguinte diagrama:

![Diagrama AWS](/docs/glueingCryptoCurrencyData/AWSDiagram!ETLJobs.jpg)

1. Os jobs AWS são despachados dentro de uma rotina de Step Functions.

2. Uma vez que o fluxo de trabalho Step Functions é ativado, a AWS Lambda [Fetch Crypto Currency Data](/src/fetchCryptoCurrencyData/README.md) será executada e passará os seguintes parâmetros de job como argumentos:

```
# @params: [JOB_NAME,
#           S3_BUCKET_NAME        || the S3 bucket where the objects were uploaded
#           S3_INPUT_ZONE         || the S3 bucket zone where the objects were uploaded
#           S3_TARGET_ZONE        || the S3 bucket zone where the processed data wil be uploaded
#           S3_ZONE_ENDPOINTS_DIR || The directories in bucket zone where the object were uploaded, ex.: ENDPOINT1, ENDPOINT2
#           OBJECTS_KEY           || The objects_key_prefix are a list of objects, ex: Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}, Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}, Endpoint/YEAR/MONTH/DAY/{TIMESTAMP}-batch-{nº batch}.{typeFile}
#           ]
```
3. O primeiro job AWS Glue será o `Processing Crypto Currency Data`, que irá:
   - Extrair dados de `/Raw`
   - Renomear colunas
   - Converter tipos de string em tipos decimais
   - Carregar dados em `/Trusted`

4. O último job AWS Glue, `Refining Crypto Currency Data`, será despachado assim que o `Processing Crypto Currency Data` for concluído com sucesso. `Refining Crypto Currency Data` irá:
   - Extrair dados de `Trusted`
   - Criar a Entidade `Currency`
   - Criar a Entidade `Crypto_Data`
   - Criar a Entidade `Currency_Value`
   - Carregar dados em `/Refined`

##### AWS IAM Policy

- A Política IAM AWS necessária para `Processing Crypto Currency Data` é:

```
{
"sid": "{aws glue role}"
"Effect": "Allow",
"Action": ["s3:ReadObject"],
"Resource": "arn:aws:s3:::{bucket_name}/Raw/*"
}
```

```
{
"sid": "{aws glue role}"
"Effect": "Allow",
"Action": ["s3:PutObject"],
"Resource": ["arn:aws:s3:::{bucket_name}/Trusted/*"]
}
```

- A Política IAM AWS necessária para Refining Crypto Currency Data é:

```
{
"sid": "{aws glue role}"
"Effect": "Allow",
"Action": ["s3:ReadObject"],
"Resource": ["arn:aws:s3:::{bucket_name}/Trusted/*",
             "arn:aws:s3:::{bucket_name}/Refined/*"]
}
```

```
{
"sid": "{aws glue role}"
"Effect": "Allow",
"Action": ["s3:PutObject"],
"Resource": ["arn:aws:s3:::{bucket_name}/Refined/*"]
}
```


#### Operação de Código

##### Processing CryptoCurrency Data

A operação do job AWS Glue ``Processing Crypto Currency Data`` pode ser ilustrada com o seguinte diagrama de atividades:

![Activity Diagram: Processing CrytoCurrency Data](/docs/glueingCryptoCurrencyData/ActivityDiagram!Processing%20Data.jpg)

1. A zona ``/Raw`` segue esta estrutura:

```
Bucket
├── Raw
│   └──── JSON
│           └── {Endpoint}
│                   └── {Year} (ex. 2024)
│                         └── {Month} (ex. 04)
│                               └── {Day} (ex. 04)
```

2. O job ``Processing Crypto Currency Data`` irá coletar os dados nos ``subdirs`` dentro de ``/Raw/JSON`` de acordo com a ``subdir date`` e ``endpoint``.

3. Os dados extraídos terão suas colunas renomeadas, e as strings decimais serão convertidas em decimais.

4. Os dados processados serão carregados na zona ``/Trusted`` seguindo esta estrutura:

```
Bucket
├── Trusted
│   └── {Endpoint}
│           └── {Year}
│                 └── {Month}
│                       └── {Day}
│                            └── {Timestamp}
```

O código opera conforme ilustrado abaixo:

![Diagram Sequence: Processing CryptoCurrency Data](/docs/glueingCryptoCurrencyData/SequenceDiagram!ProcessingData.jpg)

#### Refining CryptoCurrency Data

A operação do job AWS Glue ``Refining Crypto Currency Data`` pode ser ilustrada com o seguinte diagrama de atividades:

![Activity Diagram: Refining CrytoCurrency Data](/docs/glueingCryptoCurrencyData/ActivityDiagram!RefiningData.jpg)

1. A zona ``/Trusted ``segue esta estrutura:

```
Bucket
├── Trusted
│   └── {Endpoint}
│           └── {Year}
│                 └── {Month}
│                       └── {Day}
│                            └── {Timestamp}
```

2. O job Refining Crypto Currency Data irá coletar dados em ``/Trusted`` de acordo com a ``subdir date``, ``subdir timestamp`` e ``endpoint``.

3. Os dados extraídos serão modelados em entidades ``Currency``, ``Currency_Value`` e ``Crypto_Data``. 

4. Ao lidar com os dados da entidade ``Currency``, o job irá extrair os dados que já existem na zona ``/Refined`` e compará-los com os atuais. Se não houver novos dados, os dados da entidade ``Currency`` não serão atualizados.
    - Observação: A entidade ``Currency`` contém dados sobre as moedas ``fiat`` e ``crypto``, então não é necessário carregar mais dados com frequência.

5. Os dados processados serão carregados na zona ``/Refined`` seguindo esta estrutura:

```
Bucket
├── Refined
│   └── {Endpoint}
│           └── {Year}
│                 └── {Month}
│                       └── {Day}
│                            └── {Timestamp}
```

O código opera conforme ilustrado abaixo:

![Diagram Sequence: Processing CryptoCurrency Data](/docs/glueingCryptoCurrencyData/SequenceDiagram!ProcessingData.jpg)
# Fetch Crypto Currency Data

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
        - [AWS Lambda Function and AWS Infrastructure](/src/fetchCryptoCurrencyData/README.md#aws-lambda-function-and-aws-infrastructure)
        - [AWS IAM Policy](/src/fetchCryptoCurrencyData/README.md#aws-iam-policy)
        - [Environment Variables](/src/fetchCryptoCurrencyData/README.md#environment-variables)
        - [Code Operation](/src/fetchCryptoCurrencyData/README.md#code-operation)

### About the Source Code

The `Fetch Crypto Currency Data` module is responsible for extracting and loading data from the `/assets` and `/rates` endpoints of the [CoinBase v. 2](https://docs.coincap.io/) API and returning a payload with the instructions necessary for transforming this data by AWS Glue jobs.

### About the Source Code Architecture

The repository was developed in layers and under the Object-Oriented Programming paradigm, isolating responsibilities into classes responsible for different features of the project.

In summary, there are 4 types of classes in the source code:

1. `Controllers`: Responsible for orchestrating calls to the `CoinBase v. 2` and `Boto3` APIs according to business rules.
2. `Services`: Responsible for operating the logic and data handling of the `CoinBase v. 2` and `Boto3` APIs.
3. `Repositories`: Responsible for connecting to the `CoinBase v. 2` and `Boto3` APIs.
4. `Models`: Responsible for modeling data and facilitating data type annotations.

The classes (with their methods and attributes) are documented in the class diagram below:

![Project Class Diagram](/docs/fetchCryptoCurrencyData/ClassDiagram!fetchCryptoCurrencyData.jpg)

#### AWS Lambda Function and AWS Infrastructure

The `Fetch Crypto Currency Data` module is integrated into AWS infrastructure as illustrated in the following diagram:

![AWS Diagram](/docs/fetchCryptoCurrencyData/AWSDiagram!fetchCryptoCurrencyData.jpg)

1. The module is placed in a `Docker Image` containing the source code and an `AWS Lambda Layer` with necessary libraries. This image is created according to instructions in the [Dockerfile](/src/fetchCryptoCurrencyData/Dockerfile) and [.dockerignore](/src/fetchCryptoCurrencyData/.dockerignore).

2. This `Docker Image` is stored in Amazon ECR and an S3 bucket.

3. The `Fetch Crypto Currency Data` module is implemented in the AWS Lambda function `fetchCryptoCurrencyData`, which resides within the `workflow` of `Amazon Step Functions`.

4. This AWS Lambda function is executed as the 1st step according to the schedule set by `Amazon EventBridge`, which triggers the `Amazon Step Functions` workflow. Upon execution, it uploads data to the `Raw` zone of the bucket and outputs an object:

```
{
"bucket_name": "project_bucket", # name of the bucket where data is ingested
"zone": "Raw", # names of the zones where data is stored, namely: Raw, Trusted, and Refined
"objects_uploaded": "/Assets/2024/02/20/{timestamp}-batch_1.json,/Rates/2024/02/20/{timestamp}-batch_1.json" # list of uploaded object names in the structure {endpoint}/{year}/{month}/{day}/{timestamp}-batch_{batch number}.{fileType}
}
```


##### AWS IAM Policy

The required AWS IAM Policy for module execution is:

```
{
"sid": "{lambda function role}"
"Effect": "Allow",
"Action": ["s3:PutObject"],
"Resource": ["arn:aws:s3:::{bucket._bucket.bucket_name}/Raw/*"]
}
```

#### Environment Variables

The environment variables to execute this module locally are:

```
API_URL=https://api.coincap.io/v2

### AWS Credentials
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=

### vars to load
BATCH_SIZE=
S3_ZONE=
BUCKET_NAME=
```

#### Code Operation

The code operation can be illustrated with the following sequence diagram:

![Sequence Diagram](/docs/fetchCryptoCurrencyData/SequenceDiagram!fetchCryptoCurrencyData.jpg)

1. The `S3Repository` class is instantiated, creating an AWS session and an `Amazon S3` client. AWS credentials must be available in environment variables:

```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
```

2. The `LoadService` class is instantiated, receiving an instance of the `S3Repository` class in its constructor function (`__init__()`).

3. The instance of the `LoadService` class is passed as an argument to the constructor function (`__init__()`) of the `ETLController` class, which is then instantiated.

4. Inside the constructor function of the `ETLController` class, the static classes `TransformService` and `ExtractService` are associated with the `services` attribute. The latter has access to the `CryptoCurrencyAPIRepository` class, which connects to the `CoinBase v. 2` API.

5. After the instantiation process of the classes, the `execute()` method of the `ETLController` class is called, which invokes the private method `_extractData` of the same class.

6. The `_extractData` method calls the `getRealTimeData` and `getCurrency

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
        - [Função do AWS Lambda e a Infraestrutura da AWS](/src/fetchCryptoCurrencyData/README.md#função-do-aws-lambda-e-a-infraestrutura-da-aws)
        - [AWS IAM Policy](/src/fetchCryptoCurrencyData/README.md#aws-iam-policy)
        - [As variáveis de ambiente](/src/fetchCryptoCurrencyData/README.md#as-variáveis-de-ambiente)
        - [Operação do código](/src/fetchCryptoCurrencyData/README.md#operação-do-código)

### Sobre o Código Fonte

O módulo `Fetch Crypto Currency Data` resume-se a fazer o processo de extrair e carregar os dados dos *endpoints* `/assets` e `/rates` da API [CoinBase v. 2](https://docs.coincap.io/) e retornar um *payload* com as instruções necessárias para a transformação desses dados pelos *jobs* do AWS Glue Job.

### Sobre a Arquitetura do Código Fonte

O repositório foi desenvolvido em camadas e sob o paradigma da Programação Orientada ao Objeto, em outras palavras, foi isolado as responsabilidades em classes que ficam responsáveis por uma parte das *features* do projeto.

Em suma há 4 tipos de classes no código fonte:

1. `Controllers`: responsáveis por orquestrar, segundo as regras de negócio, as chamadas às API do `CoinBase v. 2` e do `Boto3` por meio de outras classes.
2. `Services`: responsáveis por operar a lógica e o tratamento dos dados ingeridos pela API do `CoinBase v. 2` e do `Boto3`.
3. `Repositories`: responsáveis por fazer a conexão entre às API do `CoinBase v. 2` e do `Boto3`.
4. `Models`: responsáveis por modelar os dados e facilitar a anotação dos tipos dos dados trabalhados.

As classes (com seus métodos e atributos) estão documentados no diagrama de classe abaixo:

![Diagrama de Classe do Projeto](/docs/fetchCryptoCurrencyData/ClassDiagram!fetchCryptoCurrencyData.jpg)

#### Função do AWS Lambda e a Infraestrutura da AWS

O módulo `Fetch Crypto Currency Data` é inserido na Infraestrutura da AWS é ilustrado no seguinte diagrama:

![Diagrama de AWS](/docs/fetchCryptoCurrencyData/AWSDiagram!fetchCryptoCurrencyData.jpg)

1. O módulo é inserido em uma `Docker Image` que terá o códigos fonte e a `AWS Lambda Layer` com as bibliotecas necessárias para o funcionamento do código, essa imagem será formada de acordo com as instruções no [Dockerfile](/src/fetchCryptoCurrencyData/Dockerfile) e [.dockerignore](/src/fetchCryptoCurrencyData/.dockerignore)

2. Essa `Docker Image` será salva no `Amazon ECR` e em um *bucket* do S3.

3. O módulo `Fetch Crypto Currency Data` será implementado na função AWS Lambda `fetchCryptoCurrencyData` que ficará dentro do `workflow` do `Amazon Step Functions`.

4. Essa função AWS Lambda será executada como o 1º passo conforme o agendamento (*schedule*) do `Amazon EventBridge` que vai disparar o `workflow` do `Amazon Step Functions`. Ao ser executada, fará o `upload` dos dados na zona `Raw` do *bucket* e passará como *output* o objeto:

```
{
    "bucket_name": "project_bucket", # nome do bucket em que os dados serão ingeridos
    "zone": "Raw", # nome das zonas em que os dados serão armazenados, são: Raw, Trusted e Refined
    "objects_uploaded": "/Assets/2024/02/20/{timestamp}-batch_1.json,/Rates/2024/02/20/{timestamp}-batch_1.json" # lista com o nome dos objetos que foram uploaded na estrutura {endpoint}/{year}/{month}/{day}/{timestamp}-batch_{nº batch}.{fileType}
}
```

##### AWS IAM Policy

A `AWS IAM Policy` necessária para a execução do módulo é:

```
{
    "sid": "{role da função lambda}"
    "Effect": "Allow",
    "Action": ["s3:PutObject"],
    "Resource": ["arn:aws:s3:::{bucket._bucket.bucket_name}/Raw/*"]
}
```

#### As variáveis de ambiente

As variáveis de ambiente para executar esse módulo localmente são:

```
API_URL=https://api.coincap.io/v2

# AWS Credentials
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=

# vars to load
BATCH_SIZE=
S3_ZONE=
BUCKET_NAME=
```

#### Operação do código

O funcionamento do código pode ser ilustrado com o seguinte diagrama:

![Diagrama de Sequência](/docs/fetchCryptoCurrencyData/SequenceDiagram!fetchCryptoCurrencyData.jpg)

1. A classe `S3Repository` é instanciada e com isso criado uma sessão do AWS e um cliente do `Amazon S3`, para isso é necessário que as credenciais estejam disponíveis nas variáveis de ambiente:

```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
```

2. Em seguida será instanciada a classe `LoadService` que receberá em sua função construtura (`__init__()`) a instância da classe `S3Repository`.

3. A instância da classe `LoadService` será passada como argumento para a função construtura (`__init__()`) da classe `ETLController` que será instanciada.

4. Dentro da função construtora da classe `ETLController` será associado ao atributo `services` as classes estáticas `TransformService` e `ExtractService` - essa última terá acesso a classe `CryptoCurrencyAPIRepository` que fará a conexão com à API do `CoinBase v. 2`.

5. Encerrado o processo de instancias das classes, será chamado o método `execute()` da classe `ETLController` que fará as chamadas do método privado `_extractData` da mesma classe.

6. O método `_extractData` fará chamada do método `getRealTimeData` e `getCurrencyRatesData` da classe `ExtractService` que fará a chamada aos métodos de mesmos nomes da classe `CryptoCurrencyAPIRepository` que fará o *fecth* dos dados através do método privado `_fetch` da classe `CryptoCurrencyAPIRepository`.

7. O resultado do passo anterior serão dois objetos `APICoinCapResponse` que serão tratados dentro da rotina do `execute()` da classe `ETLController` com as chamadas dos métodos `intoCurrencyDataRateExtracted` e `intoCurrencyDataExtracted` da classe `TransformService`, esses métodos vai planificar os dados, conforme o diagrama abaixo:

![Diagrama de Fluxo de Dados](/docs/fetchCryptoCurrencyData/DFDDiagram!fetchCryptoCurrencyData.jpg)

8. Os dados planificados no modelo `CurrencyDataRateExtractedModel` e `CurrencyDataExtractedModel`, essas listas de objetos serão divididas em *batches* conforme a variável de ambiente `BATCH_SIZE`, conforme abaixo:

```
BATCH_SIZE=Quantidade limite de objetos em cada lista
```

9. As listas terão o limite de objetos determinado pelo `BATCH_SIZE`, ultrapassando o limite da lista será feita uma nova lista - cada lista será um *batch* e cada *batch* corresponde a um arquivo `json`.

10. Todo esse processo é realizado dentro da rotina do método `loadBatch` da classe `LoadService` e dos métodos privados `_uploadBatch` e `_uploadJson` da mesma classe que são responsáveis pela lógica do *upload* dos objetos na zona, para isso é necessário declarar as seguintes variáveis de ambiente:

```
S3_ZONE=Raw
BUCKET_NAME=
```

11. Os métodos privados `_uploadBatch` e `_uploadJson` são executados de forma assíncrona e em *loop* assim economizando tempo da execução - a execução do código não ficará congelado até a conclusão de cada requisição.

12. Os objetos terão com o seguinte formato de `object key`: `/{Endpoint}/{YYYY}/{MM}/{DD}/{timestamp}-batch_{nº do batch}.json`. Dentro do método `_uploadJson` será acionado o método privado `_add_object_uploaded` que vai adicionar a propriedade `_objects_uploaded`, uma lista de `object key`.

13. Com isso o `loadBatch` vai retornar uma string com uma mensagem de sucesso e o método `execute` da classe `ETLController` vai montar o seguinte `payload`:

```
{
    "bucket_name": "project_bucket", # nome do bucket em que os dados serão ingeridos
    "zone": "Raw", # nome das zonas em que os dados serão armazenados, são: Raw, Trusted e Refined
    "objects_uploaded": "/Assets/2024/02/20/{timestamp}-batch_1.json,/Rates/2024/02/20/{timestamp}-batch_1.json" # lista com o nome dos objetos que foram uploaded na estrutura {endpoint}/{year}/{month}/{day}/{timestamp}-batch_{nº batch}.{fileType}
}
```

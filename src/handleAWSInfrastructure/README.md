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

The `Handle AWS Infrastructure` component is responsible for configuring and implementing AWS resources for the `Cryptocoin Data Pipeline` project.

The `CryptoCoin Data Pipeline` project performs an automated process of extraction, loading, and transformation (ELT - *Extract Load and Transform*) of data from the [CoinCap v. 2](https://docs.coincap.io/) API.

The main objective of the project is to provide learning experience in using AWS services for data engineering projects. This data can be used to create a dashboard or assist a tradebot operating with cryptocurrency assets.

### About the Source Code Architecture

The `Handle AWS Infrastructure` component is divided into 3 types of classes:

1. Stacks: The `Stack` class is a collection of AWS resources and operates the business rules for the `Cryptocoin Data Pipeline` application.
2. Resources: The `Resource` class implements and models AWS resources.
3. Events: The `Event` class implements and models AWS Eventbridge event rules.

![Class Diagram: Handle AWS Infrastructure](/docs/handleAWSInfrastructure/ClassDiagram!handleAWSArchitucture.jpg)


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

O componente `Handle AWS Infrastructure` é responsável por configurar e implementar os recursos da AWS para o projeto `Cryptocoin Data Pipeline`.

O projeto `CryptoCoin Data Pipeline` realiza um processo automatizado de extração, carregamento e transformação (ELT - *Extract Load and Transform*) de dados provenientes da API [CoinCap v. 2](https://docs.coincap.io/).

O objetivo principal do projeto é proporcionar aprendizado no uso dos serviços da AWS para projetos de engenharia de dados. Esses dados podem ser utilizados para criar um *dashboard* ou auxiliar um *tradebot* que opera com ativos de criptomoedas.

### Sobre a Arquitetura do Código Fonte

O componente `Handle AWS Infrastructure` é dividido em 3 tipos de classes:

1. Stacks: a classe `Stack` são uma coleção de recursos da AWS e que opera as regras de negócios para o aplicativo `Cryptocoin Data Pipeline`
2. Resources: a classe `Resource` faz a implementação e a modelagem dos recursos da AWS
3. Events: a classe `Event` implementa e modela regras de evento do AWS Eventbridge.

![Diagrama de Classes: Handle AWS Infrastructure](/docs/handleAWSInfrastructure/ClassDiagram!handleAWSArchitucture.jpg)

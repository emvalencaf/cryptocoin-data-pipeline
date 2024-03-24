from modules.app import fetchCryptoCurrencyData

def handler(event, context):
    result = fetchCryptoCurrencyData.execute()
    return {
        "statusCode": 200,
        "body": {
            "data": result
        }
    }
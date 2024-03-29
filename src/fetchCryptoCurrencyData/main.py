from modules.app import fetchCryptoCurrencyData

import json

def handler(event, context):
    try:
        payload = json.dumps(fetchCryptoCurrencyData.execute(),
                             indent=2)
        
        return {
            "statusCode": 200,
            "body": payload
            }
    except Exception as err:
        
        error_code = getattr(err, 'response', {}).get('ResponseMetadata', {}).get('HTTPStatusCode', 'Unknown')
        error_message = str(err)
        
        return {
            "statusCode": 500,  # or any appropriate error status code
            "body": {
                "error_code": error_code,
                "error_message": error_message
            }
        }
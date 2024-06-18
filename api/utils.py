import os
from dotenv import load_dotenv


def get_api_tokens():
    # Проверяем, выполняется ли код в Google Colab
    try:
        from google.colab import userdata
        MS_API_TOKEN = userdata.get('MS_API_TOKEN')
        WB_API_TOKEN = userdata.get('WB_API_TOKEN')
        return MS_API_TOKEN, WB_API_TOKEN
    except ImportError:
        pass

    load_dotenv()
    MS_API_TOKEN = os.getenv('MS_API_TOKEN')
    WB_API_TOKEN = os.getenv('WB_API_TOKEN')

    return MS_API_TOKEN, WB_API_TOKEN

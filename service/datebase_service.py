import requests
import json
import pandas as pd
from io import BytesIO

class DateBaseService:
    def __init__(self):
        pass

    def df_to_objects_list(self, df):
        if df is None or df.empty:
            print("⚠️ DataFrame пуст или не существует")
            return []
        objects_list = df.to_dict('records')
    
        return objects_list
    
    def read_yandex_table_simple(self, oauth_token: str, file_path: str):
        headers = {
            'Authorization': f'OAuth {oauth_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            download_url = "https://cloud-api.yandex.net/v1/disk/resources/download"
            params = {'path': file_path}
            
            response = requests.get(download_url, headers=headers, params=params)
            response.raise_for_status()
            
            download_info = response.json()
            file_url = download_info['href']
            
            file_response = requests.get(file_url)
            file_response.raise_for_status()
            
            excel_data = BytesIO(file_response.content)
            
            df = pd.read_excel(
                excel_data,
                dtype=str,  
                na_filter=False,  
                keep_default_na=False  
            )
            
            df = df.fillna('')
            return df
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False
        
    def get_data_base(self, oauth_token: str, file_path: str):
        df = self.read_yandex_table_simple(oauth_token, file_path)
        if df is not None:
            return self.df_to_objects_list(df)
        return []
    
db_service = DateBaseService()
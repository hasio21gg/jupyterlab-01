"""
export http_proxy=http://proxy.sthdg.local:8080
export https_proxy=http://proxy.sthdg.local:8080
python -m pip install --upgrade pip
pip install --upgrade setuptools
pip install pandas
pip install requests
"""
import pandas as pd
import requests
import io
import json
from typing import Any
from typing import Dict
from typing import Optional
import pprint
from tabulate import tabulate

class EStaterror(IOError):
    pass

class BaseReader():
    QUERY     : str
    TABLE_TAG : str
    version   : str
    
    @property
    def url(self) -> str:
        return f"https://api.e-stat.go.jp/rest/{self.version}/app/{self.QUERY}"
    
    @property
    def params(self) -> dict:
        """
        """
    def read(self, **kwargs) -> pd.DataFrame:
        response = self.get()
        print("{}".format(response.url))
        dict = response.json()

        result = dict["GET_STATS_DATA"]["RESULT"]
        param  = dict["GET_STATS_DATA"]["PARAMETER"]
        stats  = dict["GET_STATS_DATA"]["STATISTICAL_DATA"]
        
        try:
            if result["STATUS"] != 0:
                message = result["ERROR_MSG"]
                status  = result["STATUS"]
                raise EStaterror(f"{message} (STATUS: {status})")
        except IOError as e:
            print(e)
            return 0
        finally:
            pprint.pprint(stats["TABLE_INF"], indent=2)
            pprint.pprint(param             , indent=2)

        ret_tables = {}
        if stats["RESULT_INF"]["TOTAL_NUMBER"] != 0:
            ret_tables = stats["DATA_INF"]["VALUE"]

        classinf = pd.DataFrame()
        #pd.set_option('display.max_rows', None)
        
        df = pd.DataFrame(ret_tables)
        for inf in stats["CLASS_INF"]["CLASS_OBJ"]:
            df_t = pd.DataFrame()
            if isinstance(inf['CLASS'] , list):
                df_t = pd.json_normalize(
                    inf,
                    record_path='CLASS',
                    record_prefix='CLASS',
                    meta=['@id','@name'],
                    meta_prefix='META'
                    )
            else:
                df_t = pd.json_normalize(
                    inf, 
                    sep=''
                    )
                df_t.rename(columns={"@id": "META@id","@name" : "META@name"}, inplace=True)
            
            nkey = inf['@id']
            df[nkey]   = df.apply(lambda x: self._get_class_info(df_t, nkey  , x[f'@{nkey}']  )["CLASS@name"], axis=1)
        
        return df
    
    def _get_class_info(self, df, class_id: str, class_code: str):
        df1 = df[(df['META@id'] == class_id) & (df['CLASS@code'] == class_code) ].reset_index()
        return df1
    
    def get(self) -> requests.Response:
        r = requests.get(self.url, params = self.params)
        return r

class StatsDataReader(BaseReader):
    """
    https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?
        statsDataId=0003114565&
        appId=3aa3e35ab7adcf953ed264ee877f2c825cd1eba8
    """
    QUERY     = "getStatsData"
    TABLE_TAG = "VALUE"
    def __init__(
        self,
        appid          : str,
        code           : str,
        limit          : Optional[int] = None,
        start_position : Optional[int] = None,
        hyosho         : Optional[str] = None,
        bunrui         : Optional[list] = None,
        jikan          : Optional[list] = None,
        chiiki         : Optional[list] = None,
        lang           : str = "J",
        version        : str = "3.0",
    ) -> None:
        self.appid          = appid
        self.code           = code
        self.limit          = limit
        self.start_position = start_position
        self.hyosho         = hyosho,
        self.jikan          = jikan,
        self.bunrui         = bunrui,
        self.chiiki         = chiiki,
        self.lang           = lang
        self.version        = version

    @property
    def url(self) -> str:
        return f"https://api.e-stat.go.jp/rest/{self.version}/app/json/{self.QUERY}"
    
    @property
    def params(self) -> dict:
        params: Dict[str, Any] = {"appId": self.appid, "statsDataId": self.code}
        
        if self.limit is not None:
            params["limit"] = self.limit
        if self.start_position is not None:
            params["startPosition"] = self.start_position
        
        if self.hyosho is not None:
            list = self.hyosho[0]
            for dict in list:
                if dict['PREFIX']:
                    PREFIX = dict['PREFIX']
                    if dict['level']:
                        params[f"lv{PREFIX}"] = dict['level']
                    if dict['from']:
                        params[f"cd{PREFIX}From"] = dict['from']
                    if dict['to']:
                        params[f"cd{PREFIX}To"] = dict['to']
                    if dict['CODES'] and len(dict['CODES'])>0:
                        params[f"cd{PREFIX}"] = ",".join(map(str, dict['CODES']))
        if self.jikan is not None:
            list = self.jikan[0]
            for dict in list:
                if dict['PREFIX']:
                    PREFIX = dict['PREFIX']
                    if dict['level']:
                        params[f"lv{PREFIX}"] = dict['level']
                    if dict['from']:
                        params[f"cd{PREFIX}From"] = dict['from']
                    if dict['to']:
                        params[f"cd{PREFIX}To"] = dict['to']
                    if dict['CODES'] and len(dict['CODES'])>0:
                        params[f"cd{PREFIX}"] = ",".join(map(str, dict['CODES']))
        if self.bunrui is not None:
            list = self.bunrui[0]
            for dict in list:
                if dict['PREFIX']:
                    PREFIX = dict['PREFIX']
                    if dict['level']:
                        params[f"lv{PREFIX}"] = dict['level']
                    if dict['CODES'] and len(dict['CODES'])>0:
                        params[f"cd{PREFIX}"] = ",".join(map(str, dict['CODES']))
        if self.chiiki is not None:
            list = self.chiiki[0]
            for dict in list:
                if dict['PREFIX']:
                    PREFIX = dict['PREFIX']
                    if dict['level']:
                        params[f"lv{PREFIX}"] = dict['level']
                    if dict['CODES'] and len(dict['CODES'])>0:
                        params[f"cd{PREFIX}"] = ",".join(map(str, dict['CODES']))
        return params

def read_statsdata(
    appid          : str,
    code           : str,
    limit          : Optional[int] = None,
    start_position : Optional[int] = None,
    hyosho         : Optional[str] = None,
    jikan          : Optional[list] = None,
    bunrui         : Optional[list] = None,
    chiiki         : Optional[list] = None,
    lang           : str = "J",
    version        : str = "3.0",
    **kwargs
    ) -> pd.DataFrame:
    reader = StatsDataReader(
        appid,
        code,
        limit          = limit,
        start_position = start_position,
        hyosho         = hyosho,
        jikan          = jikan,
        bunrui         = bunrui,
        chiiki         = chiiki,
        lang           = lang,
        version=version,
    )
    dataframe = reader.read(**kwargs)
    return dataframe

if __name__ == "__main__":
    print(f"pandas    : {pd.__version__}")
    print(f"requests  : {requests.__version__}")
    
    appid      ='3aa3e35ab7adcf953ed264ee877f2c825cd1eba8'
    estat_code = '0003114535'   #(持ち家/賃家/給与住宅/分譲住宅)(新設/その他)
    #estat_code = '0003114565'   #(一戸建/長屋建)(新設{専用/併用}/その他{専用/併用})
    #estat_code = '0003138953'
    #Cat01-Cat03
    #estat_code = '0003114566'  #
    #cdtab      = ""
    #cdtab      = "18"
    hyosho     = {
        "0003114535":               #'都道府県別、工事別、利用関係別／戸数・件数、床面積'
        [
            {
                "PREFIX"  : "Tab",
                "level"  : "",      #固定
                "CODES" : [18,13],      #18:"戸数・件数", "13":"床面積の合計"
                "from"   : "",
                "to"     : "",
                
            }
        ]
    }
    jikan      = {
        "0003114535":               #'都道府県別、工事別、利用関係別／戸数・件数、床面積'
        [
            {
                "PREFIX"   : "Time",
                "level"  : "4",     #固定
                "CODES": [],
                "from"   : "2022000701",
                "to"     : "2022000831",
                
            }
        ]
    }
    chiiki     = {
        "0003114535":               #'都道府県別、工事別、利用関係別／戸数・件数、床面積'
        [
            {
                "PREFIX" : "Area",
                "level": "2",
                "CODES": [16000]
            }
        ]
    }
    bunrui     = {
        "0003138953":               #建築物】建築主別・用途別・構造別\u3000床面
        [],
        "0003114535":               #'都道府県別、工事別、利用関係別／戸数・件数、床面積'
        [
            {
                "PREFIX"  : "Cat01",     #"利用関係"
                "level": "2",       #"計"
                "CODES": []         #
            },
            #{
                #"cat": "Cat02",     #"工事"
                #"level": "1",       #"計"
                #"": []         #
            #},
            {
                "PREFIX": "Cat02",     #"工事"
                "level": "2",       #"計"
                "CODES": []         #
                #"CODES": [12,13]         #
            }
        ],
        "0003114566":               #（プレハブ）住宅の種類別、工事別、建て方別／戸数・件数、床面積
        [
              {
                "PREFIX": "Cat01",     #"建て方"
                "level": "1",       #"計"
                "CODES": []         #
              },
              #{
              #  "cat": "Cat02",     #"工事"
              #  "level": "2",       #"新設","その他"
              #},
              {
                "PREFIX": "Cat02",     #"工事"
                "level": "1",       #"計"
                "CODES": []         #
              },
              {
                "PREFIX": "Cat03",     #"住宅の種類"
                "level": "1",       #"計"
                "CODES": []         #
              }
        ]
    }  
    #df =read_statsdata(appid=appid, code=estat_code, limit=10, start_position=11335530)
    #print(type(bunrui[estat_code]))
    df =read_statsdata(
        appid      = appid, 
        code       = estat_code, 
        hyosho     = hyosho[estat_code],
        jikan      = jikan [estat_code],
        bunrui     = bunrui[estat_code],
        chiiki     = chiiki[estat_code]
    )
    """
    https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData
        ?appId=3aa3e35ab7adcf953ed264ee877f2c825cd1eba8
        &statsDataId=0003114565
        &cdArea=16000
        &limit=100
        &cdTimeFrom=2022000801
        &cdTimeTo=2022000899
    """

    pd.set_option('display.max_rows', None)
    #pd.options.display.max_colwidth = 100
    #pd.options.display.max_columns = 100
    print(df)
    #print(tabulate(df,"keys", tablefmt="pretty"))
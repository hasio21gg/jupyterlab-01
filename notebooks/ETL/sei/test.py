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
            #if dict["GET_STATS_DATA"]["RESULT"]["STATUS"] != 0:
            if result["STATUS"] != 0:
                #message = dict["GET_STATS_DATA"]["RESULT"]["ERROR_MSG"]
                message = result["ERROR_MSG"]
                #status  = dict["GET_STATS_DATA"]["RESULT"]["STATUS"]
                status  = result["STATUS"]
                raise EStaterror(f"{message} (STATUS: {status})")
        except IOError as e:
            print(e)
            #pprint.pprint(dict["GET_STATS_DATA"]["STATISTICAL_DATA"]["TABLE_INF"], indent=2)
            #pprint.pprint(dict["GET_STATS_DATA"]["PARAMETER"], indent=2)
            return 0
        finally:
            pprint.pprint(stats["TABLE_INF"], indent=2)
            pprint.pprint(param             , indent=2)


        #result = dict["GET_STATS_DATA"]["RESULT"]
        #param  = dict["GET_STATS_DATA"]["PARAMETER"]
        #stats  = dict["GET_STATS_DATA"]["STATISTICAL_DATA"]
        ret_tables = {}
        if stats["RESULT_INF"]["TOTAL_NUMBER"] != 0:
            ret_tables = stats["DATA_INF"]["VALUE"]

        #classinf = pd.DataFrame(stats["CLASS_INF"]["CLASS_OBJ"])
        classinf = pd.DataFrame()
        #pd.set_option('display.max_rows', None)
        
        df = pd.DataFrame(ret_tables)
        for inf in stats["CLASS_INF"]["CLASS_OBJ"]:
            #print("{}".format(type(inf['CLASS'])))
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
            #classinf = pd.concat([classinf, df_t])
            nkey = inf['@id']
            df[nkey]   = df.apply(lambda x: self._get_class_info(df_t, nkey  , x[f'@{nkey}']  )["CLASS@name"], axis=1)
            
                            
        #print(classinf)
        ##df = pd.DataFrame(ret_tables)
        ##df["tab"]   = df.apply(lambda x: self._get_class_info(classinf, 'tab'  , x['@tab']  )["CLASS@name"], axis=1)
        ##df["cat01"] = df.apply(lambda x: self._get_class_info(classinf, 'cat01', x['@cat01'])["CLASS@name"], axis=1)
        ##df["cat02"] = df.apply(lambda x: self._get_class_info(classinf, 'cat02', x['@cat02'])["CLASS@name"], axis=1)
        ##df["cat03"] = df.apply(lambda x: self._get_class_info(classinf, 'cat03', x['@cat03'])["CLASS@name"], axis=1)
        ##df["area"]  = df.apply(lambda x: self._get_class_info(classinf, 'area' , x['@area'] )["CLASS@name"], axis=1)
        ##df['time']  = df.apply(lambda x: self._get_class_info(classinf, 'time' , x['@time'] )["CLASS@name"], axis=1)
        return df
    
    def _get_class_info(self, df, class_id: str, class_code: str):
        #print(f'{class_id}-{class_code}')
        df1 = df[(df['META@id'] == class_id) & (df['CLASS@code'] == class_code) ].reset_index()
        #print('{}-{} {}'.format(class_id,class_code,len(df1)))
        #print(df1)
        return df1
    
    def get(self) -> requests.Response:
        #print(self.params)
        r = requests.get(self.url, params = self.params)
        #print(r)
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
        cdtab          : Optional[str] = None,
        lvarea         : Optional[str] = None,
        cdarea         : Optional[str] = None,
        cdtimefrom     : Optional[str] = None,
        cdtimeto       : Optional[str] = None,
        bunrui         : Optional[list] = None,
        lang           : str = "J",
        version        : str = "3.0",
    ) -> None:
        self.appid          = appid
        self.code           = code
        self.limit          = limit
        self.start_position = start_position
        self.cdtab          = cdtab,
        self.lvarea         = lvarea,
        self.cdarea         = cdarea,
        self.cdtimefrom     = cdtimefrom,
        self.cdtimeto       = cdtimeto,
        self.bunrui         = bunrui,
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

        if self.cdarea is not None:
            params["cdArea"] = self.cdarea
        if self.cdtimefrom is not None:
            params["cdTimeFrom"] = self.cdtimefrom 
        if self.cdtimeto is not None:
            params["cdTimeTo"] = self.cdtimeto 
        
        if self.cdtab is not None:
            params["cdTab"] = self.cdtab
        if self.lvarea is not None:
            params["lvArea"] = self.lvarea
        
        if self.bunrui is not None:
            """
            """
            l = self.bunrui[0]
            for bun in l:
                if bun['cat']:
                    if bun['level']:
                        params["lv{}".format(bun['cat'])] = bun['level']
                    if bun['codes']:
                        params["cd{}".format(bun['cat'])] = bun['codes']
        return params

def read_statsdata(
    appid          : str,
    code           : str,
    limit          : Optional[int] = None,
    start_position : Optional[int] = None,
    cdtab          : Optional[str] = None,
    lvarea         : Optional[str] = None,
    cdarea         : Optional[str] = None,
    cdtimefrom     : Optional[str] = None,
    cdtimeto       : Optional[str] = None,
    bunrui         : Optional[list] = None,
    lang           : str = "J",
    version        : str = "3.0",
    **kwargs
    ) -> pd.DataFrame:
    print(type(bunrui))
    reader = StatsDataReader(
        appid,
        code,
        limit          = limit,
        start_position = start_position,
        cdtab          = cdtab,
        lvarea         = lvarea,
        cdarea         = cdarea,
        cdtimefrom     = cdtimefrom,
        cdtimeto       = cdtimeto,
        bunrui         = bunrui,
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
    cdarea     = ""
    cdtimefrom = ""
    cdtimeto   = ""
    cdtab      = ""
    lvarea     = ""
    #cdarea     = "16000"
    cdtimefrom = "2022000800"
    cdtimeto   = "2022000899"
    cdtab      = "18"
    lvarea     = "2"            #全国:1,都道府県:2,市:3,群:4
    bunrui     = {
        "0003138953":               #建築物】建築主別・用途別・構造別\u3000床面
            [],
        "0003114535":               #'都道府県別、工事別、利用関係別／戸数・件数、床面積'
            [
                {
                "cat": "Cat01",     #"利用関係"
                "level": "2",       #"計"
                "codes": []         #
                },
                #{
                #"cat": "Cat02",     #"工事"
                #"level": "1",       #"計"
                #"codes": []         #
                #},
                {
                "cat": "Cat02",     #"工事"
                "level": "2",       #"計"
                "codes": [12,13]         #
                }
            ],
        "0003114566":               #（プレハブ）住宅の種類別、工事別、建て方別／戸数・件数、床面積
            [
              {
                "cat": "Cat01",     #"建て方"
                "level": "1",       #"計"
                "codes": []         #
              },
              #{
              #  "cat": "Cat02",     #"工事"
              #  "level": "2",       #"新設","その他"
              #},
              {
                "cat": "Cat02",     #"工事"
                "level": "1",       #"計"
                "codes": []         #
              },
              {
                "cat": "Cat03",     #"住宅の種類"
                "level": "1",       #"計"
                "codes": []         #
              }
            ]
    }  
    #df =read_statsdata(appid=appid, code=estat_code, limit=10, start_position=11335530)
    print(type(bunrui[estat_code]))
    df =read_statsdata(
        appid=appid, 
        code=estat_code, 
        cdarea=cdarea, 
        cdtimefrom=cdtimefrom, 
        cdtimeto=cdtimeto, 
        cdtab=cdtab, 
        lvarea=lvarea,
        bunrui=bunrui[estat_code]
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

    print(df)
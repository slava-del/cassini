from datetime import date, timedelta # To define date range of data
import requests # To define http request to be make 
import pandas as pd # Convert data received from copernicus API in easier format
import geopandas as gpd # Convert Pandas dataframe in Geo pandas will allow us to use metadata and geoemtry.
from shapely.geometry import shape # To convert raw Geometry data
import os
from dotenv import load_dotenv

load_dotenv()
# copernicus User email 
copernicus_user = os.getenv("copernicus_user")
# copernicus User Password
copernicus_password = os.getenv("copernicus_password") 
# WKT Representation of BBOX of AOI
ft = "POLYGON ((22.466287332337345 47.023435195043646, 22.466287332337345 44.67755354653033, 26.256055635674613 44.67755354653033, 26.256055635674613 47.023435195043646, 22.466287332337345 47.023435195043646))" 
# Sentinel satellite that you are interested in 
data_collection = "SENTINEL-2"

# Dates of search 

today =  date.today()
today_string = today.strftime("%Y-%m-%d")
yesterday = today - timedelta(days=1)
yesterday_string = yesterday.strftime("%Y-%m-%d")

def get_keycloak(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    try:
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Keycloak token creation failed. Reponse from the server was: {r.json()}"
        )
    return r.json()["access_token"]

json_ = requests.get(
    f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq '{data_collection}' and OData.CSC.Intersects(area=geography'SRID=4326;{ft}') and ContentDate/Start gt {yesterday_string}T00:00:00.000Z and ContentDate/Start lt {today_string}T00:00:00.000Z&$count=True&$top=1000"
).json()  
p = pd.DataFrame.from_dict(json_["value"]) # Fetch available dataset
if p.shape[0] > 0 : # If we get data back
    p["geometry"] = p["GeoFootprint"].apply(shape)
    # Convert pandas dataframe to Geopandas dataframe by setting up geometry
    productDF = gpd.GeoDataFrame(p).set_geometry("geometry") 
    # Remove L1C dataset if not needed
    productDF = productDF[~productDF["Name"].str.contains("L1C")] 
    print(f" total L2A tiles found {len(productDF)}")
    productDF["identifier"] = productDF["Name"].str.split(".").str[0]
    allfeat = len(productDF) 
    
    if allfeat == 0: # If L2A tiles are not available in current query
        print(f"No tiles found for {today_string}")
    else: # If L2A tiles are available in current query
        # download all tiles from server
        for index,feat in enumerate(productDF.iterfeatures()):
            try:
                # Create requests session 
                session = requests.Session()
                # Get access token based on username and password
                keycloak_token = get_keycloak(copernicus_user,copernicus_password)
                
                session.headers.update({"Authorization": f"Bearer {keycloak_token}"})
                url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({feat['properties']['Id']})/$value"
                response = session.get(url, allow_redirects=False)
                while response.status_code in (301, 302, 303, 307):
                    url = response.headers["Location"]
                    response = session.get(url, allow_redirects=False)
                print(feat["properties"]["Id"])
                file = session.get(url, verify=False, allow_redirects=True)

                with open(
                    f"/{feat['properties']['identifier']}.zip", #location to save zip from copernicus 
                    "wb",
                ) as p:
                    print(feat["properties"]["Name"])
                    p.write(file.content)
            except:
                print("problem with server")
else : # If no tiles found for given date range and AOI
    print('no data found')

import requests
import json
import settings
import currentgps

def get_location(destination):
    center_lon, center_lat = currentgps.get_gps()
    tmap_location_url = "https://apis.openapi.sk.com/tmap/pois?version=1&format=json&callback=result"

    rest_api_key = settings.get_apiKey('rest_api_key')

    searchKeyword = destination               #일단 스타벅스 경희대국제캠퍼스점 하나로 코드 작성
    params = {
        "appKey" : rest_api_key,
        "searchKeyword" : searchKeyword,
        "resCoordType" : "WGS84GEO",    #EPSG3857
        "reqCoordType" : "WGS84GEO",    #WGS84GEO
        "radius" : 1, #주변 반경 설정
        "searchtypCd" : "A", #A : 관련도순, R: 거리순
        "centerLon" : center_lon,    #경도             현재 위치 해야 됨
        "centerLat" : center_lat,    #위도
        "count" : 10
    }

    res = requests.get(tmap_location_url, params=params)

    response_dict = json.loads(res.text)
    searchPoiInfo = response_dict['searchPoiInfo']
    location_pois = searchPoiInfo['pois']
    location_poi = location_pois['poi']
    #print(len(location_poi))
    #print(location_poi)
    for i in location_poi:
        poi_name = i['name']
        poi_Lon = i['frontLon']
        poi_Lat = i['frontLat']
        poi_radius = i['radius']
     #  print(f'poi_name = {poi_name}')
     #  print(f'poi_Lon = {poi_Lon}')
     #  print(f'poi_Lat = {poi_Lat}')
     #  print(f'poi_radius = {poi_radius}\n')

    return center_lon, center_lat, poi_Lon, poi_Lat

def get_route(destination):
    current_lon, current_lat, destination_lon, destination_lat = get_location(destination)

    tmap_route_url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json&callback=result"

    rest_api_key = settings.get_apiKey('rest_api_key')

    data = {
        "appKey" : rest_api_key,
        "startX" : current_lon,    #경도
        "startY" : current_lat,    #위도
        "endX" : destination_lon,
        "endY" : destination_lat,
        "reqCoordType" : "WGS84GEO",
        "resCoordType" : "WGS84GEO",
        "startName" : "start",
        "endName" : "end",
        "passList" : ""
    }

    res = requests.post(tmap_route_url, data=data)


    response_dict = json.loads(res.text)
    a = []
    with open('points.txt', 'w') as point_file:
        with open('linestring.txt','w') as f:
            for i in response_dict['features']:
                route_geometry = i['geometry']
                route_properties = i['properties']
                route_type = route_geometry['type']
                route_coordinates = route_geometry['coordinates']
                route_description = route_properties['description']
                print(f'route_type = {route_type}')
                print(f'route_coordinates = {route_coordinates}')
                print(f'route_description = {route_description}\n')

                if route_type == 'LineString':
                    for i in route_coordinates:
                        if a == i:
                            continue
                        else : f.write(f'{i[0]} {i[1]} \n')
                    a = i
                elif route_type == 'Point':
                    point_file.write(f'{route_coordinates[0]}, {route_coordinates[1]}, {route_description}\n')
                

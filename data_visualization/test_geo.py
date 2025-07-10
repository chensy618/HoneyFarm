import geoip2.database

reader = geoip2.database.Reader("./data_visualization/GeoLite2-City.mmdb")

ip = "8.8.8.8"  # 可测试多个 IP
try:
    res = reader.city(ip)
    print("Latitude:", res.location.latitude)
    print("Longitude:", res.location.longitude)
    print("City:", res.city.name)
    print("Country:", res.country.name)
except Exception as e:
    print("Error:", e)

for ip in ["167.94.138.56", "195.184.76.227", "3.137.73.221"]:
    try:
        res = reader.city(ip)
        print(ip, "→", res.location.latitude, res.location.longitude, res.city.name, res.country.name)
    except Exception as e:
        print(ip, "→", e)

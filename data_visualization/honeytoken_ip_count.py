import json

def count_unique_ips_with_honeytokens(log_file_path):
    unique_ips = set()
    
    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue 
            
            if event.get("eventid") == "cowrie.honeytoken":
                src_ip = event.get("src_ip")
                if src_ip:
                    unique_ips.add(src_ip)
    
    return len(unique_ips), unique_ips


if __name__ == "__main__":
    log_path = "./data_visualization/raw_data/merged/filtered+merged_appliances.json" 
    count, ips = count_unique_ips_with_honeytokens(log_path)
    
    print(f"Number of unique IPs that accessed honeytokens: {count}")
    print("IPs:", ips)

import os
import shutil
import re

def restructure(data_dir):
    print(f"Restructuring data in {data_dir}...")
    os.chdir(data_dir)

    # Find all extracted files
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.startswith('T')]

    count = 0
    for file in files:
        # Example filename: T34QFE_2017-04-23.dem_10m.nc
        parts = file.split('_')
        if len(parts) < 2:
            continue
        
        tile = parts[0] # T34QFE
        date = parts[1].split('.')[0] # 2017-04-23
        
        # Parse Sentinel-2 tile name (e.g. T34QFE -> 34, Q, FE)
        match = re.match(r'^T(\d+)([A-Z])([A-Z]{2})$', tile)
        if not match:
            continue
            
        zone, lat_band, square = match.groups()
        
        # Build the LUMI folder structure: T34/34Q/34QFE/2017-04-23
        dir1 = f"T{zone}"
        dir2 = f"{zone}{lat_band}"
        dir3 = f"{zone}{lat_band}{square}"
        
        target_dir = os.path.join(dir1, dir2, dir3, date)
        os.makedirs(target_dir, exist_ok=True)
        
        # Move the file into its proper nested folder
        shutil.move(file, os.path.join(target_dir, file))
        count += 1

    print(f"Successfully restructured {count} files!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, help="Path to extracted THOR-data")
    args = parser.parse_args()
    restructure(args.data_dir)

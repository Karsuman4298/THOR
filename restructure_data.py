import os
import shutil
import re
import glob

def restructure(data_dir):
    print(f"Restructuring data in {data_dir}...")
    
    # Create DEM directories
    base_dir = os.path.dirname(os.path.abspath(data_dir))
    dem_dir = os.path.join(base_dir, "dem")
    os.makedirs(os.path.join(dem_dir, "10"), exist_ok=True)
    os.makedirs(os.path.join(dem_dir, "60"), exist_ok=True)

    os.chdir(data_dir)

    # Find all extracted files (recursively in case they were moved)
    files = []
    for root, dirs, f_names in os.walk('.'):
        for f in f_names:
            if f.startswith('T') and f.endswith('.nc'):
                files.append(os.path.join(root, f))

    count = 0
    for file_path in files:
        file = os.path.basename(file_path)
        parts = file.split('_')
        if len(parts) < 2:
            continue
        
        tile = parts[0] # T34QFE
        date = parts[1].split('.')[0] # 2017-04-23
        
        match = re.match(r'^T(\d+)([A-Z])([A-Z]{2})$', tile)
        if not match:
            continue
            
        zone, lat_band, square = match.groups()
        
        dir1 = f"T{zone}"
        dir2 = f"{zone}{lat_band}"
        dir3 = f"{zone}{lat_band}{square}"
        
        # Determine subdirectory
        subdir = ""
        if "s3:slstr" in file:
            subdir = "S3/SL_1_RBT"
        elif "s3:olci" in file:
            subdir = "S3/OL_1_EFR"
        elif "dem" in file:
            # Handle DEM separately
            if "10m" in file:
                shutil.copy(file_path, os.path.join(dem_dir, "10", f"{tile[1:]}_dem.nc"))
            elif "60m" in file:
                shutil.copy(file_path, os.path.join(dem_dir, "60", f"{tile[1:]}_dem.nc"))
            continue
        else:
            # If there are S1/S2 files, we don't know their subdirs from this snippet, but we only have S3/DEM in tiny shards
            pass

        if subdir:
            target_dir = os.path.join(dir1, dir2, dir3, date, subdir)
            os.makedirs(target_dir, exist_ok=True)
            target_file = os.path.join(target_dir, file)
            if os.path.abspath(file_path) != os.path.abspath(target_file):
                shutil.move(file_path, target_file)
                count += 1

    print(f"Successfully restructured {count} files!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, help="Path to extracted THOR-data")
    args = parser.parse_args()
    restructure(args.data_dir)

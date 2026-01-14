import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') # Ensure 'core' matches your project name
django.setup()

from django.contrib.gis import gdal
from django.contrib.gis import geos
from django.contrib.gis.geos import Point

def run_gis_test():
    print("--- GIS Environment Test ---")
    
    # 1. Test GDAL
    try:
        print(f"GDAL Version: {gdal.gdal_version().decode('utf-8')}")
        print("✅ GDAL loaded successfully.")
    except Exception as e:
        print(f"❌ GDAL Error: {e}")

    # 2. Test GEOS
    try:
        print(f"GEOS Version: {geos.geos_version().decode('utf-8')}")
        print("✅ GEOS loaded successfully.")
    except Exception as e:
        print(f"❌ GEOS Error: {e}")

    # 3. Test Spatial Objects (Sikkim Coordinates)
    try:
        # Gangtok coordinates: ~88.61 E, 27.33 N
        pnt = Point(88.61, 27.33, srid=4326)
        print(f"Created Point: {pnt.wkt}")
        print(f"Point SRID: {pnt.srid}")
        
        # Test a simple spatial operation (Distance)
        pnt2 = Point(88.60, 27.30, srid=4326)
        dist = pnt.distance(pnt2)
        print(f"Calculated distance between two points: {dist}")
        print("✅ Spatial operations working.")
    except Exception as e:
        print(f"❌ Geometry/PROJ Error: {e}")

if __name__ == "__main__":
    run_gis_test()
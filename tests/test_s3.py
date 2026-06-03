from src.utils.s3 import list_bucket_objects

keys = list_bucket_objects()

for key in keys:
    print(key)
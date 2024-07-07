try:
    import boto3
    import csv
    import uuid
    import json
    import datetime
    import re
    from datetime import datetime
    import os
    import io
    from io import StringIO
    from faker import Faker
except ModuleNotFoundError as e:
    print(e)


class AWSS3(object):

    def __init__(
        self,
        bucket=os.getenv("BUCKET_NAME"),
        aws_access_key_id=os.getenv("DEV_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("DEV_SECRET_KEY"),
        region_name=os.getenv("DEV_REGION"),
    ) -> None:
        self.BucketName = bucket
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def upload_file(self, Response=None, key=None) -> str:
        try:
            response = self.client.put_object(
                ACL="private", Body=Response, Bucket=self.BucketName, Key=str(key)
            )

            return "ok"

        except Exception as e:
            raise Exception("Failed to upload records. Error: " + str(e))

    def item_exists(self, key) -> bool:
        """Gets the Bytes Data from AWS s3"""

        try:
            response_new = self.client.get_object(Bucket=self.BucketName, Key=str(key))
            return True

        except Exception as e:
            print("Error: " + str(e))
            return False

    def get_item(self, key=None) -> bool:
        """Gets the Bytes Data from AWS s3"""
        try:
            response_new = self.client.get_object(Bucket=self.BucketName, Key=str(key))

            return response_new["Body"].read()
        except Exception as e:
            print("Error: " + str(e))
            return False

    def find_one_update(self, data=None, key=None):
        """
        This checks if Key is on S3 if it is return the data from s3
        else store on s3 and return it
        """
        flag = self.item_exists(key=key)
        if flag:
            data = self.get_item(key=key)
            return data
        else:
            self.upload_file(Response=data, key=key)
            return data

    def delete_object(self, key):
        response = self.client.delete_object(Bucket=self.BucketName, Key=key)
        return response

    def get_all_keys(self, Prefix=""):
        """
        :param Prefix: Prefix string
        :return: Keys List
        """
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.BucketName, Prefix=Prefix)
            tmp = []
            for page in pages:
                for obj in page["Contents"]:
                    tmp.append(obj["Key"])
            return tmp
        except Exception as e:
            return []

    def print_tree(self):
        keys = self.get_all_keys()
        for key in keys:
            print(key)
        return None

    def find_one_similar(self, searchTerm=""):
        keys = self.get_all_keys()
        return [key for key in keys if re.search(searchTerm, key)]

    def __repr__(self):
        return "AWS S3 Helper class"


global faker
faker = Faker()


class DataGenerator(object):

    @staticmethod
    def get_data():
        name = faker.name().split(" ")
        first_name = name[0]
        last_name = name[1]
        address = faker.address()
        text = faker.text()
        id = str(uuid.uuid4())
        city = faker.city()
        state = faker.state()

        json_data = {
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "text": text,
            "id": id,
            "city": city,
            "state": state,
        }

        return json_data


def main():
    helper_process_files = AWSS3()

    for _ in range(10):
        data = DataGenerator.get_data()
        key = f"synthetic_data/{uuid.uuid4().__str__()}.json"
        helper_process_files.upload_file(key=key, Response=json.dumps(data))
        print(data)
        print("\n")


if __name__ == "__main__":
    main()

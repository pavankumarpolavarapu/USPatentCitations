import os
import zipfile


def download_patent_file(df_file):
    storage_dir = "data"
    url = "https://bulkdata.uspto.gov/data/patent/grant/redbook/bibliographic/{}/{}".format(df_file["year"].values[0], df_file["file"].values[0])
    storage_path = os.path.join(os.getcwd(), storage_dir)
    
    path = os.path.join(storage_path, df_file["file"].values[0])
    print('Attempting to download {} to {}'.format(url, path))
    #cmd = 'curl -o {} {}'.format(path, url)
    #os.system(cmd)
    print("Unzipping the file {}".format(df_file["file"].values[0]))
    print(path)
    zip_ref = zipfile.ZipFile(path, 'r')
    zip_ref.extractall(storage_path)
    zip_ref.close()

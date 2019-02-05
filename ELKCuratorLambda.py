'''
Created on Nov 21, 2018

@author: Vishal Masih (https://github.com/vishalmasih)

To Build:
Install Python and upgrade it, run the following commands (-t deploys the packages to the local directory where this file is placed):
SET HTTPS_PROXY=https://abc:80
python -m pip install --upgrade pip
pip install boto3 -t .
pip install requests -t .
pip install requests-aws4auth -t .
pip install elasticsearch -t .
pip install elasticsearch-curator -t .
pip install os -t .

Once done, create a zip file of the contents of the source directory, not the directory itself amd upload
(Unix example https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-dependencies)

'''
import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import curator
import os
from base64 import b64decode

# Snapshots are taken for indices a day younger than the index_rentention_days
index_rentention_days = int(os.environ['index_rentention_days'])
snapshot_index_days = index_rentention_days - 1
snapshot_rentention_days = int(os.environ['snapshot_rentention_days'])

host = os.environ['es_host'] # For example, search-my-domain.region.es.amazonaws.com
region = os.environ['region'] # For example, us-west-1
service = 'es'

access_key_enc = os.environ['access_key']
secret_key_enc = os.environ['secret_key']

access_key = boto3.client('kms', region).decrypt(CiphertextBlob=b64decode(access_key_enc))['Plaintext']
secret_key = boto3.client('kms', region).decrypt(CiphertextBlob=b64decode(secret_key_enc))['Plaintext']

access_key = access_key.decode('utf-8')
secret_key = secret_key.decode('utf-8')

print(index_rentention_days)
print(snapshot_index_days)
print(snapshot_rentention_days)
print(host)
print(region)
#print(access_key)
#print(secret_key)

#Login, need to decode as char string, the decrytion returns a byte string
awsauth = AWS4Auth(access_key, secret_key, region, service)

# Lambda execution starts here.
def lambda_handler(event, context):
    # Build the Elasticsearch client.
    es = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    #print(es.info())
    index_list = curator.IndexList(es)
    
    # Do index deletion first
    index_list.filter_by_age(source='name', direction='older', timestring='%Y.%m.%d', unit='days', unit_count=index_rentention_days)
    if index_list.indices:
        print("Found %s indices to delete " % len(index_list.indices))
        print(index_list.indices)
        try: 
            curator.DeleteIndices(index_list).do_action()
        except (curator.exceptions.FailedExecution) as e:
            print(e)

    # Snapshots next
    # QA first
    # Filters by age, anything with a time stamp older than delete_index_day days in the index name.
    index_list = curator.IndexList(es)
    index_list.filter_by_regex(kind='prefix', value='qa', exclude=False)
    if index_list.indices:
        index_list.filter_by_age(source='name', direction='older', timestring='%Y.%m.%d', unit='days', unit_count=snapshot_index_days)
        if index_list.indices:
            print("Found %s indices to snapshot " % len(index_list.indices))
            print(index_list.indices)
            try:
                curator.Snapshot(index_list, repository='my-es-snapshot-repo', name='qa-%Y%m%d%H%M%S',
                             ignore_unavailable=True, include_global_state=False, partial=True,
                             wait_for_completion=False, wait_interval=10, max_wait=-1, skip_repo_fs_check=True).do_action()
            except (curator.exceptions.SnapshotInProgress, curator.exceptions.FailedExecution) as e:
                print(e)
    
    # Do STAGE now
    index_list = curator.IndexList(es)
    index_list.filter_by_regex(kind='prefix', value='stage', exclude=False)
    if index_list.indices:
        index_list.filter_by_age(source='name', direction='older', timestring='%Y.%m.%d', unit='days', unit_count=snapshot_index_days)
        if index_list.indices:
            print("Found %s indices to snapshot " % len(index_list.indices))
            print(index_list.indices)
            try:
                curator.Snapshot(index_list, repository='my-es-snapshot-repo', name='stage-%Y%m%d%H%M%S',
                             ignore_unavailable=True, include_global_state=False, partial=True,
                             wait_for_completion=False, wait_interval=10, max_wait=-1, skip_repo_fs_check=True).do_action()
            except (curator.exceptions.SnapshotInProgress, curator.exceptions.FailedExecution) as e:
                print(e)
    
    # Do PROD now
    index_list = curator.IndexList(es)
    index_list.filter_by_regex(kind='prefix', value='prod', exclude=False)
    if index_list.indices:
        index_list.filter_by_age(source='name', direction='older', timestring='%Y.%m.%d', unit='days', unit_count=snapshot_index_days)
        if index_list.indices:
            print("Found %s indices to snapshot " % len(index_list.indices))
            print(index_list.indices)
            try:
                curator.Snapshot(index_list, repository='my-es-snapshot-repo', name='prod-%Y%m%d%H%M%S',
                             ignore_unavailable=True, include_global_state=False, partial=True,
                             wait_for_completion=False, wait_interval=10, max_wait=-1, skip_repo_fs_check=True).do_action()
            except (curator.exceptions.SnapshotInProgress, curator.exceptions.FailedExecution) as e:
                print(e)
                         
    # Now delete old snapshots
    snapshot_list = curator.SnapshotList(es, repository='my-es-snapshot-repo')
    if snapshot_list.snapshots:
        snapshot_list.filter_by_age(source='creation_date', direction='older', timestring='%Y.%m.%d', unit='days', unit_count=snapshot_rentention_days)
        if snapshot_list.snapshots:
            try:
                curator.DeleteSnapshots(snapshot_list, retry_interval=10, retry_count=3).do_action()
            except (curator.exceptions.SnapshotInProgress, curator.exceptions.NoSnapshots, curator.exceptions.FailedExecution) as e:
                print(e)
    

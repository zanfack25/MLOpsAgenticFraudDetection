# from pydantic import BaseModel
# from py2neo import Graph
# import boto3
# import tempfile
# from urllib.parse import urlparse
# import os
#
# # Default S3 path or override via environment variable
# INPUT_GRAPH_URL = os.getenv(
#     "INPUT_GRAPH_URL",
#     "s3://dav-fraud-detection-bucket/DestinationRiskGraph/neo4j-p2p-data_v5.dump"
# )
#
# # Node Schemas
#
# class UserNode(BaseModel):
#     guid: str
#     money_transfer_fraud: int
#     louvainCommunityId: int | None = None
#     wccId: int | None = None
#
# class DeviceNode(BaseModel):
#     guid: str
#
# class CardNode(BaseModel):
#     guid: str
#
# class IPNode(BaseModel):
#     guid: str
#
# # Relationship Schemas
#
# class UsedRelationship(BaseModel):
#     user_guid: str
#     device_guid: str
#
# class HasIPRelationship(BaseModel):
#     user_guid: str
#     ip_guid: str
#
# class HasCCRelationship(BaseModel):
#     user_guid: str
#     card_guid: str
#
# class ReferredRelationship(BaseModel):
#     referrer_guid: str
#     referee_guid: str
#
# class P2PRelationship(BaseModel):
#     sender_guid: str
#     receiver_guid: str
#
# #  Graph Loader
#
# def load_merchant_graph():
#     """
#     Downloads Neo4j dump file from S3 and provides instructions to restore it manually.
#     Returns a py2neo Graph connection.
#     """
#     parsed = urlparse(INPUT_GRAPH_URL)
#
#     if parsed.scheme == "s3":
#         bucket = parsed.netloc
#         key = parsed.path.lstrip("/")
#         s3 = boto3.client("s3")
#         obj = s3.get_object(Bucket=bucket, Key=key)
#         dump_path = tempfile.NamedTemporaryFile(delete=False, suffix=".dump").name
#         with open(dump_path, "wb") as f:
#             f.write(obj["Body"].read())
#     else:
#         raise ValueError("Only s3:// paths are supported for graph loading.")
#
#     print(f"Graph dump downloaded to {dump_path}.")
#     print("To restore it, run the following command in your Neo4j server:")
#     print(f"neo4j-admin load --from={dump_path} --database=neo4j --force")
#
#     # Connect to Neo4j after restoration
#     graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
#     return graph

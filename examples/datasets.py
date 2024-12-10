from cozepy import Coze, TokenAuth

coze = Coze(base_url="https://api.coze.cn", auth=TokenAuth(token="xxx"))

datasets = coze.knowledge.documents.list

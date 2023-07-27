# import json
# import pandas as pd
# from celery import shared_task
#
# @shared_task
# def read_excel_to_json(filename):
#     df = pd.read_excel(filename)
#     json_data = df.to_json(orient='records')
#     return json_data
#
# def process_excel(request):
#     # Faça o upload do arquivo e salve-o em algum lugar temporário no servidor.
#     filename = "/path/to/uploaded/file.xlsx"
#
#     # Chame a task para ler o arquivo Excel e transformá-lo em JSON
#     json_data = read_excel_to_json.delay(filename).get()
#
#     # Chame a task para salvar o JSON no banco de dados
#     # save_json_to_db.delay(json_data)
#
#     return HttpResponse("Arquivo Excel processado com sucesso.")
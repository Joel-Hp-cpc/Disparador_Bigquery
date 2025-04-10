# Copyright 2021 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START eventarc_gcs_server]
import os
import json
from flask import Flask, request
from google.cloud import bigquery

app = Flask(__name__)

# [END eventarc_gcs_server]

# [START eventarc_gcs_handler]
@app.route('/', methods=['POST'])
def index():
    print('Llegó una solicitud POST')

    # Obtiene el contenido JSON de la solicitud
    content = request.json

    if not content:
        print("Error: No se recibió un JSON válido")
        return "Bad Request", 400  # Código 400 para solicitud incorrecta

    try:
        ds = content['resource']['labels']['dataset_id']
        proj = content['resource']['labels']['project_id']
        tbl = content['protoPayload']['resourceName']
        rows = int(content['protoPayload']['metadata']['tableDataChange']['insertedRowsCount'])

        if ds == 'cloud_run_tmp' and tbl.endswith('tables/cloud_run_trigger') and rows > 0:
            query = create_agg()
            return "Table created", 200

    except KeyError as e:
        print(f"Error de clave en JSON: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

    return "ok", 200

# [END eventarc_gcs_handler]

def create_agg():
    print('Llegó a la función create_agg')
    client = bigquery.Client()
    query = """
    CREATE OR REPLACE TABLE cloud_run_tmp.created_by_trigger AS
    SELECT 
      name, SUM(number) AS n
    FROM cloud_run_tmp.cloud_run_trigger
    GROUP BY name
    ORDER BY n DESC
    LIMIT 10
    """
    client.query(query)
    return query

# [START eventarc_gcs_server]
if __name__ == "__main__":
    print('Iniciando aplicación Flask...')
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
# [END eventarc_gcs_server]

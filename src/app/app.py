from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
@app.route('/<cargo>')
def index(cargo=None):
    # Lendo o arquivo CSV usando pandas
    df = pd.read_csv("deu_certo.csv")
    # Filtrando apenas as colunas desejadas
    df = df[['TITULO', 'DATA', 'EMPRESA', 'LOCAL', 'Cargo', 'Remoto', 'Resumo', 'Senioridade', 'LINK']]
   
    if cargo:
        mapping = {
            "1": 1,
            "2": 2,
            "3": 3
        }
        df = df[df['Cargo'] == mapping.get(cargo)]
    
    jobs = df.to_dict('records')
    return render_template('index.html', jobs=jobs)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=5001)
    

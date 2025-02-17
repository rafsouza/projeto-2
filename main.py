from lojacoletivo import app


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80, debug=False) # Funciona no AWS
    app.run(debug=True) # Funciona no VSCode
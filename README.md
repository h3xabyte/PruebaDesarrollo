# Prueba De Desarrollo - Julián Felipe Ramírez 😎
[![Flask](https://buttercms.com/static/images/tech_banners/Flask.png)](https://flask.palletsprojects.com/en/1.1.x/)
# Get started

En este documento se hara explicito el uso de el REST API python, utilizando el framework FLASK para las funcionalidades de la prueba de desarrollo.

La aplicacion entera la podemos encontrar en el archivo `app.py`.
Dentro de el directorio ./ podemos encontrar:

`quick.db` Contiene la base de datos sqlite3 lista para su uso.

`uploadcl.csv` Plantilla CSV que se tiene que enviar para crear usuarios.



## Instalacion

    pip install -r requirements


## Modificar Path de la base de datos (Se encuentra en la linea 14)

    'sqlite:///C:\Users\HP\Desktop\qck\quick.db'


## Correr el app (Windows) 'se referencia a py.exe' (No utilice un venv)

    py -3 app.py/python3 app.py







# REST API
----------------------------------------------------------------------------------------------
## Registro de Usuario:

### Request
`POST /register`

     curl -i -H 'Accept: application/json' -d 'name:nombre&password:pass' http://localhost:5000/register

{
     "name":"julian",
     "password":"julian123"

}
### Respuesta

    HTTP/1.1 200 OK
    Date: Wed, 10 FEB 2020 12:36:30 GMT
    Status: 200 OK
    Connection: close
    Content-Type: application/json
    Content-Length: 36

    {"Message":""Signup Succesfully""}
----------------------------------------------------------------------------------------------
## Login:

### Request
`POST /login`


[![Flask](https://i.ibb.co/Rh6jttz/userlogin-1-840x228.webp)](https://flask.palletsprojects.com/en/1.1.x/)

### Respuesta

    HTTP/1.1 200 OK
    Date: Wed, 10 FEB 2020 12:36:30 GMT
    Status: 200 OK
    Connection: close
    Content-Type: application/json
    Content-Length: 36

    {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiIxODM5ZDg4MC1jYzAwLTRiZWEtODhkYS0yNDI2NTU1MDE5OGIiLCJleHAiOjE2MTI5Njk3NTh9.R4ZyXhrgzl7CKS7y0OK47FcH8BWGIXfMEYrv6CaFfAs"}

----------------------------------------------------------------------------------------------
## Uso de el token:




[![Flask](https://i.ibb.co/jhMNCKp/TOKEN.png)](https://flask.palletsprojects.com/en/1.1.x/)

simplemente  se envia por headers x-access-tokens,  si no es valido retornara el error de werkzeug, no le puse excepcion para controlar mas facilmente si el token expiro o no es valido

----------------------------------------------------------------------------------------------
## Subida de archivo:




[![Flask](https://i.ibb.co/hCCRSvg/csv.png)](https://flask.palletsprojects.com/en/1.1.x/)



----------------------------------------------------------------------------------------------
## Gracias!

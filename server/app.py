from . import app, db
from flask import request, make_response, render_template, url_for
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import select
import random








@app.route("/")
def index():
    return render_template("index.html")

# @app.route("/login2")
# def login2():
#     return render_template('login.html')

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    dni = data.get("dni")

    #mando el dni, recibo un token como resultado. si el dni xiste en la bd, lo llevo a la pagina, si no existe lo llevo a insertar los datos. ambos con el token

    if not dni:
        return make_response(
            "Escribí tu DNI",
            401
        )

    cliente = Cliente.query.filter_by(cuil = dni).first()

    if cliente:
        token = jwt.encode({
            'id': cliente.id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        },
        "secret",
        "HS256"
        )
        return make_response({'token': token}, 201)

    if not cliente:
        return make_response(
            "Llevo a escribir sus datos",
            200
        )
    
    return make_response("No se pudo ingresar", 500)


def token_required(t):
    @wraps(t)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
             return make_response({"message":"Token is missing"}, 401)

        try:
            data = jwt.decode(token, "secret", algorithms=["HS256"])
            current_cliente = Cliente.query.filter_by(id=data["id"]).first()
            print(current_cliente)
        except Exception as ex:
            print(ex)
            return make_response({
                "message": "Token is invalid"},
                401
            )
        return t(current_cliente, *args, **kwargs)
    return decorated

@app.route("/api/cliente", methods=["GET"])
@token_required
def getCliente(current_cliente):
    cuenta_id = buscarCuentaId(current_cliente)
    cuenta = Cuenta.query.filter_by(id=cuenta_id).first()
    rol = db.session.query(ClienteXCuenta.rol).join(Cliente).filter(Cliente.id == current_cliente.id).first()
    tipoCuenta = db.session.query(TipoCuenta.nombre).join(Cuenta).filter(Cuenta.id == cuenta.id).first()
    direccion = db.session.query(Direccion).join(Cliente).filter(Cliente.id == current_cliente.id).first()
    localidad = Localidad.query.filter_by(id=direccion.localidad_id).first()
    provincia = Provincia.query.filter_by(id=localidad.provincia_id).first()
    print(localidad)
    #Enviar JSON con los datos de la Cuenta y del Cliente
    print(rol)
    print(tipoCuenta)
    return make_response(
        {"data":
        {
            "cliente": {
                "id": current_cliente.id,
                "nombre": current_cliente.nombre,
                "cuil":current_cliente.cuil,
                "alta":current_cliente.alta
            },
            "cuenta": {
                "id": cuenta.id,
                "numeroCuenta": cuenta.numeroCuenta,
                "saldo": cuenta.saldo,
                "alta": cuenta.alta,
                "rol": rol[0],
                "tipoCuenta": tipoCuenta[0]
            },     
            "direccion": {
                "calle": direccion.calle,
                "numero": direccion.numero,
                "departamento": direccion.departamento,
                "localidad": localidad.nombre,
                "provincia": provincia.nombre
            }
            
        }}
    )

@app.route("/api/store", methods=["POST"])
# @token_required
def store():
    data = request.json

    _dni = data.get("dni")
    _nombre = data.get("nombre")

    _provincia = data.get("provincia")
    _localidad = data.get("localidad")
    _calle = data.get("calle")
    _numero = data.get("numero")
    _departamento = data.get("departamento")

    if not _dni or not _nombre or not _provincia or not _calle or not _numero:
        return make_response(
            "Complete los datos",
            401
        )


    provincia = Provincia(
        nombre = _provincia
    )
    db.session.add(provincia)
    db.session.commit()

    localidad = Localidad (
        nombre = _localidad,
        provincia_id = provincia.id
    )
    db.session.add(localidad)
    db.session.commit()


    direccion = Direccion (
        calle = _calle,
        numero = _numero,
        departamento = _departamento,
        localidad_id = localidad.id
    )
    db.session.add(direccion)
    db.session.commit()


    cliente = Cliente(
        cuil = _dni,
        nombre = _nombre,
        alta = datetime.now(),
        direccion_id = direccion.id
    )
    db.session.add(cliente)
    db.session.commit()


    cuenta = Cuenta(
        numeroCuenta = 88888888,
        saldo = 8888.88,
        alta = datetime.now(),
        banco_id = 1,
        tipoCuenta_id = 1
    )
    db.session.add(cuenta)
    db.session.commit()

    clienteXCuenta = ClienteXCuenta(
        rol = "principal",
        cliente_id = cliente.id,
        cuenta_id = cuenta.id
    )
    db.session.add(clienteXCuenta)
    db.session.commit()

    return make_response("Cliente Creado", 200)


@app.route("/api/transferencia", methods=["POST"])
@token_required
def transferencia(current_cliente):
    data = request.json
    _monto = data.get("monto")
    _cuentaDestino = buscarNumeroCuenta(data.get("cuentaDestino"))

    if not _monto or not _cuentaDestino:
        return make_response(
            "Escribe los valores",
            500
        )

    _cuentaOrigen = buscarCuentaId(current_cliente)
    cuenta = Cuenta.query.filter_by(id = _cuentaOrigen).first()
    
    if cuenta.saldo < _monto:
        return make_response(
            "No se puede",
            401
        )

    transaccion = Transaccion(
        monto = _monto,
        numeroOperacion = 88888888,
        fecha = datetime.now(),
        cuentaOrigen_id = _cuentaOrigen,
        cuentaDestino_id = _cuentaDestino,
        tipoTransaccion_id = 1
    )
    db.session.add(transaccion)
    db.session.commit()

    cuentaOrigen = Cuenta.query.filter_by(id = _cuentaOrigen).first()
    cuentaOrigen.saldo = cuentaOrigen.saldo - _monto
    db.session.commit()

    cuentaDestino = Cuenta.query.filter_by(id = _cuentaDestino).first()
    cuentaDestino.saldo = cuentaDestino.saldo + _monto
    db.session.commit()

    return make_response("Transacción realizada", 200)


@app.route("/api/movimientos", methods=["GET"])
@token_required
def movimientos(current_cliente):

    cuenta_id = buscarCuentaId(current_cliente)

    movimientos = Transaccion.query.filter_by(cuentaOrigen_id=cuenta_id).all()
    return make_response(
        {"data":[row.serialize for row in movimientos]}
    )


def buscarCuentaId(cliente):
    cuenta_id = db.session.query(ClienteXCuenta.cuenta_id).join(Cliente).filter(Cliente.id == cliente.id).first()
    return cuenta_id[0]

def buscarNumeroCuenta(cuenta):
    
    cuenta = Cuenta.query.filter_by(numeroCuenta = cuenta).first()

    return cuenta.id

if __name__ == '__main__':
    app.debug = True
    app.run()
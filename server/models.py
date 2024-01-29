from . import db
from sqlalchemy.sql import func

class Banco(db.Model):
    __tablename__ = "Banco"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100))
    cuentas = db.relationship('Cuenta', backref="Banco")



class Direccion(db.Model):
    __tablename__ = "Direccion"
    id = db.Column(db.Integer, primary_key = True)
    calle = db.Column(db.String(100))
    departamento = db.Column(db.String(50))
    numero = db.Column(db.Integer)
    localidad_id= db.Column(db.Integer, db.ForeignKey("Localidad.id"))
    clientes = db.relationship('Cliente', backref="Direccion")

class Localidad(db.Model):
    __tablename__ = "Localidad"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100))
    provincia_id= db.Column(db.Integer, db.ForeignKey("Provincia.id"))
    direcciones = db.relationship('Direccion', backref="Localidad")


class Provincia(db.Model):
    __tablename__ = "Provincia"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100))
    localidades = db.relationship('Localidad', backref="Provincia")



class Cliente(db.Model):
    __tablename__ = "Cliente"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100))
    cuil = db.Column(db.Integer)
    alta = db.Column(db.DateTime(timezone=True), server_default=func.now())
    direccion_id = db.Column(db.Integer, db.ForeignKey("Direccion.id"))
    clientesCuentas = db.relationship('ClienteXCuenta', backref="Cliente")

class ClienteXCuenta(db.Model):
    __tablename__= "ClienteXCuenta"
    id = db.Column(db.Integer, primary_key = True)
    rol = db.Column(db.String(100))
    cliente_id = db.Column(db.Integer, db.ForeignKey("Cliente.id"))
    cuenta_id = db.Column(db.Integer, db.ForeignKey("Cuenta.id"))

class Cuenta(db.Model):
    __tablename__ = "Cuenta"
    id = db.Column(db.Integer, primary_key = True)
    numeroCuenta = db.Column(db.Integer)
    saldo = db.Column(db.Float)
    alta = db.Column(db.DateTime(timezone=True), server_default=func.now())
    clientesCuentas = db.relationship('ClienteXCuenta', backref="Cuenta")
    banco_id = db.Column(db.Integer, db.ForeignKey("Banco.id"))
    tipoCuenta_id = db.Column(db.Integer, db.ForeignKey("TipoCuenta.id"))
    # transacciones = db.relationship('Transaccion', backref="Cuenta")
    # transaccionesOrigen = db.relationship('Transaccion', backref="Cuenta")
    # transaccioneDestino = db.relationship('Transaccion', backref="Cuenta")


class TipoCuenta(db.Model):
    __tablename__ = "TipoCuenta"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100))



class Transaccion(db.Model):
    __tablename__ = "Transaccion"
    id = db.Column(db.Integer, primary_key = True)
    monto = db.Column(db.Numeric(10,2))
    numeroOperacion = db.Column(db.Integer)
    fecha = db.Column(db.DateTime(timezone=True), server_default=func.now())
    cuentaOrigen_id = db.Column(db.Integer, db.ForeignKey("Cuenta.id"))
    cuentaDestino_id = db.Column(db.Integer, db.ForeignKey("Cuenta.id"))
    tipoTransaccion_id = db.Column(db.Integer, db.ForeignKey("TipoTransaccion.id"))

    @property
    def serialize(self):

        
        return{
            "numeroOperacion": self.numeroOperacion,
            "monto": self.monto,
            "fecha": self.fecha
        }

class TipoTransaccion(db.Model):
    __tablename__ = "TipoTransaccion"
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(100))
    transacciones = db.relationship('Transaccion', backref="TipoTransaccion")


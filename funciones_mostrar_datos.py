#Funciones que muestras los datos obtenidos del envío de formularios
def mostrar_datos(formulario):
    print(formulario.nombre.data)
    print(formulario.apellido.data)
    print(formulario.password.data)
    print(formulario.email.data)
def mostrar_datos_crear(formulario_crear):
    print(formulario_crear.titulo.data)
    print(formulario_crear.fechaEven.data)
    print(formulario_crear.hora.data)
    print(formulario_crear.opciones.data)
    print(formulario_crear.imagen.data)
    print(formulario_crear.descripcion.data)
def mostrar_datos_inicio(formulario_ingreso):
    print(formulario_ingreso.email.data)

def mostrar_datos_comentario(formulario_comentario):
    print(formulario_comentario.campocomentario.data)

def mostrar_datos_filtro(filtro):
    print(filtro.opciones.data)

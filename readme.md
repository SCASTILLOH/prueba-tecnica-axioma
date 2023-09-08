## Clone login Banco de Chile test AXIOMA 

crear env
```
python3 -m venv env
```
activar env en mac o linux
```
source env/bin/activate
```
instalar dependencias con pip
```
pip install -r req.txt
```
correr servidor localhost
```
python manage.py runserver
```

administrador: http://127.0.0.1:8000/admin/
login: http://127.0.0.1:8000/login/
home: http://127.0.0.1:8000/

* administrador y usuario deben logearse en navegadores separados

<img src="images_readme/image1.png" alt="image" width="500">

## Funcionalidades:

- Valida credenciales de usuario
- Valida rut chileno
- Solo 3 intentos fallidos luego se bloquea cliente
- Solo administrador puede desbloquear
- Login requerido para acceder a cartola
- Redirige al login si harcodea url un usuario no autorizado
- Cuenta con pagina administrador (django admin)
- El administrador crea cuentas de usuario
- El numero de cuenta se crea por medio de signals
- El administrador crea cargos, abonos, saldos, estado
- El saldo contable y disponible se actualiza segun cargos y abonos, al grabar usuario
- El comportamiento de saldos es real a un banco como retenciones y disponible
- Soporta sobregiro
- Linea de credito no tiene funcionalidad más que crearla 
- El home de usuario tiene logout que redirige al login


## Tecnologías y librerías usadas:

- django
- django-crispy-forms
- sqlite3
- rut-chile
- css + sass
- js
- fontawesome icons

<img src="images_readme/image2.png" alt="image" width="500">
<img src="images_readme/image3.png" alt="image" width="500">
<img src="images_readme/image4.png" alt="image" width="500">
<img src="images_readme/image5.png" alt="image" width="500">
<img src="images_readme/image6.png" alt="image" width="500">
<img src="images_readme/image7.png" alt="image" width="500">
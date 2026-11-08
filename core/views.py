from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Comercio, Categoria,Resena
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.text import slugify
import uuid




def inicio(request):
    return render(request, 'inicio.html')


def busqueda(request):
    query = request.GET.get('q', '')
    categoria_slug = request.GET.get('categoria', '')

    comercios = Comercio.objects.filter(estado='activo')

    if query:
        comercios = comercios.filter(nombre__icontains=query)

    if categoria_slug:
        comercios = comercios.filter(categoria__slug=categoria_slug)

    comercios = comercios.order_by('-destacado', '-total_visualizaciones')
    categorias = Categoria.objects.filter(activa=True)

    return render(request, 'busqueda.html', {
        'comercios': comercios,
        'categorias': categorias,
        'query': query,
        'categoria_slug': categoria_slug,
    })


def perfil_comercio(request, slug):
    comercio = get_object_or_404(Comercio, slug=slug, estado='activo')

    Comercio.objects.filter(pk=comercio.pk).update(
        total_visualizaciones=comercio.total_visualizaciones + 1
    )

    resenas = comercio.resenas.filter(aprobada=True).order_by('-creado_en')
    comercios_relacionados = Comercio.objects.filter(
        categoria=comercio.categoria,
        estado='activo'
    ).exclude(pk=comercio.pk)[:3]

    return render(request, 'perfil_comercio.html', {
        'comercio': comercio,
        'resenas': resenas,
        'comercios_relacionados': comercios_relacionados,
    })


def registro(request):
    if request.user.is_authenticated:
        return redirect('busqueda')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password1:
            messages.error(request, 'Todos los campos son obligatorios.')
        elif password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif len(password1) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya está en uso.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Ese correo ya está registrado.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            login(request, user)
            messages.success(request, f'¡Bienvenido a WherIA, {username}!')
            return redirect('busqueda')

    return render(request, 'registro.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('busqueda')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'busqueda')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('inicio')



@login_required(login_url='/login/')
def panel_dashboard(request):
    comercios = Comercio.objects.filter(propietario=request.user)
    
    # Tomar el primer comercio del usuario para el contexto
    comercio = comercios.first()
    
    resenas = []
    if comercio:
        resenas = comercio.resenas.filter(aprobada=True).order_by('-creado_en')[:3]

    return render(request, 'panel/dashboard.html', {
        'comercios': comercios,
        'comercio': comercio,
        'resenas': resenas,
    })

@login_required(login_url='/login/')
def panel_editar(request, slug):
    comercio = get_object_or_404(
        Comercio,
        slug=slug,
        propietario=request.user
    )

    if request.method == 'POST':
        comercio.nombre = request.POST.get('nombre', comercio.nombre)
        comercio.descripcion = request.POST.get('descripcion', comercio.descripcion)
        comercio.telefono = request.POST.get('telefono', comercio.telefono)
        comercio.whatsapp = request.POST.get('whatsapp', comercio.whatsapp)
        comercio.email = request.POST.get('email', comercio.email)
        comercio.sitio_web = request.POST.get('sitio_web', comercio.sitio_web)
        comercio.direccion = request.POST.get('direccion', comercio.direccion)
        comercio.ciudad = request.POST.get('ciudad', comercio.ciudad)
        comercio.dias_atencion = request.POST.get('dias_atencion', comercio.dias_atencion)

        horario_apertura = request.POST.get('horario_apertura')
        horario_cierre = request.POST.get('horario_cierre')
        if horario_apertura:
            comercio.horario_apertura = horario_apertura
        if horario_cierre:
            comercio.horario_cierre = horario_cierre

        comercio.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('panel_dashboard')

    return render(request, 'panel/editar.html', {
        'comercio': comercio,
    })



@login_required(login_url='/login/')
def dejar_resena(request, slug):
    comercio = get_object_or_404(Comercio, slug=slug, estado='activo')

    if request.method == 'POST':
        calificacion = request.POST.get('calificacion')
        comentario = request.POST.get('comentario', '').strip()

        # Validar que no haya reseñado antes
        if Resena.objects.filter(comercio=comercio, autor=request.user).exists():
            messages.error(request, 'Ya dejaste una reseña para este comercio.')
            return redirect('perfil_comercio', slug=slug)

        # Validar calificación
        if not calificacion or not calificacion.isdigit():
            messages.error(request, 'Selecciona una calificación válida.')
            return redirect('perfil_comercio', slug=slug)

        calificacion = int(calificacion)
        if calificacion < 1 or calificacion > 5:
            messages.error(request, 'La calificación debe ser entre 1 y 5.')
            return redirect('perfil_comercio', slug=slug)

        Resena.objects.create(
            comercio=comercio,
            autor=request.user,
            calificacion=calificacion,
            comentario=comentario,
            aprobada=True
        )

        messages.success(request, '¡Gracias por tu reseña!')
        return redirect('perfil_comercio', slug=slug)

    return redirect('perfil_comercio', slug=slug)


@login_required(login_url='/login/')
def responder_resena(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id)

    # Verificar que el comerciante es dueño del comercio
    if resena.comercio.propietario != request.user:
        messages.error(request, 'No tienes permiso para responder esta reseña.')
        return redirect('panel_dashboard')

    if request.method == 'POST':
        respuesta = request.POST.get('respuesta', '').strip()
        if respuesta:
            resena.respuesta = respuesta
            resena.save()
            messages.success(request, 'Respuesta publicada correctamente.')
        return redirect('panel_dashboard')

    return redirect('panel_dashboard')



@login_required(login_url='/login/')
def panel_crear_comercio(request):
    categorias = Categoria.objects.filter(activa=True)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        categoria_id = request.POST.get('categoria')
        telefono = request.POST.get('telefono', '').strip()
        whatsapp = request.POST.get('whatsapp', '').strip()
        email = request.POST.get('email', '').strip()
        sitio_web = request.POST.get('sitio_web', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()
        dias_atencion = request.POST.get('dias_atencion', '').strip()
        horario_apertura = request.POST.get('horario_apertura', '')
        horario_cierre = request.POST.get('horario_cierre', '')
        latitud = request.POST.get('latitud', '')
        longitud = request.POST.get('longitud', '')

        # Validaciones básicas
        if not nombre:
            messages.error(request, 'El nombre del negocio es obligatorio.')
            return render(request, 'panel/crear_comercio.html', {'categorias': categorias})

        if not categoria_id:
            messages.error(request, 'Selecciona una categoría.')
            return render(request, 'panel/crear_comercio.html', {'categorias': categorias})

        if not direccion or not ciudad:
            messages.error(request, 'La dirección y ciudad son obligatorias.')
            return render(request, 'panel/crear_comercio.html', {'categorias': categorias})

        # Generar slug único
        base_slug = slugify(nombre)
        slug = base_slug
        counter = 1
        while Comercio.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1

        try:
            categoria = Categoria.objects.get(id=categoria_id)
        except Categoria.DoesNotExist:
            messages.error(request, 'Categoría no válida.')
            return render(request, 'panel/crear_comercio.html', {'categorias': categorias})

        comercio = Comercio(
            propietario=request.user,
            nombre=nombre,
            slug=slug,
            descripcion=descripcion,
            categoria=categoria,
            telefono=telefono,
            whatsapp=whatsapp,
            email=email,
            sitio_web=sitio_web,
            direccion=direccion,
            ciudad=ciudad,
            dias_atencion=dias_atencion,
            estado='pendiente',
            plan='basico',
        )

        if latitud:
            try:
                comercio.latitud = float(latitud)
            except ValueError:
                pass

        if longitud:
            try:
                comercio.longitud = float(longitud)
            except ValueError:
                pass

        if horario_apertura:
            comercio.horario_apertura = horario_apertura

        if horario_cierre:
            comercio.horario_cierre = horario_cierre

        comercio.save()

        messages.success(request, f'¡Negocio "{nombre}" registrado! Está pendiente de verificación.')
        return redirect('panel_dashboard')

    return render(request, 'panel/crear_comercio.html', {
        'categorias': categorias,
    })
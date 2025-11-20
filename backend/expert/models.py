from django.db import models


class Pregunta(models.Model):
    TIPO_BOOL = "bool"
    TIPO_SELECT = "select"
    TIPO_NUMBER = "number"

    TIPOS = [
        (TIPO_BOOL, "Sí / No"),
        (TIPO_SELECT, "Selección"),
        (TIPO_NUMBER, "Numérico"),
    ]

    texto = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default=TIPO_BOOL)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.id}] {self.texto[:50]}..."


class OpcionRespuesta(models.Model):
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="opciones"
    )
    etiqueta = models.CharField(max_length=100)  # Ej: "Sí", "No", "Débil"
    valor = models.CharField(max_length=100)     # Valor normalizado

    def __str__(self):
        return f"{self.pregunta_id} - {self.etiqueta} ({self.valor})"


class Diagnostico(models.Model):
    nombre = models.CharField(max_length=50)  # Ej: ALTO, MEDIO, BAJO
    recomendaciones = models.TextField()

    def __str__(self):
        return self.nombre


class Regla(models.Model):
    nombre = models.CharField(max_length=100)
    peso = models.IntegerField(default=10)
    diagnostico = models.ForeignKey(
        Diagnostico,
        on_delete=models.CASCADE,
        related_name="reglas"
    )
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} (peso={self.peso}, dx={self.diagnostico})"


class ReglaCondicion(models.Model):
    OPERADOR_IGUAL = "="
    OPERADOR_DISTINTO = "!="
    OPERADOR_MAYOR_IGUAL = ">="
    OPERADOR_MENOR_IGUAL = "<="
    OPERADOR_IN = "IN"

    OPERADORES = [
        (OPERADOR_IGUAL, "="),
        (OPERADOR_DISTINTO, "!="),
        (OPERADOR_MAYOR_IGUAL, ">="),
        (OPERADOR_MENOR_IGUAL, "<="),
        (OPERADOR_IN, "IN"),
    ]

    regla = models.ForeignKey(
        Regla,
        on_delete=models.CASCADE,
        related_name="condiciones"
    )
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="condiciones"
    )
    operador = models.CharField(max_length=5, choices=OPERADORES, default=OPERADOR_IGUAL)
    valor = models.CharField(max_length=100)

    def __str__(self):
        return f"Regla {self.regla_id} - Preg {self.pregunta_id} {self.operador} {self.valor}"


class Evaluacion(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    riesgo_final = models.CharField(max_length=50)
    puntaje_total = models.IntegerField()
    detalle = models.TextField(blank=True)  # Podemos guardar JSON como texto

    def __str__(self):
        return f"Eval {self.id} - {self.riesgo_final} ({self.fecha})"


class Respuesta(models.Model):
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name="respuestas"
    )
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name="respuestas"
    )
    valor = models.CharField(max_length=100)

    def __str__(self):
        return f"Eval {self.evaluacion_id} - Preg {self.pregunta_id} = {self.valor}"

